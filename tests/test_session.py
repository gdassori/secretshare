from tests import MainTestClass
import uuid


class TestSession(MainTestClass):
    def setUp(self):
        print('Initialized TestSession')
        self.masterkey = str(uuid.uuid4())
        self.alias = 'the session master'

    def test_create_session(self):
        print('TestSession: Creating session')
        payload = {
            "masterkey": self.masterkey,
            "alias": self.alias
        }
        response = self.client.post('/session', data=payload)
        self.assert200(response)
        self.assertEqual(
            {'session':
                 {'secret': None,
                  'owner': 'the session master',
                  'users': [],
                  'secret_sha256': None}
             },
            response.json
        )