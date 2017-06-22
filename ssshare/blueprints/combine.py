import flask
from flask.views import MethodView
from ssshare import exceptions
from ssshare.blueprints import validators
from ssshare.domain.combine import CombineSession
from ssshare.domain.master import SharedSessionMaster
from ssshare.domain.secret import Share, SharedSessionSecret

bp = flask.Blueprint('combine', __name__)


class CombineSessionCreateView(MethodView):
    @validators.validate(validators.CombineSessionCreateValidator)
    def post(self, params=None):
        user = SharedSessionMaster.new(
            alias=params['client_alias']
        )
        secret = SharedSessionSecret.new(
            shares=params['session_policies']['shares'],
            quorum=params['session_policies']['quorum'],
            protocol=params['session_policies']['protocol']
        )
        session = CombineSession.new(
            session_id=params.get('session_id'),
            master=user,
            alias=params['session_alias'],
            session_type=params['session_type'],
            secret=secret
        ).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": str(session.uuid)
            }
        )


class CombineSessionSharedView(MethodView):
    @validators.validate(validators.CombineSessionGetValidator)
    def get(self, session_id, params=None):
        session = CombineSession.get(session_id, auth=params['auth'])
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

    @validators.validate(validators.CombineSessionEditValidator)
    def put(self, session_id, params=None):
        session = CombineSession.get(session_id)
        if not session:
            raise exceptions.ObjectNotFoundException
        user = params.get('auth') and session.get_user(params['auth'], alias=str(params['client_alias'])) \
               or session.join(params['client_alias'])
        if not user:
            raise exceptions.ObjectDeniedException
        user.session = session
        if params.get('share'):
            session.secret.add_share(Share(params['share'], str(user.uuid)))
        session.update()
        return flask.jsonify(
            {
                "session": session.to_api(auth=str(user.uuid)),
                "session_id": str(session.uuid)
            }
        )


bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'POST'],
    view_func=CombineSessionSharedView.as_view('combine_session_shared')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=CombineSessionCreateView.as_view('combine_session_create'))