import json
from datetime import datetime, timezone
from werkzeug.wrappers import Request, Response
import paseto
from paseto.keys.symmetric_key import SymmetricKey
from paseto.protocols.v4 import ProtocolVersion4
from paseto.exceptions import PasetoException


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
        if auth_header is None:
            res = Response(
                json.dumps({'error': 'Auth token missing'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        try:
            sk = SymmetricKey(key_material=self.auth_key.encode(), protocol=ProtocolVersion4)
            token = paseto.parse(
                key=sk,
                purpose='local',
                token=auth_header,
            )
            print(token)
        except ValueError:
            res = Response(
                json.dumps({'error': 'Auth token decode failed'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)
        except PasetoException:
            res = Response(
                json.dumps({'error': 'Auth token exception'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # validate required fields are in token
        token_data = token['message']
        if 'id' not in token_data or 'exp' not in token_data or 'role' not in token_data:
            res = Response(
                json.dumps({'error': 'Auth token invalid'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # verify token has not expired
        exp = datetime.fromisoformat(token_data['exp'])
        if datetime.now(timezone.utc) > exp:
            res = Response(
                json.dumps({'error': 'Auth token expired'}),
                mimetype='application/json',
                status=400
            )
            return res(environ, start_response)

        # success call
        environ['user_id'] = token_data['id']
        environ['role'] = token_data['role']
        environ['auth_key'] = self.auth_key
        return self.app(environ, start_response)
