from ssshare.app import app
from flask_testing import TestCase


class MainTestClass(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def user_with_uuid_have_share(self, response, share_id):
        for x in response['session']['users']:
            if x.get('auth'):
                if x.get('shareholder', True):
                    self.assertEqual(x['share'], share_id)
                    print('User with uuid {} have share_id {}'.format(x['auth'], x['share']))
