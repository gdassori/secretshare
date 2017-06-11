import flask
from flask.views import MethodView
from ssshare import exceptions
from ssshare.blueprints import validators
from ssshare.domain.split import SplitSession
from ssshare.domain.master import SharedSessionMaster

bp = flask.Blueprint('split', __name__)


class SplitSessionCreateView(MethodView):
    @validators.validate(validators.SplitSessionCreateValidator)
    def post(self, params=None):
        user = SharedSessionMaster.new(
            alias=params['client_alias']
        )
        session = SplitSession.new(
            master=user,
            alias=params['session_alias'],
            policies=params['session_policies']
        ).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": str(session.uuid)
            }
        )


class SplitSessionSharedView(MethodView):
    @validators.validate(validators.SplitSessionGetValidator)
    def get(self, session_id, params=None):
        session = SplitSession.get(session_id, auth=params['auth'])
        if not session:
            raise exceptions.ObjectNotFoundException
        if not session.ttl:
            raise exceptions.ObjectExpiredException
        return flask.jsonify(
            {
                "session": session.to_api(auth=params['auth']),
                "session_id": str(session.uuid)
            }
        )

    @validators.validate(validators.SplitSessionEditValidator)
    def put(self, session_id, params=None):
        session = SplitSession.get(session_id)
        if not session:
            raise exceptions.ObjectNotFoundException
        user = params.get('auth') and session.get_user(params['auth'], alias=str(params['client_alias'])) \
               or session.join(params['client_alias'])
        if not user:
            raise exceptions.ObjectDeniedException
        if user.is_master:
            session.secret.edit_secret(dict(params['session']['secret']))
        session.update()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid and str(user.uuid)),
                "session_id": str(session.uuid)
            }
        )

bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'POST'],
    view_func=SplitSessionSharedView.as_view('split_session_shared')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SplitSessionCreateView.as_view('split_session_create'))