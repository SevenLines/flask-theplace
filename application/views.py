import json
from urllib2 import urlopen
from flask import render_template, request, redirect, jsonify
import flask
from flask.helpers import url_for
from application import app, helpers
from application.helpers import get_categories, get_items
from application.models import db, Category

db.init_app(app)

@app.route('/categories/update')
def update():
    root = request.args.get('root', helpers.urls['list'])
    r = urlopen(root)
    Category.query.delete()
    categories = get_categories(r.read().decode("windows-1251"))
    for category in categories:
        print category
        db.session.add(Category(name=category['name'], local_url=category['href']))
    db.session.commit()
    return redirect(url_for('index'))



@app.route('/items/top')
def images():
    url = request.args.get('url')
    page = request.args.get('page')
    r = urlopen(url)
    images = get_items(r.read().decode("windows-1251"))
    if request.is_xhr:
        return jsonify(data=images)


@app.route('/categories/query')
def query_categories():
    query = request.args.get('query')
    categories = Category.query.filter(Category.name.like("%{query}%".format(query=query)))
    return jsonify(items=list([c.serialize() for c in categories]))


@app.route('/')
def index():
    categories = Category.query
    return render_template("theplace/index.html", **{
        'categories': json.dumps(list([c.serialize() for c in categories]))
    })