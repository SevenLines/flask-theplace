import os
import tempfile
import unittest
import theplace

__author__ = 'm'


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, theplace.app.config['DATABASE'] = tempfile.mkstemp()
        theplace.app.config['TESTING'] = True
        self.app = theplace.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(theplace.app.config['DATABASE'])

    def test_index_should_response(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)


