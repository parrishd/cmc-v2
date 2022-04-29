import os

from flask import Flask
from .db import DB
from .middleware.db_init_middleware import DBInitMiddleware
from .middleware.db_close_middleware import DBCloseMiddleware
from .middleware.auth_header_middleware import AuthHeaderMiddleware


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'api.sqlite'),
    )

    # print(os.environ)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # get the auth key for token encryption
    auth_key = os.environ.get('VIMS_AUTH_KEY')
    if auth_key is None or auth_key == '' or len(auth_key) != 32:
        raise Exception('auth key is empty')

    # set as os env variables
    dbs = DB(
        app,
        os.environ.get('VIMS_DB_HOST'),
        os.environ.get('VIMS_DB_DATABASE'),
        os.environ.get('VIMS_DB_USER'),
        os.environ.get('VIMS_DB_PASSWORD')
    )

    # AfterResponse(app)
    app.wsgi_app = DBCloseMiddleware(app.wsgi_app)
    app.wsgi_app = DBInitMiddleware(app.wsgi_app, dbs)
    app.wsgi_app = AuthHeaderMiddleware(app.wsgi_app, auth_key)

    from .service import auth
    auth.login(app)
    auth.test(app)

    from .service.integration import benthic as benthic_integration
    benthic_integration.BenthicIntegrationService(app, roles=['Admin', 'Coordinator'])

    from .service.integration import waterquality as waterquality_integration
    waterquality_integration.WaterQualityIntegrationService(app, roles=[])

    # from .service.integration.waterquality import waterquality
    # waterquality.service(app, [])  # todo: pass service roles

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    return app
