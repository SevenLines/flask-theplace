import re
from urllib2 import urlopen
from urlparse import urljoin
from lxml import html
from lxml.cssselect import CSSSelector
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

    album_item_xpath = CSSSelector(".alblink a").path
    image_item_xpath = CSSSelector(".thumbnails .image").path
    paginator_item_xpath = CSSSelector(".navmenu a").path

    regexp = re.compile(r"(.*?)/thumb_(.*)")

    @property
    def paths(self):
        out = []
        for category in self.categories:
            url = "http://hqcelebrity.org/index.php?cat=%s" % category
            if url not in out:
                out.append(url)
                yield url

            r = urlopen(url)
            root = html.fromstring(r.read())
            navmenu = root.cssselect(".navmenu a")
            for link in navmenu:
                url = link.get("href")
                if url not in out:
                    out.append(url)
                    yield urljoin(self.root, url)