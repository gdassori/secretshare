from tests import MainTestClass
from ssshare.blueprints.combinators import is_uuid


class TestSession(MainTestClass):
    def setUp(self):
        print('Initialized TestSession')
        self.master_alias = 'the session master'
        self.session_alias = 'the session alias'

    def test_create_session(self):
        print('TestSession: Creating session')
        payload = {
            "user_alias": self.master_alias,
            "session_alias": self.session_alias
        }
        response = self.client.post('/session', data=payload)
        self.assert200(response)
        session_id = is_uuid(response.json['session_id'])
        self.assertEqual(
            {
                'session': {
                    'secret': None,
                    'users': [
                        {
                            'alias': 'the session master',
                            'role': 'master'
                        }
                    ],
                    'secret_sha256': None,
                    'ttl': 600,
                    'alias': 'the session alias'
                },
                'session_id': session_id,
             },
            response.json
        )