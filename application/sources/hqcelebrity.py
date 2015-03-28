from application.sources import Source

__author__ = 'm'


class HqCelebritySource(Source):
    name = "hqcelebrity"
    root = "http://hqcelebrity.org/"
    # photos = "http://www.theplace.ru/photos/"
    # decode = "windows-1251"

    # album_item_xpath = '//table[@id="models_list"]//a'
    @property
    def paths(self):
        return []
