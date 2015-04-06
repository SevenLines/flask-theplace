import re
from urllib2 import urlopen
from urlparse import urljoin
from lxml import html
from lxml.cssselect import CSSSelector
import requests
from application.sources import Source

__author__ = 'm'


class HqDiesel(Source):
    name = "hqdiesel"
    root = "http://www.hqdiesel.net/"
    photos = "http://www.hqdiesel.net/gallery"

    categories = [
        140, 64,  # male celebs
        37, 38, 40, 41, 42,  # female celebs
        80, 31, 552, 553,  # models
        # 33, 191,  # movies
    ]

    category_item_xpath = CSSSelector(".catlink a").path
    image_item_xpath = CSSSelector(".thumbnails .image").path
    paginator_item_xpath = CSSSelector(".navmenu a").path

    regexp = re.compile(r"(.*?)/thumb_(.*)")

    @property
    def paths(self):
        out = []
        for category in self.categories:
            url = "http://www.hqdiesel.net/gallery/index.php?cat=%s" % category
            if url not in out:
                out.append(url)
                yield url


    def category_info(self, node):
        href = "%s/%s" % (self.photos, node.get("href"))
        id_ = re.search(r"\?cat=(\d+)", node.get("href")).group(1)

        # r = requests.get(href)
        # root = html.fromstring(r.read())

        return {
            'name': node.text,
            'local_url': href,
            'local_id': id_,
            'albums': []
        }

    def image_info(self, node):
        src = node.get('src')
        thumbnail = src
        src = src.replace('/thumb_', '/')
        # src = self.regexp.sub(r'\1/\2', node.get('src'))
        return {
            'thumbnail': "%s/%s" % (self.photos, thumbnail),
            'src': "%s/%s" % (self.photos, src),
        }

    def pages(self, nodes):
        max_num = 1
        id = -1
        for node in nodes:
            href = node.get("href")
            m = re.match("thumbnails\.php\?album=(\d+)&page=(\d+)", href)
            if m:
                id = int(m.group(1))
                page_num = int(m.group(2))
                if page_num > max_num:
                    max_num = page_num

        return list(["%s/%s" % (self.photos, "thumbnails.php?album=%d&page=%d" % (id, i))
                     for i in xrange(1, max_num + 1)]), id, ""

    def get_albums(self, url):
        r = requests.get(url)
        root = html.fromstring(r.text)

        albums_nodes = root.cssselect(".alblink a")
        for album in albums_nodes:
            yield {
                'local_url': "%s/%s" % (self.photos, album.get("href")),
                'name': album.text,
                'album_id': re.search(r"\?album=(\d+)", album.get("href")).group(1)
            }