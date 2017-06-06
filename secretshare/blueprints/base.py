import flask
from flask.views import MethodView
from secretshare import exceptions
from secretshare.domain.session.master import ShareSessionMaster
from secretshare.domain.session.session import ShareSession


bp = flask.Blueprint('session', __name__)


class SessionShareView(MethodView):
    def _parse_post_request(self, values):
        if not values or not values.get('masterkey') or not values.get('alias'):
            raise exceptions.WrongParametersException
        return values

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
        data = flask.request.json
        if not all([data, session_id]):
            raise exceptions.WrongParametersException
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        return flask.jsonify(
            {
                "session": session.to_dict()
            }
        )

    def post(self):
        params = self._parse_post_request(flask.request.values)
        master = ShareSessionMaster(masterkey=params['masterkey'], alias=params['alias'])
        session = ShareSession(master=master).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=params['masterkey'])
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