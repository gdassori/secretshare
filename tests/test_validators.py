from unittest import TestCase
from pycomb.exceptions import PyCombValidationError
from ssshare.blueprints import validators


class TestValidators(TestCase):
    def setUp(self):
        print('Initialized TestValidators')
        self._valid_create = {
                "client_alias": "the session master",
                "session_alias": "the session alias",
                "session_policies": {
                    "quorum": 3,
                    "shares": 5
                }
             }

    def test_create_session_Validator(self):
        print('Validators: ShareSessionCreateValidator')
        validators.SplitSessionCreateValidator(self._valid_create)
        with self.assertRaises(PyCombValidationError):
            invalid = {k:v for k, v in self._valid_create.items()}
            invalid['user_alias'] = None
            validators.SplitSessionCreateValidator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['user_alias'] = 'not_uuid'
            validators.SplitSessionCreateValidator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['user_alias'] = 'not_uuid'
            validators.SplitSessionCreateValidator(invalid)

            invalid = {k: v for k, v in self._valid_create.items() if k != 'user_alias'}
            validators.SplitSessionCreateValidator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['moar'] = 'values'
            validators.SplitSessionCreateValidator(invalid)