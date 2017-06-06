from unittest import TestCase
from pycomb.exceptions import PyCombValidationError
from secretshare.blueprints import combinators


class TestCombinators(TestCase):
    def setUp(self):
        print('Initialized TestCombinators')
        self._valid_create = {
                "user_alias": "the session master",
                "session_alias": "the session alias"
             }

    def test_create_session_combinator(self):
        print('TestCombinators: ShareSessionCreateCombinator')
        combinators.ShareSessionCreateCombinator(self._valid_create)
        with self.assertRaises(PyCombValidationError):
            invalid = {k:v for k, v in self._valid_create.items()}
            invalid['user_alias'] = None
            combinators.ShareSessionCreateCombinator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['user_alias'] = 'not_uuid'
            combinators.ShareSessionCreateCombinator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['user_alias'] = 'not_uuid'
            combinators.ShareSessionCreateCombinator(invalid)

            invalid = {k: v for k, v in self._valid_create.items() if k != 'user_alias'}
            combinators.ShareSessionCreateCombinator(invalid)

            invalid = {k: v for k, v in self._valid_create.items()}
            invalid['moar'] = 'values'
            combinators.ShareSessionCreateCombinator(invalid)