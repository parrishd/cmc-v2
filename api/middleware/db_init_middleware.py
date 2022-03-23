import json

from werkzeug.wrappers import Request, Response


class DBInitMiddleware:

    def __init__(self, app, db):
        self.app = app
        self.db = db

    def __call__(self, environ, start_response):
        print('-- DBInitMiddleware')
        if self.db.connect():
            environ['db'] = self.db
            return self.app(environ, start_response)

        res = Response(
            json.dumps({'error': 'DB connection failed'}),
            mimetype='application/json',
            status=500
        )
        return res(environ, start_response)



