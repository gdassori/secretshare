import uuid
import functools
import flask
from flask import json
from pycomb import combinators as validators
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

SplitProtocolValidator = validators.subtype(
    validators.String,
    lambda x: x in ['fxc1']
)

SplitSessionValidator = validators.struct(
    {
        "secret": validators.struct(
            {
                "value": validators.String,
                "protocol": validators.maybe(SplitProtocolValidator),
            }
        )
    }
)

SplitSessionCreateValidator = validators.struct(
    {
        "client_alias": validators.String,
        "session_alias": validators.String,
        "session_policies": validators.struct(
            {
                "shares": validators.Int,
                "quorum": validators.Int
            }
        )
    },
    strict=True
)

SplitSessionGetValidator = validators.struct(
    {
        "client_alias": validators.String,
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

CombineSessionCreateValidator = validators.struct(
    {
        "client_alias": validators.String,
        "session_alias": validators.String,
        "session_type": validators.String,
        "session_id": validators.maybe(UUIDValidator),
        "session_policies": validators.struct(
            {
                "quorum": validators.Int,
                "shares": validators.Int
            }
        )
    },
    strict=True
)

CombineSessionGetValidator = validators.struct(
    {
        "client_alias": validators.String,
        "auth": UUIDValidator
    },
    strict=True
)

CombineSessionJoinValidator = validators.struct(
    {
        "client_alias": validators.String,
    },
    strict=True
)

CombineSessionPutShareValidator = validators.struct(
    {
        "client_alias": validators.String,
        "auth": validators.maybe(validators.String),
        "share": validators.String
    },
    strict=True
)

CombineSessionMasterEditValidator = validators.struct(
    {
        "client_alias": validators.String,
        "auth": validators.String,
        "session_alias": validators.String,
        "session_type": validators.String,
    },
    strict=True
)

CombineSessionEditValidator = validators.union(
    CombineSessionJoinValidator,
    CombineSessionPutShareValidator,
    CombineSessionMasterEditValidator
)