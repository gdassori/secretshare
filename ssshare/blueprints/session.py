import flask
from flask.views import MethodView
from ssshare import exceptions, settings
from ssshare.blueprints import combinators
from ssshare.domain.master import ShareSessionMaster
from ssshare.domain.session import ShareSession

bp = flask.Blueprint('session', __name__)


class SessionCreateView(MethodView):
    @combinators.validate(combinators.ShareSessionCreateCombinator)
    def post(self, params=None):
        user = ShareSessionMaster.new(alias=params['user_alias'])
        session = ShareSession.new(master=user, alias=params['session_alias']).store()
        return flask.jsonify(
            {
                "session": session.to_api(auth=user.uuid),
                "session_id": str(session.uuid)
            }
        )


class SessionShareView(MethodView):
    @combinators.validate(combinators.ShareSessionGetCombinator)
    def get(self, session_id, params=None):
        session = ShareSession.get(session_id, auth=params['auth'])
        if not session:
            raise exceptions.DomainObjectNotFoundException
        if not session.ttl:
            raise exceptions.DomainObjectExpiredException
        return flask.jsonify(
            {
                "session": session.to_api(auth=params['auth']),
                "session_id": str(session.uuid)
            }
        )

    @combinators.validate(combinators.ShareSessionEditCombinator)
    def put(self, session_id, params=None):
        session = ShareSession.get(session_id)
        if not session:
            raise exceptions.DomainObjectNotFoundException
        if params.get('auth'):
            user = session.get_user(params['auth'], alias=str(params['user_alias']))
        else:
            user = session.join(params['user_alias'])
        if not user:
            raise exceptions.ObjectDeniedException
        print('user is {}'.format(user.to_dict()))
        if user.is_master:
            session.set_from_payload(dict(params))
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
    view_func=SessionShareView.as_view('get_or_edit_session')
)

bp.add_url_rule(
    '',
    methods=['POST'],
    view_func=SessionCreateView.as_view('create_session'))