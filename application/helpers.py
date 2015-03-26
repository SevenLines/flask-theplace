import os
from urllib2 import urlopen
from urlparse import urljoin
from lxml import html
import re
from werkzeug.utils import secure_filename
from application import app
from application.models import Category

__author__ = 'm'

urls = {
    "theplace": {
        "root": "http://www.theplace.ru/",
        "photos": "http://www.theplace.ru/photos/",
        "paths": [
            "http://www.theplace.ru/photos/?s_id=0",
            "http://www.theplace.ru/photos/?s_id=1",
            "http://www.theplace.ru/photos/?s_id=2",
            "http://www.theplace.ru/photos/?s_id=3",
        ],
    }
}


def get_image_path(url, category_name):
    filename = url.split("/")[-1]
    return os.path.join(app.config['SAVE_PATH'], category_name, filename)


def get_categories(data, source):
    root = html.fromstring(data)
    out = [{"name": item.text,
            "href": urljoin(urls["theplace"]['photos'], item.get("href")),
            "local_id": re.search(r"mid(\d+)\.html", item.get("href")).group(1)
            }
           for item in root.xpath('//table[@id="models_list"]//a')]

    return out


def get_items(data, source):
    root = html.fromstring(data)
    gallery = root.find_class('gallery-pics-list')
    if len(gallery):
        gallery = gallery[-1]
    else:
        return []

    images = gallery.cssselect("a img")
    listalka = root.cssselect(".listalka.ltop a")
    id = -1
    pages = 0
    if len(listalka):
        href = listalka[-1].get('href')
        regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
        m = regexp.search(href)
        if m:
            id = int(m.group(1))
            pages = int(m.group(2))

    regexp = re.compile(r"(.*?)_s(\.\w+)")
    category = Category.query.filter(Category.local_id == id).first()

    images_out = []
    for img in images:
        src = regexp.sub(r'\1\2', img.get('src'))
        images_out.append({"thumbnail": urljoin(urls["theplace"]['root'], img.get('src')),
                           "src": urljoin(urls["theplace"]['root'], src),
                           "exists": os.path.exists(get_image_path(src, category.name)) if category else False,
                           })

    return {
        'images': images_out,
        'id': id,
        'pages': [urljoin(urls["theplace"]['root'], "/photos/gallery.php?id=%d&page=%d") % (id, i) for i in
                  xrange(1, pages + 1)],
    }