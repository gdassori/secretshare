import flask
from flask.views import MethodView
from ssshare import exceptions
from ssshare.blueprints import validators
from ssshare.domain.combine_session import CombineSession
from ssshare.domain.master import SharedSessionMaster

bp = flask.Blueprint('combine', __name__)


class CombineSessionCreateView(MethodView):
    @validators.validate(validators.CombineSessionCreateValidator)
    def post(self, params=None):
        user = SharedSessionMaster.new(alias=params['user_alias'])
        session = CombineSession.new(
            master=user,
            alias=params['session_alias'],
            session_type=params['session_type']
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
            raise exceptions.DomainObjectNotFoundException
        user = params.get('auth') and session.get_user(params['auth'], alias=str(params['user_alias'])) \
               or session.join(params['user_alias'])
        if not user:
            raise exceptions.ObjectDeniedException
        if params.get('share'):
            session.add_share_from_payload(params['share'])
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