import os
import requests

from lxml import html

from application.app_settings import app
from application.sources.hqcelebrity import HqCelebritySource
from application.sources.theplace import ThePlaceSource
from carreck import CarreckSource


sources = {
    ThePlaceSource.name: ThePlaceSource(),
    CarreckSource.name: CarreckSource(),
    HqCelebritySource.name: HqCelebritySource(),
}


def open_url_ex(url, referrer='http://www.carreck.com/pictures/'):
    r = requests.get(url)
    return r

def is_local():
    return app.config['USE_LOCAL']


def get_image_path(url, category_name):
    filename = url.split("/")[-1]
    return os.path.join(app.config['SAVE_PATH'], category_name, filename)


def get_albums(source):
    source = sources[source]
    for path in source.paths:
        response = open_url_ex(path, source.photos)
        response = response.text
        root = html.fromstring(response)

        for node in root.xpath(source.album_item_xpath):
            name, href, local_id = source.album_info(node)
            yield {
                'name': name,
                'href': href,
                'local_id': local_id,
            }


def get_images(source, url, name):
    source = sources[source]
    response = open_url_ex(url, source.photos)
    response = response.text

    root = html.fromstring(response)

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
