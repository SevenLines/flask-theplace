import glob
import imghdr
import os
import re
from urllib2 import urlopen
import urllib2
import time

from flask import render_template, request, redirect, jsonify, url_for
import flask
from flask.ext.migrate import upgrade
from sqlalchemy import or_, and_
from werkzeug.wrappers import Response

from application.app_settings import app
from application.helpers import get_albums, get_images, get_image_path, is_local, sources, SourceExtractor
from application.models import db, Category
from helpers import open_url_ex


@app.route('/categories/update')
def update():
    if is_local():
        if request.headers.get('accept') == 'text/event-stream':

            # select source
            source = request.args.get("source")
            if source is None:
                _sources = sources
            else:
                _sources = [source, ]

            def get():
                for source_name in _sources:
                    Category.query.filter(Category.source_name == source_name).delete()
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

            out = get()
            return Response(out, mimetype="text/event-stream")
        else:
            force_update = request.args.get('force_update', False)
            return render_template("theplace/update.html", sources=sources, force_update=force_update)
    else:
        return redirect(url_for("index"))


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
        return jsonify(data=_images, name=name, is_local=is_local(), source=source_name)


@app.route('/download', methods=["POST", ])
def download():
    if is_local():
        url = request.form.get('url')
        name = request.form.get('name', '_')
        source = request.form.get('source', '')

        src, filename = SourceExtractor.get_src(url, name, source)
        ext = src.split('.')[-1]
        if not filename.endswith(ext):
            filename = "%s.%s" % (filename, ext)

        r = open_url_ex(src)

        # what = imghdr.what(None, r.content)
        # print "%s: %s" % (what if what else '!none', url)
        # if not what:
        if not re.search('image/.*', r.headers['content-type']):
            flask.abort(406)

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, mode='wb') as f:
            f.write(r.content)
        return filename
    else:
        return flask.abort(405)


@app.route('/remove', methods=["POST", ])
def remove():
    if is_local():
        url = request.form.get('url')
        name = request.form.get('name', '_')
        source = request.form.get('source', '')
        filename = SourceExtractor.get_path(url, name, source)
        files = glob.glob("%s*" % filename)
        if len(files) == 1:
            os.remove(files[0])
            return ""
        else:
            flask.abort(404)
    else:
        return flask.abort(405)


@app.route('/image-src')
def image_src():
    url = request.args.get('url')
    src = SourceExtractor.get_src(url, "_", 'source')
    return src[0]


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
            return redirect(url_for("update", force_update=True))
    return render_template("theplace/index.html")