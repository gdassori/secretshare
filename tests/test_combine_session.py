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
            "session_type": "transparent",
            "session_policies": {
                "shares": 5,
                "quorum": 3,
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
                    'secret': None,
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master',
                            'auth': self._masterkey,
                            'shareholder': False
                        }
                    ],
                    'secret_sha256': None,
                    'ttl': response.json['session']['ttl'],
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
        data = secret_share_repository.get_session(session_id)
        data['last_update'] = 1 # epoch based, last update in the shiny 70s
        secret_share_repository.update_session(data)
        print('CombineSession: someone request an expired session')
        response = self.client.get('/combine/%s?auth=%s&client_alias=%s' % (session_id, user_key, 'client_alias'))
        self.assertEqual(response.status_code, 410)

    def test_put_share(self):
        jsonresponse = self.test_create_session()
        alias, session_id, user_key = jsonresponse['session']['users'][0]['alias'], \
                                      jsonresponse['session_id'], \
                                      jsonresponse['session']['users'][0]['auth']
        payload = {
            'client_alias': 'peter',
            'share': 'thebirdistheword'
        }
        subscribe1 = self.client.put('/combine/%s' % session_id, data=json.dumps(payload))
        self.assert200(subscribe1)
        self.assertEqual(subscribe1.json['session']['users'][1]['alias'], 'peter')
        self.assertEqual(subscribe1.json['session']['users'][1]['share'], 'thebirdistheword')
        print('CombineSession: a client join a combine session and present its share')
        return subscribe1