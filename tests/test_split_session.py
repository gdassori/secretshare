import json
import uuid
from unittest.mock import create_autospec
from ssshare.domain.secret import Share
from ssshare.services.fxc.api import FXCWebApiService
from tests import MainTestClass
from ssshare.blueprints.validators import is_uuid


class TestSplitSession(MainTestClass):
    def setUp(self):
        self.master_alias = 'the session master'
        self.session_alias = 'the session alias'

    def test_create_session(self):
        print('SplitSession: a master create a session')
        payload = {
            "client_alias": self.master_alias,
            "session_alias": self.session_alias,
            "session_policies": {
                "quorum": 3,
                "shares": 5
            }
        }
        response = self.client.post('/split', data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][0]['auth']))
        self._masterkey = response.json['session']['users'][0]['auth']
        self.assertEqual(
            {
                'session': {
                    'secret': {
                        'quorum': 3,
                        'shares': 5,
                        'sha256': None,
                        'secret': None,
                        'protocol': 'fxc1'
                    },
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master',
                            'auth': self._masterkey,
                            'shareholder': False
                        }
                    ],
                    'ttl': 600,
                    'alias': 'the session alias'
                },
                'session_id': response.json['session_id']
             },
            response.json
        )
        return response.json

    def test_get_session(self):
        jsonresponse = self.test_create_session()
        print('SplitSession: a master get a created session')
        session_id, user_auth = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']
        response = self.client.get('/split/%s?auth=%s' % (session_id, user_auth))
        print(response.json)
        self.assertEqual(response.json, jsonresponse)

    def test_get_session_404_no_session(self):
        print('SplitSession: a get happen on a non existent session')
        response = self.client.get('/split/%s?auth=%s' % (str(uuid.uuid4()), str(uuid.uuid4())))
        self.assert404(response)

    def test_get_session_401_no_auth(self):
        jsonresponse = self.test_create_session()
        print('SplitSession: a get happen on a good session, but without rights')
        session_id, _ = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']
        response = self.client.get('/split/%s?auth=%s' % (session_id, str(uuid.uuid4())))
        self.assert401(response)

    def test_get_session_410_expired(self):
        jsonresponse = self.test_create_session()
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']

        # force session expiration
        print('SplitSession: the session expires')
        from ssshare.control import secret_share_repository
        data = secret_share_repository.get_session(session_id)
        data['last_update'] = 1 # epoch based, last update in the shiny 70s
        secret_share_repository.update_session(data)
        print('SplitSession: someone request an expired session')
        response = self.client.get('/split/%s?auth=%s' % (session_id, user_key))
        self.assertEqual(response.status_code, 410)

    def test_join_session(self):
        created_session = self.test_create_session()
        print('SplitSession: a user join a valid created session')
        payload = {
            'client_alias' : 'a shareholder'
        }
        response = self.client.put('/split/%s' % created_session['session_id'], data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][1]['auth']))
        session_id, user_auth = response.json['session_id'], response.json['session']['users'][1]['auth']
        expected_response = {
            'session': {
                'secret': {
                    'quorum': 3,
                    'shares': 5,
                    'sha256': None,
                    'protocol': 'fxc1'
                },
                'users': [
                    {'role': 'master', 'alias': 'the session master', 'shareholder': False},
                    {'role': 'user', 'auth': user_auth, 'alias': 'a shareholder'}
                ],
                'ttl': 600,
                'alias': 'the session alias',
            },
            'session_id': session_id
        }
        print(response.json)
        self.assertEqual(expected_response, response.json)
        return response.json

    def test_master_get_user_joined_session(self):
        joined_session = self.test_join_session()
        print('SplitSession: after a join, the master get the session and see the joined user')
        response = self.client.get('/split/%s?auth=%s' % (joined_session['session_id'], self._masterkey))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][1]['auth']))

    def test_user_join_session_401_twice_join(self):
        joined_session = self.test_join_session()
        print('SplitSession: a user is unable to join a session twice \ user alias is unique')
        payload = {
            'client_alias' : 'a shareholder'
        }
        response = self.client.put('/split/%s' % joined_session['session_id'], data=json.dumps(payload))
        self.assert401(response)

    def test_master_put_secret_on_joined_session(self):
        from ssshare import control
        control.fxc_web_api_service = create_autospec(FXCWebApiService)
        shares = [
            Share(value='cafe01'),
            Share(value='cafe02'),
            Share(value='cafe03'),
            Share(value='cafe04'),
            Share(value='cafe05')
        ]
        control.fxc_web_api_service.split.return_value = shares
        joined_session = self.test_join_session()
        print('SplitSession: a master is able to put a secret and its rules into a session')
        session_id = joined_session['session_id']
        payload = {
            'session': {
                'secret': {
                    'value': 'my awesome secret',
                }
            },
            'client_alias': self.master_alias,
            'auth': self._masterkey
        }
        response = self.client.put('/split/%s' % session_id, data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][1]['auth']))
        expected_response = {
            'session': {
                'ttl': 600,
                'alias': 'the session alias',
                'secret': {
                    'quorum': 3,
                    'shares': 5,
                    'sha256': '6e1f1d4f6b6c900f3fb72466bbec4a3c7c049fc845a8751a5374227091c1f252',
                    'secret': 'my awesome secret',
                    'protocol': 'fxc1'
                },
                'users': [
                    {
                        'auth': self._masterkey,
                        'alias': self.master_alias,
                        'role': 'master',
                        'shareholder': False
                    },
                    {
                        'auth': response.json['session']['users'][1]['auth'],
                        'alias': 'a shareholder',
                        'role': 'user',
                        'share': 'cafe01'
                    }
                ]
            },
            'session_id': session_id
        }
        self.assertEqual(expected_response, response.json)
        self.assertTrue(control.fxc_web_api_service.split.called)
        self.assertEqual(shares[0].user, response.json['session']['users'][1]['auth'])
        return response.json

    def test_user_get_session_with_secret(self):
        session_with_secret = self.test_master_put_secret_on_joined_session()
        print('SplitSession: a user is able to see the hash of the secret presented by the master')
        session_id = session_with_secret['session_id']
        user_key = session_with_secret['session']['users'][1]['auth']
        response = self.client.get('/split/%s?auth=%s' % (session_id, user_key))
        self.assert200(response)
        expected_response = {
            'session_id': session_id,
            'session': {
                'ttl': 600,
                'alias': 'the session alias',
                'secret': {
                    'quorum': 3,
                    'shares': 5,
                    'sha256': '6e1f1d4f6b6c900f3fb72466bbec4a3c7c049fc845a8751a5374227091c1f252',
                    'protocol': 'fxc1'
                },
                'users': [
                    {
                        'alias': 'the session master',
                        'role': 'master',
                        'shareholder': False
                    },
                    {
                        'auth': user_key,
                        'alias': 'a shareholder',
                        'role': 'user',
                        'shareholder': True
                    }
                ]
            }
        }
        self.assertEqual(expected_response, response.json)
        return response.json

"""
    secret cannot be re-declared
    
    def test_master_fail_to_put_a_secret(self):
        joined_session = self.test_join_session()
        print('SplitSession: a master fail to put a secret where shares are less than quorum')
        session_id = joined_session['session_id']
        payload = {
            'session': {
                'secret': {
                    'secret': 'my awesome secret',
                }
            },
            'client_alias': self.master_alias,
            'auth': self._masterkey
        }
        response = self.client.put('/split/%s' % session_id, data=json.dumps(payload))
        self.assert400(response)
        print('SplitSession: a master fail to put an empty secret')
        payload = {
            'session': {
                'secret': {
                    'secret': None,
                    'shares': 5,
                    'quorum': 3
                }
            },
            'client_alias': self.master_alias,
            'auth': self._masterkey
        }
        response = self.client.put('/split/%s' % session_id, data=json.dumps(payload))
        self.assert400(response)
"""