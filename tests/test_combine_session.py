import json
import uuid
from unittest.mock import create_autospec

from ssshare.services.fxc.api import FXCWebApiService
from tests import MainTestClass
from ssshare.blueprints.validators import is_uuid


class TestCombineSession(MainTestClass):
    def setUp(self):
        self.master_alias = 'the session master'
        self.session_alias = 'the session alias'

    def test_create_session(self, session_type='transparent', shares=5, quorum=3):
        print('CombineSession: a master create a session')
        payload = {
            "client_alias": self.master_alias,
            "session_alias": self.session_alias,
            "session_type": session_type,
            "session_policies": {
                "shares": shares,
                "quorum": quorum,
                "protocol": "fxc1"
            }
        }
        response = self.client.post('/combine', data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][0]['auth']))
        self._masterkey = response.json['session']['users'][0]['auth']
        self.assertEqual(
            {
                'session': {
                    'secret': {
                        'protocol': 'fxc1',
                        'quorum': 3,
                        'shares': 5
                               },
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master',
                            'auth': self._masterkey,
                            'shareholder': False
                        }
                    ],
                    'ttl': response.json['session']['ttl'],
                    'alias': 'the session alias',
                    'subtype': session_type
                },
                'session_id': response.json['session_id']
             },
            response.json
        )
        return response.json

    def test_get_session(self):
        jsonresponse = self.test_create_session()
        print('CombineSession: a master get a created session')
        session_id, user_key, alias = jsonresponse['session_id'], \
                                      jsonresponse['session']['users'][0]['auth'], \
                                      jsonresponse['session']['users'][0]['alias']
        response = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (session_id, user_key, alias))
        self.assertEqual(response.json, jsonresponse)

    def test_get_session_404_no_session(self):
        print('CombineSession: a get happen on a non existent session')
        response = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (
            str(uuid.uuid4()), str(uuid.uuid4()), 'client_alias')
        )
        self.assert404(response)

    def test_get_session_401_no_auth(self):
        jsonresponse = self.test_create_session()
        print('CombineSession: a get happen on a good session, but without rights')
        session_id, _ = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']
        response = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (
            session_id, str(uuid.uuid4()), 'user_without_rights')
        )
        self.assert401(response)

    def test_get_session_410_expired(self):
        jsonresponse = self.test_create_session()
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']

        # force session expiration
        print('CombineSession: the session expires')
        from ssshare.control import secret_share_repository
        data = secret_share_repository.get_session('combine/{}'.format(session_id))
        data['last_update'] = 1 # epoch based, last update in the shiny 70s
        secret_share_repository.update_session(data)
        print('CombineSession: someone request an expired session')
        response = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (session_id, user_key, 'client_alias'))
        self.assertEqual(response.status_code, 410)

    def test_put_share(self, session_type='transparent', shares=5, quorum=3):
        jsonresponse = self.test_create_session(session_type=session_type, shares=shares, quorum=quorum)
        alias, session_id, user_key = jsonresponse['session']['users'][0]['alias'], \
                                      jsonresponse['session_id'], \
                                      jsonresponse['session']['users'][0]['auth']
        payload = {
            'client_alias': 'case',
            'share': 'cafe01'
        }
        response = self.client.put('/combine/%s' % session_id, data=json.dumps(payload))
        self.assert200(response)
        self.user_with_uuid_have_share(response.json, 'cafe01')
        self.assertEqual(response.json['session']['users'][1]['alias'], 'case')
        print('CombineSession: a client join a combine session and present its share')
        return response.json

    def _test_combine(self, combine_type='transparent'):
        jsonresponse = self.test_put_share(session_type=combine_type)
        session_id = jsonresponse['session_id']
        payload = {
            'client_alias': 'molly',
            'share': 'cafe02'
        }
        subscribe2 = self.client.put('/combine/%s' % session_id, data=json.dumps(payload))
        print(subscribe2.json)
        self.assert200(subscribe2)
        self.assertEqual(subscribe2.json['session']['users'][2]['alias'], 'molly')
        self.user_with_uuid_have_share(subscribe2.json, 'cafe02')
        print('CombineSession: the second client join a combine session and present its share')
        payload = {
            'client_alias': 'armitage',
            'share': 'cafe03'
        }
        from ssshare import control
        control.fxc_web_api_service = create_autospec(FXCWebApiService)
        control.fxc_web_api_service.combine.return_value = 'secret'
        subscribe3 = self.client.put('/combine/%s' % session_id, data=json.dumps(payload))
        self.assert200(subscribe3)
        self.user_with_uuid_have_share(subscribe3.json, 'cafe03')
        self.assertEqual(subscribe3.json['session']['users'][3]['alias'], 'armitage')
        expected_secret = {
            'protocol': 'fxc1',
            'quorum': 3,
            'sha256': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b',
            'shares': 5,
        }
        if combine_type == 'transparent':
            expected_secret['secret'] = 'secret'

        self.assertEqual(subscribe3.json['session']['secret'], expected_secret)
        print('CombineSession: the third client join a combine session and present its share')
        return subscribe3.json


    def test_transparent_combine(self):
        self._test_combine()

    def test_federated_combine(self):
        res = self._test_combine(combine_type='federated')
        res['session']['secret']['secret'] = 'secret'
        master_res = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (res['session_id'], self._masterkey, self.master_alias))
        expected_master_res = {
            'session_id': res['session_id'],
            'session': {
                'alias': 'the session alias',
                'secret': {
                    'shares': 5,
                    'quorum': 3,
                    'sha256': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b',
                    'protocol': 'fxc1',
                    'secret': 'secret'
                },
                'subtype': 'federated'
            }
        }
        self.assertEqual(expected_master_res['session']['alias'], master_res.json['session']['alias'])
        self.assertEqual(expected_master_res['session']['secret'], master_res.json['session']['secret'])
        self.assertEqual(expected_master_res['session']['subtype'], master_res.json['session']['subtype'])
        self.assertEqual(4, len(master_res.json['session']['users']))


