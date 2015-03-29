from urllib2 import urlopen
from urlparse import urljoin
from lxml import html
from lxml.cssselect import CSSSelector
import re
from application.sources import Source

__author__ = 'm'


class HqCelebritySource(Source):
    name = "hqcelebrity"
    root = "http://hqcelebrity.org/"

    categories = [
        4,  # male celebs
        23, 24, 25, 26, 27,  # female celebs
        31, 32, 33  # multiple celebs
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

    def album_info(self, node):
        return (
            node.text,
            urljoin(self.root, node.get("href")),
            re.search(r"\?album=(\d+)", node.get("href")).group(1),
        )

    def image_info(self, node):
        src = self.regexp.sub(r'\1/\2', node.get('src'))
        return {
            'thumbnail': urljoin(self.root, node.get("src")),
            'src': urljoin(self.root, src),
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

        return list([urljoin(self.root, "thumbnails.php?album=%d&page=%d" % (id, i))
                     for i in xrange(1, max_num+1)]), id






