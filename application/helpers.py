import glob
import os
import re
from urlparse import urljoin
import requests

from lxml import html
from sqlalchemy.sql import ClauseElement

from application.app_settings import app
from application.sources.hqcelebrity import HqCelebritySource
from application.sources.theplace import ThePlaceSource
from application.sources.carreck import CarreckSource
from hqdiesel import HqDiesel


sources = {
    ThePlaceSource.name: ThePlaceSource(),
    CarreckSource.name: CarreckSource(),
    HqCelebritySource.name: HqCelebritySource(),
    HqDiesel.name: HqDiesel()
}


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        # session.commit()
        return instance



def open_url_ex(url, referrer='http://www.carreck.com/pictures/'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Referer': referrer
    }
    r = requests.get(url, headers=headers)
    return r


def is_local():
    return app.config['USE_LOCAL']


def get_image_path(filename, category_name, source):
    # filename = url.split("/")[-1]
    return os.path.join(app.config['SAVE_PATH'], category_name, source, filename)


def get_categories(source):
    source = sources[source]
    for path in source.paths:
        response = open_url_ex(path, source.photos)
        response = response.text
        root = html.fromstring(response)

        for node in root.xpath(source.category_item_xpath):
            yield source.category_info(node)


def get_images(source_name, url, name):
    source = sources[source_name]
    response = open_url_ex(url, source.photos)
    response = response.text

    root = html.fromstring(response)

    images = []

    if source.image_item_xpath:
        for node in root.xpath(source.image_item_xpath):
            image = source.image_info(node)
            if not image:
                continue

            filename = SourceExtractor.get_path(image['src'], name, source_name)

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


def get_albums(source_name, url):
    return sources[source_name].get_albums(url)


class SourceExtractor(object):
    """
    get image url even  if it
    """

    @classmethod
    def get_type(cls, url):
        for type, info in cls.TYPES.items():
            if re.search(info['pattern'], url):
                return info, type
        return None, ""

    @classmethod
    def get_src(cls, url, category_name, source):
        type, type_name = cls.get_type(url)
        path = cls.__get_path(url, category_name, source, type, type_name)
        if type is None:
            return url, path
        else:
            return type['src'](url, category_name), path


    @classmethod
    def get_path(cls, url, category_name, source):
        type, type_name = cls.get_type(url)
        return cls.__get_path(url, category_name, source, type, type_name)

    @classmethod
    def __get_path(cls, url, category_name, source, type, type_name):
        if type is None:
            filename = url.split('/')[-1]
        else:
            filename = type['filename'](url)
        return get_image_path("%s%s" % (type_name, filename), category_name, source)


    # region imagebam.com
    @classmethod
    def __get_imagebam_name(cls, url):
        return url.split('/')[-1]

    @classmethod
    def __get_imagebam(cls, url, category_name):
        r = requests.get(url)
        root = html.fromstring(r.text)

        img = root.cssselect("#imageContainer img")
        if len(img):
            img = img[-1]
        else:
            return ""

        return img.get("src")

    # endregion

    # region imagevenue
    @classmethod
    def __get_imagevenue_name(cls, url):
        m = re.search(cls.TYPES['imagevenue']['pattern'], url)
        if m:
            return m.group(2)
        else:
            ""
            # return get_image_path(m.group(2), category_name, source)
            # else:
            # return None

    @classmethod
    def __get_imagevenue(cls, url, category_name):
        r = requests.get(url)
        root = html.fromstring(r.text)

        m = re.search(cls.TYPES['imagevenue']['pattern'], url)

        img = root.cssselect("#thepic")
        if len(img):
            img = img[-1]
        else:
            return ""

        return urljoin(url, img.get("src"))

    # endregion

    # region imgbox
    @classmethod
    def __get_imgbox(cls, url, category_name):
        r = requests.get(url)
        root = html.fromstring(r.text)

        img = root.cssselect(".image-container img")
        if len(img):
            img = img[-1]
        else:
            return ""
        return img.get('src')


    @classmethod
    def __get_imgbox_name(cls, url):
        m = re.search(cls.TYPES['imgbox']['pattern'], url)
        if m:
            return m.group(1)
        else:
            return None

    # endregion


    TYPES = {
        'imagebam': {
            'pattern': r'^http://www.imagebam.com/',
            'src': lambda url, category_name: SourceExtractor.__get_imagebam(url, category_name),
            'filename': lambda url: SourceExtractor.__get_imagebam_name(url)
        },
        'imagevenue': {
            'pattern': r'^http://img(\d+)\.imagevenue.com/img.php\?.*?image=(.*)',
            'src': lambda url, category_name: SourceExtractor.__get_imagevenue(url, category_name),
            'filename': lambda url: SourceExtractor.__get_imagevenue_name(url)
        },
        'imgbox': {
            'pattern': r'^http://imgbox.com/(\w+)',
            'src': lambda url, category_name: SourceExtractor.__get_imgbox(url, category_name),
            'filename': lambda url: SourceExtractor.__get_imgbox_name(url)
        }
    }
