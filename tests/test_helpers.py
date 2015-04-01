import imghdr
from unittest.case import TestCase
import requests
from helpers import SourceExtractor

__author__ = 'm'


class TestHelpers(TestCase):

    def test_get_imagebum_img_should_return_image(self):
        url = "http://www.imagebam.com/image/e722cc393497689"
        src = SourceExtractor.get_src(url)
        self.assertNotEqual(src, "")

        img = requests.get(src)
        what = imghdr.what(None, img.content)
        self.assertEqual(what, "jpeg")
