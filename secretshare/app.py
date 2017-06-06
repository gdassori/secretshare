from flask import Flask, Response
from secretshare import settings, exceptions
from secretshare.blueprints.base import bp as base_bp

app = Flask(__name__)

app.config.update(
    DEBUG=settings.DEBUG,
    SECRET_KEY=settings.FLASK_SECRET_KEY
)

app.register_blueprint(base_bp, url_prefix='/session')


@app.errorhandler(exceptions.WrongParametersException)
def wrong_parameters_error(_):
    return Response(status=400)


@app.errorhandler(exceptions.DomainObjectNotFoundException)
def domain_object_not_found_error(_):
    return Response(status=404)


if __name__ == '__main__':
    app.run(host=settings.LISTEN_HOSTNAME, port=settings.LISTEN_PORT)