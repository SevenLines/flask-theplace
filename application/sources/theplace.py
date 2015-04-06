from urlparse import urljoin
import re
from lxml.cssselect import CSSSelector
from application.sources import Source

__author__ = 'm'


class ThePlaceSource(Source):
    name = "theplace"
    root = "http://www.theplace.ru/"
    photos = "http://www.theplace.ru/photos/"
    decode = "windows-1251"

    category_item_xpath = '//table[@id="models_list"]//a'
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

    def category_info(self, node):
        href = urljoin(self.photos, node.get("href"))
        id_ = re.search(r"mid(\d+)\.html", node.get("href")).group(1)
        return {
            'name': node.text,
            'local_url': href,
            'local_id': id_,
            'albums': [
                {
                    'album_id': id_,
                    'local_url': href
                },
            ]
        }

    def image_info(self, node):
        src = self.regexp.sub(r'\1\2', node.get('src'))
        return {
            "thumbnail": urljoin(self.root, node.get('src')),
            "src": urljoin(self.root, src),
        }

    def pages(self, node):
        if len(node) > 0:
            node = node[-1]
            href = node.get('href')
            regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
            m = regexp.search(href)
            if m:
                id = int(m.group(1))
                pages = int(m.group(2))
            else:
                return [], -1, ""

            return list([urljoin(self.root, "/photos/gallery.php?id=%d&page=%d" % (id, i))
                         for i in xrange(1, pages + 1)]), id, ""

        else:
            return [], -1, ""











