import os
from urllib2 import urlopen
from urlparse import urljoin
import re

from lxml import html

from application.app_settings import app
from application.models import Category
from application.sources.hqcelebrity import HqCelebritySource
from application.sources.theplace import ThePlaceSource


sources = {
    ThePlaceSource.name: ThePlaceSource(),
    HqCelebritySource.name: HqCelebritySource(),
}


def is_local():
    return app.config['USE_LOCAL']


def get_image_path(url, category_name):
    filename = url.split("/")[-1]
    return os.path.join(app.config['SAVE_PATH'], category_name, filename)


def get_albums(source):
    source = sources[source]
    for path in source.paths:
        data = urlopen(path)
        data = data.read().decode(source.decode)
        root = html.fromstring(data)

        for node in root.xpath(source.album_item_xpath):
            name, href, local_id = source.album_info(node)
            yield {
                'name': name,
                'href': href,
                'local_id': local_id,
            }


def get_images(source, url, name):
    source = sources[source]
    data = urlopen(url)
    data = data.read().decode(source.decode)

    root = html.fromstring(data)

    images = []

    for node in root.xpath(source.image_item_xpath):
        image = source.image_info(node)

        if is_local():
            exists = os.path.exists(get_image_path(image['src'], name))
        else:
            exists = False

        image.update({
            'exists': exists
        })
        images.append(image)

    paginator = root.xpath(source.paginator_item_xpath)

    id_ = -1
    pages, id_ = source.pages(paginator)

    return {
        'images': images,
        'id': id_,
        'pages': pages
    }



    # gallery = root.find_class('gallery-pics-list')
    # if len(gallery):
    # gallery = gallery[-1]
    # else:
    #     return []
    #
    # images = gallery.cssselect("a img")
    # listalka = root.cssselect(".listalka.ltop a")
    # id = -1
    # pages = 0
    # if len(listalka):
    #     href = listalka[-1].get('href')
    #     regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
    #     m = regexp.search(href)
    #     if m:
    #         id = int(m.group(1))
    #         pages = int(m.group(2))
    #
    # regexp = re.compile(r"(.*?)_s(\.\w+)")
    # category = Category.query.filter(Category.local_id == id).first()
    #
    # images_out = []
    # for img in images:
    #     src = regexp.sub(r'\1\2', img.get('src'))
    #     if is_local():
    #         exists = os.path.exists(get_image_path(src, category.name)) if category else False
    #     else:
    #         exists = False
    #     images_out.append({"thumbnail": urljoin(source['root'], img.get('src')),
    #                        "src": urljoin(source['root'], src),
    #                        "exists": exists,
    #                        })
    #
    # [urljoin(source['root'], "/photos/gallery.php?id=%d&page=%d") % (id, i) for i in
    #                   xrange(1, pages + 1)],
    #     }
