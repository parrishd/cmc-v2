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
from api.model import  flask_user, asp_net_user, asp_net_user_role


def login(app):
    @app.route('/auth/login', methods=['POST'])
    def service():
        db = request.environ['db']
        auth_key = request.environ['auth_key']
        data = request.json
        print(data)

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
        if anur is None or len(anur) == 0:
            return jsonify({'error': 'invalid role set', 'code': '0x01'}), 403

        roles = []
        for r in anur:
            roles.append({'id': r.RoleId, 'name': r.Name})

        exp = datetime.now(timezone.utc) + timedelta(seconds=3600)
        token_data = {'id': anu.Id, 'exp': exp.isoformat(), 'roles': roles}
        sk = SymmetricKey(key_material=auth_key.encode(), protocol=ProtocolVersion4)
        token = paseto.create(
            key=sk,
            purpose='local',
            claims=token_data,
            exp_seconds=3600
        )

        resp = {'token': token, 'exp': exp.isoformat()}
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
