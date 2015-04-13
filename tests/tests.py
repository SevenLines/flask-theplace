from __future__ import absolute_import
import json

import os
import tempfile
import unittest
from flask import url_for
import shutil
from flask.ext.migrate import upgrade
import application.app_settings
from application.helpers import SourceExtractor
from application.models import migrate

__author__ = 'm'


class FlaskTestCase(unittest.TestCase):
    save_path = os.path.abspath('tests/media')
    image_bam_src = 'http://www.imagebam.com/image/e722cc393497689'
    bad_image_bam_src = 'http://www.imagebam.com/image/ae722cc393497689'
    image_venue_src = 'http://img285.imagevenue.com/img.php?image=157538130_HQ_002_122_110lo.jpg'

    @classmethod
    def setUpClass(cls):
        cls.app = application.app_settings.app
        cls.app.config['SAVE_PATH'] = cls.save_path
        cls.app.config['SERVER_NAME'] = 'localhost:5000'
        if os.path.exists(cls.save_path):
            shutil.rmtree(cls.save_path)

        cls.db_fd, application.app_settings.app.config['DATABASE'] = tempfile.mkstemp()
        application.app_settings.app.config['TESTING'] = True
        cls.client = application.app_settings.app.test_client()

        with application.app_settings.app.app_context():
            upgrade()

    def setUp(self):
        self.client_context = self.app.app_context()
        self.client_context.push()

    def tearDown(self):
        self.client_context.pop()

    def test_index_should_response(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_images_should_contains_source_info(self):
        url = 'http://www.theplace.ru/photos/Alison_Brie-mid3918.html'
        id = 3918
        r = self.client.get(url_for('images'), query_string={
            'url': url,
            'id': id,
        }, headers=[('X-Requested-With', 'XMLHttpRequest')])
        data = json.loads(r.data)
        self.assertIn('source', data)

    def test_download_cant_save_bad_image(self):
        bad_link = "http://www.imagebam.com/image/e1f066294507199"
        r = self.client.post(url_for('download'), data={'url': bad_link})
        self.assertFalse(os.path.exists(os.path.join(self.save_path, "_", "e1f066294507199.jpg")))
        self.assertEqual(r.status_code, 406)

    def test_download_should_save_good_images(self):
        good_link = "http://www.theplace.ru/archive/alison_brie/img/alison-briec.jpg"
        r = self.client.post(url_for('download'), data={'url': good_link, 'source': 'source'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(os.path.exists(os.path.join(self.save_path, "_", "source", "alison-briec.jpg")))

    def test_remove_should_remove_existing_image(self):
        good_link = "http://www.theplace.ru/archive/alison_brie/img/alison-briec.jpg"
        r = self.client.post(url_for('download'), data={'url': good_link, 'source': 'source', 'name': 'Alison Brie'})
        path = os.path.join(self.save_path, "Alison Brie", "source", "alison-briec.jpg")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(os.path.exists(path))

        r = self.client.post('/remove', data={'url': good_link, 'source': 'source', 'name': 'Alison Brie'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(os.path.exists(path))

    def test_get_url_should_return_url_for_good_image(self):
        r = self.client.get(url_for('image_src'), query_string={'url': self.image_bam_src})
        src, _ = SourceExtractor.get_src(self.image_bam_src, '', 'source')
        self.assertEqual(r.data, src)

    def test_get_url_should_return_none_for_bad_image(self):
        r = self.client.get(url_for('image_src'), query_string={'url': self.bad_image_bam_src})
        self.assertEqual(r.data, "")


    def test_superior_pics_can_process_custom_urls(self):
        url = "http://forums.superiorpics.com/ubbthreads/ubbthreads.php/topics/4640509/Alison_Brie_is_PERFECT"
        r = self.client.get(url_for('query_categories'), query_string={'query': url})
        data = json.loads(r.data)
        data = data['items'][0]

        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('sources', data)

        source = data['sources'][0]

        self.assertIn('name', source)
        self.assertIn('local_id', source)
        self.assertIn('local_url', source)
        self.assertIn('albums', source)

        album = source['albums'][0]

        self.assertIn('id', album)
        self.assertIn('name', album)
        self.assertIn('album_id', album)
        self.assertIn('local_url', album)

    def test_superior_pics_process_images(self):
        urls = [
            "http://forums.superiorpics.com/ubbthreads/ubbthreads.php/topics/2907126/Aisleyne_HorganWallace_@_The_2"
            "http://forums.superiorpics.com/ubbthreads/ubbthreads.php/topics/1842804/Aisleyne_Horgan_Wallace_Variou"
            "http://forums.superiorpics.com/ubbthreads/ubbthreads.php/topics/4640509/Alison_Brie_is_PERFECT",
        ]
        for url in urls:
            r = self.client.get(url_for('images'), query_string={'url': url, 'id': -1})

            data = json.loads(r.data)

            self.assertIn('data', data)
            self.assertIn('images', data['data'])

            images = data['data']['images']

            self.assertGreater(len(images), 0)