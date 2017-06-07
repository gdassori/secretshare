import uuid

from tests import MainTestClass
from ssshare.blueprints.combinators import is_uuid


class TestSession(MainTestClass):
    def setUp(self):
        print('Initialized TestSession')
        self.master_alias = 'the session master'
        self.session_alias = 'the session alias'

    def test_create_session(self):
        print('TestSession: create session')
        payload = {
            "user_alias": self.master_alias,
            "session_alias": self.session_alias
        }
        response = self.client.post('/session', data=payload)
        self.assert200(response)
        self.assertTrue(is_uuid(response.json['session_id']))
        self.assertTrue(is_uuid(response.json['session']['users'][0]['key']))
        self.assertEqual(
            {
                'session': {
                    'secret': None,
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master',
                            'key': response.json['session']['users'][0]['key']
                        }
                    ],
                    'secret_sha256': None,
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
        print('TestSession: get session')
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['key']
        response = self.client.get('/session/%s?auth=%s' % (session_id, user_key))
        self.assertEqual(response.json, jsonresponse)

    def test_get_session_404_no_session(self):
        print('TestSession: get a non existent session')
        response = self.client.get('/session/%s?auth=%s' % (str(uuid.uuid4()), str(uuid.uuid4())))
        self.assert404(response)

    def test_get_session_401_no_auth(self):
        jsonresponse = self.test_create_session()
        print('TestSession: get session without auth rights')
        session_id, _ = jsonresponse['session_id'], jsonresponse['session']['users'][0]['key']
        response = self.client.get('/session/%s?auth=%s' % (session_id, str(uuid.uuid4())))
        self.assert401(response)

    def test_get_session_410_expired(self):
        jsonresponse = self.test_create_session()
        print('TestSession: get an expired session')
        session_id, user_key = jsonresponse['session_id'], jsonresponse['session']['users'][0]['key']

        from ssshare.ioc import secret_share_repository
        data = secret_share_repository.get_session(session_id)
        data['last_update'] = 1
        secret_share_repository.update_session(data)

        response = self.client.get('/session/%s?auth=%s' % (session_id, user_key))
        self.assertEqual(response.status_code, 410)