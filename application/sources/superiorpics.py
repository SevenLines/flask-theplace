from urlparse import urljoin
import re
from lxml import html
from lxml.cssselect import CSSSelector
import requests
from application.sources import Source

__author__ = 'm'


class SuperiorPicsSource(Source):
    name = "superiorpics"
    root = "http://forums.superiorpics.com/"
    photos = "http://forums.superiorpics.com/"

    category_item_xpath = ''
    image_item_xpath = CSSSelector('.post_inner > div a').path
    paginator_item_xpath = CSSSelector('.listalka.ltop a').path

    @property
    def paths(self):
        return []

    def category_info(self, node):
        # href = urljoin(self.photos, node.get("href"))
        # id_ = re.search(r"mid(\d+)\.html", node.get("href")).group(1)
        return {
            'name': '',
            'local_url': '',
            'local_id': '',
            'albums': []
        }

    def image_info(self, node):
        img = node.cssselect("img")
        if img:
            img = img[0]
        else:
            return None
        image = {
            "thumbnail": img.get('src'),
            "src": node.get('href'),
        }

        if image['src'].endswith('/'):
            return None

        return image

    def pages(self, node):
        # if len(node) > 0:
        # node = node[-1]
        # href = node.get('href')
        #     regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
        #     m = regexp.search(href)
        #     if m:
        #         id = int(m.group(1))
        #         pages = int(m.group(2))
        #     else:
        #         return [], -1, ""
        #
        #     return list([urljoin(self.root, "/photos/gallery.php?id=%d&page=%d" % (id, i))
        #                  for i in xrange(1, pages + 1)]), id, ""
        #
        # else:
        return [], -1, ""

    def get_album_info(self, url):
        if not url:
            return None
        if url.startswith("http://forums.superiorpics.com"):
            r = requests.get(url)

            root = html.fromstring(r.text)
            celebname = root.cssselect(".celebname a")
            celebname = celebname[0].text if len(celebname) > 0 else ""

            albums = [
                {
                    "id": -1,
                    "name": root.head.find('title').text,
                    "album_id": -1,
                    "local_url": url,
                }
            ]
            sources = [
                {
                    "name": self.name,
                    "local_id": -1,
                    "local_url": url,
                    "albums": albums,
                }
            ]

            return {
                "name": celebname,
                "id": -1,
                "sources": sources
            }
        else:
            return None











