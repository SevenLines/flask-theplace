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
from application.helpers import get_categories, get_images, get_image_path, is_local, sources, SourceExtractor, \
    get_or_create, get_albums
from application.models import db, Category, Source, Album
from helpers import open_url_ex, get_custom_album


@app.route('/categories/update')
def update():
    if is_local():
        if request.headers.get('accept') == 'text/event-stream':

            source = request.args.get("source")
            if source is None:
                _sources = sources
            else:
                _sources = [source, ]

            def get():
                for source_name in _sources:
                    # Source.query.filter(Source.name == source_name).delete()
                    sq = db.session.query(Source.id).filter(Source.name == source_name).subquery()
                    Album.query.filter(Album.source_id.in_(sq)).delete(synchronize_session='fetch')
                    Source.query.filter(Source.name == source_name).delete()
                    db.session.commit()
                    for category in get_categories(source_name):
                        dbCategory = get_or_create(db.session, Category, name=category['name'])
                        db.session.flush()
                        src = Source(
                            name=source_name,
                            local_id=category['local_id'],
                            local_url=category['local_url'],
                            category_id=dbCategory.id
                        )
                        db.session.add(src)
                        db.session.flush()
                        for album in category['albums']:
                            album = Album(
                                album_id=album['album_id'],
                                name=album.get('name', ''),
                                local_url=album['local_url'],
                                source_id=src.id,
                            )
                            db.session.add(album)
                            db.session.flush()
                        status = "%s (%s)" % (category['name'], source_name)
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
        if re.search(sources[sn].root, url):
            source_name = sn
            break

    if not source_name:
        flask.abort(404)

    album = Album.query.join(Source)\
        .filter(and_(Source.name == source_name, or_(Album.album_id==id_, Album.local_url == url)))\
        .first()
    if album:
        name = album.source.category.name
    else:
        album_info = get_custom_album(url)
        if album_info and 'name' in album_info:
            name = album_info['name']
        else:
            name = ''

    _images = get_images(source_name, url, name)
    # if request.is_xhr:
    return jsonify(data=_images, name=name, is_local=is_local(), source=source_name)


@app.route('/download', methods=["POST", ])
def download():
    if is_local():
        url = request.form.get('url')
        name = request.form.get('name', '_')
        source = request.form.get('source', '')

        src, filename = SourceExtractor.get_src(url, name, source)
        ext = src.split('.')[-1]
        if len(ext) > 4:
            ext = "jpg"


        r = open_url_ex(src)

        if not filename.endswith(ext):
            filename = "%s.%s" % (filename, ext)


        # if not re.search('image/.*', r.headers['content-type']):
        #     what = imghdr.what(None, r.content)
        #     if not what:
        #         flask.abort(406)

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

    album_info = get_custom_album(query)
    if album_info:
        return jsonify(items=[album_info, ])

    categories = Category.query.filter(Category.name.like(u"%{query}%".format(query=query)))

    # if we have sources without albums we will try to load albums
    for category in categories.with_lockmode('read')[:5]:
        for source in category.sources:
            if source.albums.count() == 0:
                for album in get_albums(source.name, source.local_url):
                    album = Album(
                        album_id=album['album_id'],
                        name=album.get('name', ''),
                        local_url=album['local_url'],
                        source_id=source.id,
                    )
                    db.session.add(album)
    db.session.commit()

    items = list([c.serialize() for c in categories])
    return jsonify(items=items)


@app.route('/')
def index():
    if is_local():
        upgrade()
        if not Category.query.count():
            return redirect(url_for("update", force_update=True))
    return render_template("theplace/index.html")