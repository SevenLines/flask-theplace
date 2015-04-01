import os
from urllib2 import urlopen
import urllib2

from lxml import html

from application.app_settings import app
from application.sources.hqcelebrity import HqCelebritySource
from application.sources.theplace import ThePlaceSource
from carreck import CarreckSource


sources = {
    ThePlaceSource.name: ThePlaceSource(),
    HqCelebritySource.name: HqCelebritySource(),
    CarreckSource.name: CarreckSource(),
}


def open_url_ex(url, referrer='http://www.carreck.com/pictures/'):
    r = urllib2.Request(url, None,
                        headers={
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Connection': 'keep-alive',
                                'Cache-Control':"max-age=0",
                                'Referer': referrer})
    return urlopen(r)

def is_local():
    return app.config['USE_LOCAL']


def get_image_path(url, category_name):
    filename = url.split("/")[-1]
    return os.path.join(app.config['SAVE_PATH'], category_name, filename)


def get_albums(source):
    source = sources[source]
    for path in source.paths:
        data = open_url_ex(path, source.photos)
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
    try:
        data = open_url_ex(url, source.photos)
    except urllib2.HTTPError, e:
        print e.fp.read()
        raise e
        # return {
        #     'images': [],
        #     'id': -1,
        #     'pages': []
        # }
    data = data.read().decode(source.decode)

    root = html.fromstring(data)

    images = []

    if source.image_item_xpath:
        for node in root.xpath(source.image_item_xpath):
            image = source.image_info(node)
            if not image:
                continue

            if is_local():
                exists = os.path.exists(get_image_path(image['src'], name))
            else:
                exists = False

            image.update({
                'exists': exists
            })
            images.append(image)

    id_ = -1
    pages = []
    next_page = ""
    if source.paginator_item_xpath:
        paginator = root.xpath(source.paginator_item_xpath)
        pages, id_, next_page = source.pages(paginator)

    return {
        'images': images,
        'id': id_,
        'pages': pages,
        'next_page': next_page,
    }
