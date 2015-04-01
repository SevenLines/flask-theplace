import os
import tempfile
import unittest
from flask import url_for
import shutil
import application.app_settings
from helpers import SourceExtractor

__author__ = 'm'


class FlaskTestCase(unittest.TestCase):

    save_path = os.path.abspath('tests/media')
    image_bam_src = 'http://www.imagebam.com/image/e722cc393497689'
    bad_image_bam_src = 'http://www.imagebam.com/image/ae722cc393497689'
    image_venue_src = 'http://img285.imagevenue.com/img.php?image=157538130_HQ_002_122_110lo.jpg'

    def setUp(self):
        application.app_settings.app.config['SAVE_PATH'] = self.save_path
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_path)

        self.db_fd, application.app_settings.app.config['DATABASE'] = tempfile.mkstemp()
        application.app_settings.app.config['TESTING'] = True
        self.app = application.app_settings.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(application.app_settings.app.config['DATABASE'])

    def test_index_should_response(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)


    def test_download_cant_save_bad_image(self):
        bad_link = "http://www.imagebam.com/image/e1f066294507199"
        r = self.app.post('/download', data={'url':bad_link})
        self.assertFalse(os.path.exists(os.path.join(self.save_path, "_", "e1f066294507199.jpg")))
        self.assertEqual(r.status_code, 406)

    def test_download_should_save_good_images(self):
        good_link = "http://www.theplace.ru/archive/alison_brie/img/alison-briec.jpg"
        r = self.app.post('/download', data={'url':good_link})
        self.assertTrue(os.path.exists(os.path.join(self.save_path, "_", "alison-briec.jpg")))
        self.assertEqual(r.status_code, 200)


    def test_get_url_should_return_url_for_good_image(self):
        r = self.app.get('/image-src', query_string={'url':self.image_bam_src})
        src, _ = SourceExtractor.get_src(self.image_bam_src, '')
        self.assertEqual(r.data, src)

    def test_get_url_should_return_none_for_bad_image(self):
        r = self.app.get('/image-src', query_string={'url': self.bad_image_bam_src})
        self.assertEqual(r.data, "")
