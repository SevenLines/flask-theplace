import imghdr
from unittest.case import TestCase
import requests
from helpers import SourceExtractor

__author__ = 'm'


class TestHelpers(TestCase):
    image_bam_src = 'http://www.imagebam.com/image/e722cc393497689'
    image_venue_src = 'http://img285.imagevenue.com/img.php?image=157538130_HQ_002_122_110lo.jpg'

    def test_source_extractor_get_src_for_imagebam(self):
        src, path = SourceExtractor.get_src(self.image_bam_src, '_')
        self.assertNotEqual(src, "")
        self.assertTrue(path.endswith("e722cc393497689"))

        img = requests.get(src)
        what = imghdr.what(None, img.content)
        self.assertEqual(what, "jpeg")


    def test_source_extractor_get_src_for_imagevenue(self):
        src, path = SourceExtractor.get_src(self.image_venue_src, '_')
        self.assertNotEqual(src, "")
        self.assertTrue(path.endswith("157538130_HQ_002_122_110lo.jpg"))

        img = requests.get(src)
        what = imghdr.what(None, img.content)
        self.assertEqual(what, "jpeg")


    def test_get_type(self):
        type = SourceExtractor.get_type(self.image_bam_src)
        self.assertEqual(SourceExtractor.TYPES['imagebam'], type)

        type = SourceExtractor.get_type(self.image_venue_src)
        self.assertEqual(SourceExtractor.TYPES['imagevenue'], type)