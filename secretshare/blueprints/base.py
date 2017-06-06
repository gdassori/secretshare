import flask
from flask.views import MethodView
from secretshare import exceptions
from secretshare.domain.share.session import ShareSession


bp = flask.Blueprint('session', __name__)


class SessionShareView(MethodView):
    def get(self, session_id):
        print('session_id: {}'.format(session_id))
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
        data = flask.request.json
        if not data:
            raise exceptions.WrongParametersException
        session = ShareSession().store()
        return flask.jsonify(
            {
                "session": session.to_dict()
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