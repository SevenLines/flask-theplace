import os
from urllib2 import urlopen
import urllib2
from flask import stream_with_context, render_template, request, redirect, jsonify, url_for
import flask
from flask.ext.migrate import upgrade
from flask.ext.socketio import emit, send
from sqlalchemy import or_, and_
import time
from werkzeug.wrappers import Response
from application.app_settings import app
from application.helpers import get_albums, get_images, get_image_path, is_local, sources
from application.models import db, Category
from socket_settings import socketio


@app.route('/categories/update')
def update():
    if is_local():
        if request.headers.get('accept') == 'text/event-stream':
            def get():
                Category.query.delete()
                for source_name in sources:
                    for category in get_albums(source_name):
                        db.session.add(Category(name=category['name'],
                                                source_name=source_name,
                                                local_url=category['href'],
                                                local_id=category['local_id']))
                        status = "%s (%s)" % (category['name'], source_name)
                        # print status
                        yield "data: %s\n\n" % status
                    db.session.commit()
                yield "data: $done\n\n"
            return Response(get(), mimetype="text/event-stream")
        else:
            return render_template("theplace/update.html")
    else:
        return redirect(url_for("index"))


@app.route('/update_progress')
def update_progress():
    def inner():
        yield "cool"
        time.sleep(2)
        yield "cool2"
    return Response(inner(), mimetype="text")

@app.route('/items/images')
def images():
    url = request.args.get('url')
    id_ = request.args.get('id')

    source_name = ""
    for sn in sources:
        if url.startswith(sources[sn].root):
            source_name = sn
            break

    if not source_name:
        flask.abort(404)

    category = Category.query.filter(
        and_(Category.source_name == source_name,
             or_(Category.local_id == id_, Category.local_url == url)
             )
    ).first()
    name = category.name if category else ''
    _images = get_images(source_name, url, name)
    if request.is_xhr:
        return jsonify(data=_images, name=name, is_local=is_local())


@app.route('/download', methods=["POST", ])
def download():
    if is_local():
        url = request.form.get('url')
        name = request.form.get('name', '_')

        r = urllib2.Request(url, None,
                            headers={'User-Agent': 'I just wanna get some of your pictures. Thanks for your work',
                                     'Referer': 'localhost'})
        r = urlopen(r)

        filename = get_image_path(url, name)

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, mode='wb') as f:
            f.write(r.read())
        return ""
    else:
        return flask.abort(405)


@app.route('/remove', methods=["POST", ])
def remove():
    if is_local():
        url = request.form.get('url')
        name = request.form.get('name', '_')
        filename = get_image_path(url, name)
        if os.path.exists(filename):
            os.remove(filename)
            return ""
        else:
            flask.abort(404)
    else:
        return flask.abort(405)


@app.route('/categories/query')
def query_categories():
    query = request.args.get('query')
    categories = Category.query.filter(Category.name.like(u"%{query}%".format(query=query)))
    return jsonify(items=list([c.serialize() for c in categories]))


@app.route('/')
def index():
    if is_local():
        upgrade()
        if not Category.query.count():
            return redirect(url_for("update"))
    return render_template("theplace/index.html")