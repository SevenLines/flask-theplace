from urlparse import urljoin
import re
from lxml.cssselect import CSSSelector
from application.sources import Source

__author__ = 'm'


class HqPicturesSource(Source):
    name = "hqpictures"
    root = "http://hq-pictures.com/index.php"
    # photos = "http://www.theplace.ru/photos/"
    # decode = "windows-1251"

    album_item_xpath = '//table[@id="models_list"]//a'
    image_item_xpath = CSSSelector('.gallery-pics-list a img').path
    paginator_item_xpath = CSSSelector('.listalka.ltop a').path

    regexp = re.compile(r"(.*?)_s(\.\w+)")

    @property
    def paths(self):
        return ["%sphotos/?s_id=0" % self.root,
                "%sphotos/?s_id=1" % self.root,
                "%sphotos/?s_id=2" % self.root,
                "%sphotos/?s_id=3" % self.root,
                ]

    def album_info(self, node):
        return (
            node.text,
            urljoin(self.photos, node.get("href")),
            re.search(r"mid(\d+)\.html", node.get("href")).group(1),
        )

    def image_info(self, node):
        src = self.regexp.sub(r'\1\2', node.get('src'))
        return {
            "thumbnail": urljoin(self.root, node.get('src')),
            "src": urljoin(self.root, src),
        }

    def pages(self, node):
        node = node[-1]
        href = node.get('href')
        regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
        m = regexp.search(href)
        if m:
            id = int(m.group(1))
            pages = int(m.group(2))
        else:
            return []

        return list([urljoin(self.root, "/photos/gallery.php?id=%d&page=%d" % (id, i))
                     for i in xrange(1, pages + 1)]), id, ""











