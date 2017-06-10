import uuid
import functools
import flask
from flask import json
from pycomb import combinators as validators  # avoid combine feature\combinators misunderstanding
from pycomb.exceptions import PyCombValidationError
from ssshare import exceptions, settings


def is_uuid(value):
    try:
        assert value
        return uuid.UUID(value)
    except (TypeError, ValueError, AssertionError):
        return


def validate(validation_class, silent=not settings.DEBUG):
    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*a, **kw):
            if flask.request.method == 'GET':
                p = {k: v for k, v in flask.request.values and flask.request.values.items() or {}}
            else:
                try:
                    p = flask.request.data and json.loads(flask.request.data.decode())
                except Exception:
                    raise exceptions.WrongParametersException
            if silent:
                try:
                    validation_class(p)
                except PyCombValidationError:
                    raise exceptions.WrongParametersException
            else:
                validation_class(p)
            return fun(*a, params=p, **kw)
        return wrapper
    return decorator


UUIDValidator = validators.subtype(
    validators.String,
    is_uuid
)

SplitSessionDataValidator = validators.struct(
    {
        "secret": validators.struct(
            {
                "secret": validators.String,
                "shares": validators.Int,
                "quorum": validators.Int
            }
        )
    }
)

SplitSessionValidator = validators.subtype(
    SplitSessionDataValidator,
    lambda x: x['secret']['shares'] >= x['secret']['quorum']
)



SplitSessionCreateValidator = validators.struct(
    {
        "client_alias": validators.String,
        "session_alias": validators.String
    },
    strict=True
)

SplitSessionGetValidator = validators.struct(
    {
        "auth": UUIDValidator
    },
    strict=True
)


SplitSessionJoinValidator = validators.struct(
    {
        "client_alias": validators.String,
    },
    strict=True
)

SplitSessionMasterEditValidator = validators.struct(
    {
        "client_alias": validators.String,
        "auth": validators.String,
        "session": SplitSessionValidator
    },
    strict=True
)

SplitSessionEditValidator = validators.union(
    SplitSessionJoinValidator,
    SplitSessionMasterEditValidator
)

CombineSessionCreateValidator = NotImplementedError
CombineSessionGetValidator = NotImplementedError
CombineSessionJoinValidator = NotImplementedError
CombineSessionEditValidator = NotImplementedError