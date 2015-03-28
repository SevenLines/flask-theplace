__author__ = 'm'


class Source(object):
    name = ""
    root = ""
    photos = ""
    decode = "utf8"

    album_item_xpath = ""
    image_item_xpath = ""
    paginator_item_xpath = ""

    @property
    def paths(self):
        return []

    def album_info(self, node):
        """
        :param node: which contains info about album
        :return: triple: (name, absolute_url, local_id)
        """
        return None

    def image_info(self, node):
        pass

    def pages(self, node):
        pass