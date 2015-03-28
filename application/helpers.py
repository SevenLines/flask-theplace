import os
from urllib2 import urlopen

from lxml import html

from application.app_settings import app
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

    if source.image_item_xpath:
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

    id_ = -1
    pages = []
    if source.paginator_item_xpath:
        paginator = root.xpath(source.paginator_item_xpath)
        pages, id_ = source.pages(paginator)

    return {
        'images': images,
        'id': id_,
        'pages': pages
    }
