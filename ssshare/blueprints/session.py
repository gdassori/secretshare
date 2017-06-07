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
        user = session.join(flask.request.values['user_alias'])
        session.update()
        return flask.jsonify(
            {
                "session": session.to_api(auth=str(user.uuid)),
                "session_id": str(session.uuid)
            }
        )

    def delete(self, session_id):
        data = flask.request.json
        if not all([data, session_id]):
            raise exceptions.WrongParametersException
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        session.delete()
        return flask.jsonify(
            {
                "success": True,
                "session_id": str(session.uuid)
            }
        )


bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'DELETE', 'POST'],
    view_func=SessionShareView.as_view('get_or_edit_session')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SessionCreateView.as_view('create_session'))