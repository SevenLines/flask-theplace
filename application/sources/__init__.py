__author__ = 'm'


class Source(object):
    name = ""
    root = ""
    photos = ""
    decode = "utf8"

    category_item_xpath = ""
    image_item_xpath = ""
    paginator_item_xpath = ""

    @property
    def paths(self):
        return []

    def category_info(self, node):
        """
        :param node: which contains info about album
        :return: triple: (name, absolute_url, local_id)
        """
        return None

    def image_info(self, node):
        pass

    def pages(self, node):
        """
        :param node:
        :return: tripple (pages_urls, album_id, next_page)
        """
        pass