from secretshare.app import app
from flask_testing import TestCase


class MainTestClass(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def create_app(self):
        app.config['TESTING'] = True
        return app