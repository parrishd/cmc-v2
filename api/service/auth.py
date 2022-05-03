import json
import base64
import os
import hashlib
import collections
from datetime import datetime, timedelta, timezone
from flask import jsonify, request
# from paseto.protocol.version2 import encrypt
import paseto
from paseto.keys.symmetric_key import SymmetricKey
from paseto.protocols.v4 import ProtocolVersion4
from api.middleware import role_validation
from api.model import flask_user, asp_net_user, asp_net_user_role


class AuthService:
    def __init__(self, app):
        app.route('/auth/login', methods=['POST'])(self.login)
        app.route('/auth/generate', methods=['POST'])(self.generate)

        self.create_roles = ['Admin']
        app.route('/auth/create', methods=['POST'])(self.create)

    @staticmethod
    def login():
        db = request.environ['db']
        auth_key = request.environ['auth_key']
        data = request.json

        # verify user account
        anu = asp_net_user.get_asp_net_user_by(
            db,
            ['Id', 'Status', 'EmailConfirmed'],
            'UserName',
            data['email'])

        if anu is None:
            return jsonify({'error': 'user: not found', 'code': '0x01'}), 404

        # check user status
        if not anu.Status:
            return jsonify({'error': 'user: invalid status', 'code': '0x02'}), 403

        # check email confirmed
        if not anu.EmailConfirmed:
            return jsonify({'error': 'user: email confirmation', 'code': '0x03'}), 403

        # verify user account
        fu = flask_user.get_flask_user_by(
            db,
            ['Id', 'Email', 'PasswordHash'],
            'Id',
            anu.Id)

        if fu is None:
            return jsonify({'error': 'api user: not found', 'code': '0x01'}), 404

        # validate password
        passDecoded = base64.b64decode(fu.PasswordHash)
        salt = passDecoded[:32]  # 32 is the length of the salt
        key = passDecoded[32:]
        passKey = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), salt, 1000000)

        if key != passKey:
            return jsonify({'error': 'invalid authentication', 'code': '0x01'}), 403

        # load roles
        anur = asp_net_user_role.get_asp_net_user_roles_by_uid(db, anu.Id)
        if anur is None:
            return jsonify({'error': 'invalid role set', 'code': '0x01'}), 403

        exp = datetime.now(timezone.utc) + timedelta(seconds=3600)
        token_data = {'id': anu.Id, 'exp': exp.isoformat(), 'role': {'id': anur.RoleId, 'name': anur.Name}}
        sk = SymmetricKey(key_material=auth_key.encode(), protocol=ProtocolVersion4)
        token = paseto.create(
            key=sk,
            purpose='local',
            claims=token_data,
            exp_seconds=3600
        )

        resp = {'token': token, 'exp': exp.isoformat()}
        return jsonify(resp), 200

    @staticmethod
    def generate():
        data = request.json

        if 'password' not in data:
            return jsonify({'error': 'invalid payload', 'code': '0x01'}), 404

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), salt, 1000000)
        salt_key = salt + key
        passEncoded = base64.b64encode(salt_key)

        resp = {'status': 200, 'hash': passEncoded.decode("utf-8")}
        return jsonify(resp), 200

    def create(self):
        # validate roles
        ur = request.environ['roles']
        if not role_validation.validate(self.create_roles, ur):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        db = request.environ['db']
        data = request.json

        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'invalid payload', 'code': '0x01'}), 404

        # verify user account
        anu = asp_net_user.get_asp_net_user_by(
            db,
            ['Id', 'Email'],
            'UserName',
            data['email'])

        if anu is None:
            return jsonify({'error': 'user: not found', 'code': '0x01'}), 404

        # verify entry has not already been created in FlaskUsers
        fu = flask_user.get_flask_user_by(
            db,
            ['Id'],
            'Id',
            anu.Id)

        if fu is not None:
            return jsonify({'error': 'api user: exists', 'code': '0x01'}), 401

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), salt, 1000000)
        salt_key = salt + key
        passEncoded = base64.b64encode(salt_key)

        # insert into FlaskUsers
        nfu = flask_user.FlaskUser(**{
            'Id': anu.Id,
            'Email': anu.Email,
            'PasswordHash': passEncoded.decode("utf-8")
        })
        res = flask_user.insert_flask_user(db, nfu)
        print(res)

        resp = {'status': 200}
        return jsonify(resp), 200


def test(app):
    @app.route('/auth/test', methods=['GET'])
    def test_service():
        db = request.environ['db']

        email = request.args.get('email')
        # print(email)
        # if not db.connect():
        #     return jsonify({'error': 'unable to connect to db'}), 500

        sql = """
            SELECT
                Id,
                FirstName,
                LastName,
                Email
            FROM
                dbo.AspNetUsers
            WHERE
                Email = ?
            ORDER BY Email
            OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;
        """

        params = email

        db.cursor.execute(sql, params)
        users = []
        for u in db.cursor:
            user = collections.OrderedDict()
            user['id'] = u[0]
            user['first_name'] = u[1]
            user['last_name'] = u[2]
            user['email'] = u[3]
            users.append(user)

        if len(users) == 0:
            return jsonify({'error': 'user not found'}), 404

        return jsonify(users), 200
