from secretshare.blueprints.combinators import is_uuid
from tests import MainTestClass
import uuid


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
            {'session':
                 {'secret': None,
                  'owner': 'the session master',
                  'users': [],
                  'secret_sha256': None},
             'session_id': session_id
             },
            response.json
        )