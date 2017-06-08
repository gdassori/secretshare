import flask
from flask.views import MethodView
from ssshare import exceptions, settings
from ssshare.blueprints import combinators
from ssshare.domain.master import ShareSessionMaster
from ssshare.domain.session import ShareSession

bp = flask.Blueprint('session', __name__)


class SessionCreateView(MethodView):
    @combinators.validate(combinators.ShareSessionCreateCombinator, silent=not settings.DEBUG)
    def post(self):
        user = ShareSessionMaster.new(alias=flask.request.values['user_alias'])
        session = ShareSession.new(master=user, alias=flask.request.values['session_alias']).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": str(session.uuid)
            }
        )


class SessionShareView(MethodView):
    @combinators.validate(combinators.ShareSessionGetCombinator, silent=not settings.DEBUG)
    def get(self, session_id):
        session = ShareSession.get(session_id, auth=flask.request.values['auth'])
        if not session:
            raise exceptions.DomainObjectNotFoundException
        if not session.ttl:
            raise exceptions.DomainObjectExpiredException
        return flask.jsonify(
            {
                "session": session.to_api(auth=flask.request.values['auth']),
                "session_id": str(session.uuid)
            }
        )

    @combinators.validate(combinators.ShareSessionJoinCombinator, silent=not settings.DEBUG)
    def put(self, session_id):
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        user = not flask.request.values.get('user_auth') and session.join(flask.request.values['user_alias']) or \
            session.get_user(flask.request.values['user_auth'], alias=str(flask.request.values['user_alias']))
        if not user:
            raise exceptions.ObjectDeniedException
        if user.is_master:
            session.set_from_payload(dict(flask.request.values)).is_changed and session.update()
        return flask.jsonify(
            {
                "session": session.to_api(auth=str(user.uuid)),
                "session_id": str(session.uuid)
            }
        )

bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'POST'],
    view_func=SessionShareView.as_view('get_or_edit_session')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SessionCreateView.as_view('create_session'))