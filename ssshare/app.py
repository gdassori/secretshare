from flask import Flask, Response
from pycomb.exceptions import PyCombValidationError
from ssshare import settings, exceptions
from ssshare.blueprints.split import bp as split_bp
from ssshare.blueprints.combine import bp as combine_bp

app = Flask(__name__)

app.config.update(
    DEBUG=settings.DEBUG,
    SECRET_KEY=settings.FLASK_SECRET_KEY
)

app.register_blueprint(split_bp, url_prefix='/split')
app.register_blueprint(combine_bp, url_prefix='/combine')


@app.errorhandler(exceptions.WrongParametersException)
def wrong_parameters_error(_):
    return Response(status=400, response='arguments')


@app.errorhandler(PyCombValidationError)
def validation_error(_):
    return Response(status=400, response='values')


@app.errorhandler(exceptions.ObjectDeniedException)
def domain_object_request_not_authorized(_):
    return Response(status=401)


@app.errorhandler(exceptions.DomainObjectNotFoundException)
def domain_object_not_found_error(_):
    return Response(status=404)


@app.errorhandler(exceptions.DomainObjectExpiredException)
def domain_object_expired_error(_):
    return Response(status=410)




if __name__ == '__main__':
    app.run(host=settings.LISTEN_HOSTNAME, port=settings.LISTEN_PORT)