from urllib2 import urlopen
from urlparse import urljoin
from lxml import html
import re

__author__ = 'm'

urls = {
    "root": "http://www.theplace.ru/",
    "photos": "http://www.theplace.ru/photos/",
    "list": "http://www.theplace.ru/photos/?s_id=0",
}


def get_categories(data):
    root = html.fromstring(data)
    out = [{"name": item.text,
            "href": urljoin(urls['photos'], item.get("href"))}
           for item in root.xpath('//table[@id="models_list"]//a')]

    return out


def get_items(data):
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

    regexp = re.compile("(.*?)_s(.\w+)")


    return {
        'images': [{"thumbnail": urljoin(urls['root'], img.get('src')),
                    "src": urljoin(urls['root'], regexp.sub(r'\1\2', img.get('src')))} for img in images],
        'id': id,
        'pages': [urljoin(urls['root'], "/photos/gallery.php?id=%d&page=%d") % (id, i) for i in xrange(1, pages + 1)],
    }