import os
from urllib2 import urlopen
import urllib2
from flask import render_template, request, redirect, jsonify, url_for
import flask
from flask.ext.migrate import upgrade
from application.app_settings import app
from application.helpers import get_albums, get_images, get_image_path, is_local, sources
from application.models import db, Category

db.init_app(app)


@app.route('/categories/update')
def update():
    if is_local():
        if request.is_xhr:
            Category.query.delete()
            for source_name in sources:
                for category in get_albums(source_name):
                    db.session.add(Category(name=category['name'],
                                            local_url=category['href'],
                                            local_id=category['local_id']))
                db.session.commit()
            return "ok"
        else:
            return render_template("theplace/update.html")
    else:
        return redirect(url_for("index"))


@app.route('/items/images')
def images():
    url = request.args.get('url')
    id_ = request.args.get('id')
    category = Category.query.filter(Category.local_id == id_).first()
    name = category.name if category else ''
    _images = get_images("theplace", url, name)
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