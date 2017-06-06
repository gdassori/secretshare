import functools
from pycomb import combinators
from uuid import UUID
import flask
from pycomb.exceptions import PyCombValidationError

from secretshare import exceptions


def is_uuid(value):
    try:
        return UUID(value)
    except (TypeError, ValueError):
        print('not uuid: {}'.format(value))
        return


def validate(validation_class, silent=True):
    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*a, **kw):
            p = {k:v for k, v in flask.request.values.items()}
            if silent:
                try:
                    validation_class(p)
                except PyCombValidationError:
                    raise exceptions.WrongParametersException
            else:
                validation_class(p)
            return fun(*a, **kw)
        return wrapper
    return decorator


UUIDCombinator = combinators.subtype(
    combinators.String,
    is_uuid
)

ShareSessionCreateCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
        "session_alias": combinators.String
    }
)

ShareSessionJoinCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
        "session_key": UUIDCombinator
    }
)