import json
import os
from urllib2 import urlopen
import urllib2
from flask import render_template, request, redirect, jsonify
import flask
from application.app_settings import app
from application.helpers import get_categories, get_items, urls, get_image_path
from application.models import db, Category

db.init_app(app)


@app.route('/categories/update')
def update():
    if request.is_xhr:
        Category.query.delete()

        source = request.args.get('source', "theplace")

        for root in urls[source]['paths']:
            r = urlopen(root)
            categories = get_categories(r.read().decode("windows-1251"), source)
            for category in categories:
                db.session.add(Category(name=category['name'],
                                        local_url=category['href'],
                                        local_id=category['local_id']))

        db.session.commit()
        return "ok"
    else:
        return render_template("theplace/update.html")


@app.route('/items/images')
def images():
    url = request.args.get('url')
    page = request.args.get('page')
    r = urlopen(url)
    images = get_items(r.read().decode("windows-1251"), "theplace")
    category = Category.query.filter(Category.local_url == url).first()
    if request.is_xhr:
        return jsonify(data=images, name=category.name if category else '')


@app.route('/download', methods=["POST", ])
def download():
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

@app.route('/remove', methods=["POST", ])
def remove():
    url = request.form.get('url')
    name = request.form.get('name', '_')
    filename = get_image_path(url, name)
    if os.path.exists(filename):
        os.remove(filename)
        return ""
    else:
        flask.abort(404)


@app.route('/categories/query')
def query_categories():
    query = request.args.get('query')
    categories = Category.query.filter(Category.name.like(u"%{query}%".format(query=query)))
    return jsonify(items=list([c.serialize() for c in categories]))


@app.route('/')
def index():
    categories = Category.query
    return render_template("theplace/index.html", **{
        'categories': json.dumps(list([c.serialize() for c in categories]))
    })