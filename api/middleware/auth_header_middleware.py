import json
from datetime import datetime
from werkzeug.wrappers import Request, Response
from paseto.protocol.version2 import decrypt


class AuthHeaderMiddleware:

    def __init__(self, app, auth_key):
        self.app = app
        self.auth_key = auth_key
        self.skipper = [
            '/auth/login'
        ]

    def __call__(self, environ, start_response):
        request = Request(environ)
        print(f'-- AuthHeaderMiddleware: {request.path}')

        # check if the path should be skipped
        if request.path in self.skipper:
            environ['auth_key'] = self.auth_key
            return self.app(environ, start_response)

        # fetch and decode the authorization token
        auth_header = request.headers.get('Authorization')
        try:
            token = decrypt(auth_header.encode(), self.auth_key.encode())
        except ValueError:
            res = Response(
                json.dumps({'error': 'Auth token decode failed'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # validate required fields are in token
        token_data = json.loads(token)
        if 'id' not in token_data or 'exp' not in token_data:
            res = Response(
                json.dumps({'error': 'Auth token invalid'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # verify token has not expired
        exp = datetime.strptime(token_data['exp'], "%Y-%m-%dT%H:%M:%S.%f")
        if datetime.now() > exp:
            res = Response(
                json.dumps({'error': 'Auth token expired'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # success call
        environ['user_id'] = token_data['id']
        environ['auth_key'] = self.auth_key
        return self.app(environ, start_response)

        # res = Response(
        #     json.dumps({'error': 'DB connection failed'}),
        #     mimetype='application/json',
        #     status=500
        # )
        # return res(environ, start_response)
