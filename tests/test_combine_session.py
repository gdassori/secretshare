import json
import uuid
from tests import MainTestClass
from ssshare.blueprints.validators import is_uuid


class TestCombineSession(MainTestClass):
    def setUp(self):
        self.master_alias = 'the session master'
        self.session_alias = 'the session alias'

    def test_create_session(self):
        print('CombineSession: a master create a session')
        payload = {
            "client_alias": self.master_alias,
            "session_alias": self.session_alias,
            "session_type": "transparent"
        }
        response = self.client.post('/combine', data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][0]['auth']))
        self._masterkey = response.json['session']['users'][0]['auth']
        self.assertEqual(
            {
                'session': {
                    'secret': None,
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master',
                            'auth': self._masterkey
                        }
                    ],
                    'secret_sha256': None,
                    'ttl': 600,
                    'alias': 'the session alias',
                    'type': 'transparent'
                },
                'session_id': response.json['session_id']
             },
            response.json
        )
        return response.json

    def test_get_session(self):
        jsonresponse = self.test_create_session()
        print('CombineSession: a master get a created session')
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']
        response = self.client.get('/combine/%s?auth=%s' % (session_id, user_key))
        self.assertEqual(response.json, jsonresponse)

    def test_get_session_404_no_session(self):
        print('CombineSession: a get happen on a non existent session')
        response = self.client.get('/combine/%s?auth=%s' % (str(uuid.uuid4()), str(uuid.uuid4())))
        self.assert404(response)

    def test_get_session_401_no_auth(self):
        jsonresponse = self.test_create_session()
        print('CombineSession: a get happen on a good session, but without rights')
        session_id, _ = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']
        response = self.client.get('/combine/%s?auth=%s' % (session_id, str(uuid.uuid4())))
        self.assert401(response)

    def test_get_session_410_expired(self):
        jsonresponse = self.test_create_session()
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['auth']

        # force session expiration
        print('CombineSession: the session expires')
        from ssshare.control import secret_share_repository
        data = secret_share_repository.get_session(session_id)
        data['last_update'] = 1 # epoch based, last update in the shiny 70s
        secret_share_repository.update_session(data)
        print('CombineSession: someone request an expired session')
        response = self.client.get('/combine/%s?auth=%s' % (session_id, user_key))
        self.assertEqual(response.status_code, 410)

'''
    def test_join_session(self):
        created_session = self.test_create_session()
        print('CombineSession: a user join a valid created session')
        payload = {
            'user_alias' : 'a shareholder'
        }
        response = self.client.put('/combine/%s' % created_session['session_id'], data=json.dumps(payload))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][1]['auth']))
        session_id, user_key = response.json['session_id'], response.json['session']['users'][1]['auth']
        expected_response = {
            'session': {
                'users': [
                    {'role': 'master', 'alias': 'the session master'},
                    {'role': 'user', 'auth': user_key, 'alias': 'a shareholder'}
                ],
                'ttl': 600,
                'secret_sha256': None,
                'alias': 'the session alias'
            },
            'session_id': session_id
        }
        self.assertEqual(expected_response, response.json)
        return response.json

    def test_master_get_user_joined_session(self):
        joined_session = self.test_join_session()
        print('CombineSession: after a join, the master get the session and see the joined user')
        response = self.client.get('/split/%s?auth=%s' % (joined_session['session_id'], self._masterkey))
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][1]['auth']))

    def test_user_join_session_401_twice_join(self):
        joined_session = self.test_join_session()
        print('CombineSession: a user is unable to join a session twice \ user alias is unique')
        payload = {
            'user_alias' : 'a shareholder'
        }
        response = self.client.put('/split/%s' % joined_session['session_id'], data=json.dumps(payload))
        self.assert401(response)

    def test_master_put_secret_on_joined_session(self):
        joined_session = self.test_join_session()
        print('CombineSession: a master is able to put a secret and its rules into a session')
        session_id = joined_session['session_id']
        payload = {
            'session': {
                'secret': {
                    'secret': 'my awesome secret',
                    'shares': 3,
                    'quorum': 2
                }
            },
            'user_alias': self.master_alias,
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
                'secret': 'my awesome secret',
                'secret_sha256': '6e1f1d4f6b6c900f3fb72466bbec4a3c7c049fc845a8751a5374227091c1f252',
                'users': [
                    {
                        'auth': self._masterkey,
                        'alias': self.master_alias,
                        'role': 'master'},
                    {
                        'auth': response.json['session']['users'][1]['auth'],
                        'alias': 'a shareholder',
                        'role': 'user'
                    }
                ]
            },
            'session_id': session_id
        }
        self.assertEqual(expected_response, response.json)
        return response.json

    def test_user_get_session_with_secret(self):
        session_with_secret = self.test_master_put_secret_on_joined_session()
        print('CombineSession: a user is able to see the hash of the secret presented by the master')
        session_id = session_with_secret['session_id']
        user_key = session_with_secret['session']['users'][1]['auth']
        response = self.client.get('/split/%s?auth=%s' % (session_id, user_key))
        self.assert200(response)
        expected_response = {
            'session_id': session_id,
            'session': {
                'secret_sha256': '6e1f1d4f6b6c900f3fb72466bbec4a3c7c049fc845a8751a5374227091c1f252',
                'ttl': 600,
                'alias': 'the session alias',
                'users': [
                    {
                        'alias': 'the session master',
                        'role': 'master'
                    },
                    {
                        'auth': user_key,
                        'alias': 'a shareholder',
                        'role': 'user'
                    }
                ]
            }
        }
        self.assertEqual(expected_response, response.json)

    def test_master_fail_to_put_a_secret(self):
        """
        shares < quorum,
        secret == None
        """
        joined_session = self.test_join_session()
        print('CombineSession: a master fail to put a secret where shares are less than quorum')
        session_id = joined_session['session_id']
        payload = {
            'session': {
                'secret': {
                    'secret': 'my awesome secret',
                    'shares': 2,
                    'quorum': 3
                }
            },
            'user_alias': self.master_alias,
            'auth': self._masterkey
        }
        response = self.client.put('/split/%s' % session_id, data=json.dumps(payload))
        self.assert400(response)
        print('CombineSession: a master fail to put an empty secret')
        payload = {
            'session': {
                'secret': {
                    'secret': None,
                    'shares': 5,
                    'quorum': 3
                }
            },
            'user_alias': self.master_alias,
            'auth': self._masterkey
        }
        response = self.client.put('/split/%s' % session_id, data=json.dumps(payload))
        self.assert400(response)
'''