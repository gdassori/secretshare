import uuid

from pycomb.exceptions import PyCombValidationError

from secretshare.blueprints import combinators
from unittest import TestCase


class TestCombinators(TestCase):
    def setUp(self):
        self._valid_create = {
                "user_alias": "the session master",
                "session_alias": "the session alias"
             }

    def test_create_session_combinator(self):
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