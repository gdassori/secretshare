import flask
from flask.views import MethodView
from secretshare import exceptions, settings
from secretshare.blueprints import combinators
from secretshare.domain.master import ShareSessionMaster
from secretshare.domain.session import ShareSession

bp = flask.Blueprint('session', __name__)


class SessionShareView(MethodView):
    @combinators.validate(combinators.ShareSessionGetCombinator,
                          silent=not settings.DEBUG)
    def get(self, session_id):
        if not session_id:
            raise exceptions.WrongParametersException
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        return flask.jsonify(
            {
                "session": session.to_dict()
            }
        )

    def put(self, session_id):
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        return flask.jsonify(
            {
                "session": session.to_dict()
            }
        )

    @combinators.validate(combinators.ShareSessionCreateCombinator, silent=not settings.DEBUG)
    def post(self):
        params = flask.request.values
        user = ShareSessionMaster.new(alias=params['user_alias'])
        session = ShareSession.new(master=user, alias=params['session_alias']).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": session.uuid
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
                "session_id": session_id
            }
        )


bp.add_url_rule(
    '/<string:session_id>',
    methods=['GET', 'PUT', 'DELETE'],
    view_func=SessionShareView.as_view('get_or_edit_session')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SessionShareView.as_view('create_session'))