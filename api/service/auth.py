import json
import base64
import collections
from datetime import datetime, timedelta, timezone
from flask import jsonify, request
# from paseto.protocol.version2 import encrypt
import paseto
from paseto.keys.symmetric_key import SymmetricKey
from paseto.protocols.v4 import ProtocolVersion4


def login(app):
    @app.route('/auth/login', methods=['POST'])
    def service():
        db = request.environ['db']
        auth_key = request.environ['auth_key']
        data = request.json
        print(data)

        # fetch user from database by email
        sql = """
            SELECT 
                Id, 
                Status,
                EmailConfirmed, 
                PasswordHash
            FROM 
                dbo.AspNetUsers
            WHERE
                UserName = ?;
        """
        db.cursor.execute(sql, data['email'])
        q = db.cursor.fetchone()
        if q is None:
            return jsonify({'error': 'user: not found', 'code': '0x01'}), 404

        # create a user dictionary
        user = collections.OrderedDict()
        user['id'] = q[0]
        user['status'] = q[1]
        user['email_confirmed'] = q[2]
        user['password_hash'] = q[3]

        # check user status
        if not user['status']:
            return jsonify({'error': 'user: invalid status', 'code': '0x02'}), 403

        # check email confirmed
        if not user['email_confirmed']:
            return jsonify({'error': 'user: email confirmation', 'code': '0x03'}), 403

        # todo: load roles
        # todo: validate password
        # decoded = base64.b64decode(user['password_hash'])
        # print(decoded)
        # print(len(decoded))

        exp = datetime.now(timezone.utc) + timedelta(seconds=3600)
        token_data = {'id': user['id'], 'exp': exp.isoformat()}
        # token = encrypt(
        #     json.dumps(token_data).encode('utf-8'),
        #     auth_key.encode()
        # )
        # my_key = SymmetricKey.generate(protocol=ProtocolVersion4)
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
