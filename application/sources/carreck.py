from urlparse import urljoin
import re
from lxml.cssselect import CSSSelector
from application.sources import Source

__author__ = 'm'


class CarreckSource(Source):
    name = "carreck"
    root = "http://www.carreck.com/"
    photos = "http://www.carreck.com/pictures/"
    # decode = "windows-1251"

    album_item_xpath = CSSSelector(".widget_categories .cat-item").path
    image_item_xpath = CSSSelector('.postentry a.ext-link').path
    paginator_item_xpath = CSSSelector('.navigation .alignleft a').path

    regexp = re.compile(r"(.*?)_s(\.\w+)")

    @property
    def paths(self):
        return [self.photos, ]

    def album_info(self, node):
        m = re.search("cat-item-(\d+)", node.get("class"))
        id_ = -1
        if m:
            id_ = m.group(1)

        a = node.xpath("a")[-1]
        return (
            a.text,
            a.get("href"),
            id_,
        )

    def image_info(self, node):
        img_list = node.xpath("img")
        if len(img_list):
            img = img_list[-1]
        else:
            return None
        return {
            "thumbnail": img.get("src"),
            "src": node.get("href")
        }

    def pages(self, node):
        if len(node) > 0:
            node = node[-1]
            return [], -1, node.get("href")
        else:
            # if len(node) > 0:
            #     node = node[-1]
            #     href = node.get('href')
            #     regexp = re.compile(r"/photos/gallery\.php\?id=(\d+)&page=(\d+)")
            #     m = regexp.search(href)
            #     if m:
            #         id = int(m.group(1))
            #         pages = int(m.group(2))
            #     else:
            #         return [], -1
            #
            #     return list([urljoin(self.root, "/photos/gallery.php?id=%d&page=%d" % (id, i))
            #                  for i in xrange(1, pages + 1)]), id
            #
            # else:
            return [], -1, ""
