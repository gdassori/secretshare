import functools
from uuid import UUID
import flask
from pycomb import combinators
from pycomb.exceptions import PyCombValidationError
from ssshare import exceptions


def is_uuid(value):
    try:
        assert value
        return UUID(value)
    except (TypeError, ValueError, AssertionError):
        return


def validate(validation_class, silent=True):
    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*a, **kw):
            p = {k:v for k, v in flask.request.values and flask.request.values.items() or {}}
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

ShareSessionGetCombinator = combinators.struct(
    {
        "auth": UUIDCombinator
    }
)

ShareSessionJoinCombinator = combinators.struct(
    {
        "user_alias": combinators.String,
    }
)