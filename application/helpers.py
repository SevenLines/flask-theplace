import glob
import os
import requests

from lxml import html

from application.app_settings import app
from application.sources.hqcelebrity import HqCelebritySource
from application.sources.theplace import ThePlaceSource
from application.sources.carreck import CarreckSource


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

            filename = SourceExtractor.get_path(image['src'], name)

            if is_local():
                files = glob.glob("%s*" % filename)
                exists = len(files) > 0
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


class SourceExtractor(object):
    """
    get image url even  if it
    """

    @classmethod
    def get_type(cls, url):
        for type, info in cls.TYPES.items():
            if url.startswith(info['prefix']):
                return info
        return None

    @classmethod
    def get_src(cls, url, category_name):
        type = cls.get_type(url)
        if type is None:
            return url, get_image_path(url, category_name)
        else:
            return type['src'](url, category_name), type['path'](url, category_name)


    @classmethod
    def get_path(cls, url, category_name):
        type = cls.get_type(url)
        if type is None:
            return get_image_path(url, category_name)
        else:
            return type['path'](url, category_name)

    # region imagebam.com
    @staticmethod
    def __get_imagebam_path(url, category_name):
        filename = get_image_path(url, category_name)
        return filename

    @staticmethod
    def __get_imagebam(url, category_name):
        r = requests.get(url)
        root = html.fromstring(r.text)

        img = root.cssselect("#imageContainer img")
        if len(img):
            img = img[-1]
        else:
            return ""

        return img.get("src")
    # endregion

    TYPES = {
        'imagebam': {
            'prefix': 'http://www.imagebam.com/',
            'src': lambda url, category_name: SourceExtractor.__get_imagebam(url, category_name),
            'path': lambda url, category_name: SourceExtractor.__get_imagebam_path(url, category_name)
        }
    }
