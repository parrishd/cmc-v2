from flask import jsonify, request
from datetime import datetime

from api.util import number
from api.model import group
from api.middleware import role_validation


class GroupService:
    fields = [
        'AddressFirst',
        'AddressSecond',
        'BenthicMethod',
        'City',
        'CmcMember',
        'CmcMember2',
        'CmcMember3',
        'CmcMember4',
        'CmcMember5',
        'Code',
        'ContactCellPhone',
        'ContactEmail',
        'ContactName',
        'ContactOfficePhone',
        'CreatedBy',
        'CreatedDate',
        'DataUseDate',
        'Description',
        'Id',
        'Logo',
        'ModifiedBy',
        'ModifiedDate',
        'Name',
        'ParametersSampled',
        'State',
        'Status',
        'Url',
        'Zip',
        'cmcQapp',
        'coordinatorCanPublish',
    ]

    def __init__(self, app):
        self.group_service_get_roles = ['Admin', 'Officer', 'Member']
        self.group_service_delete_roles = ['Admin', 'Officer', 'Member']
        app.route('/group/<gid>', methods=['GET', 'DELETE'])(self.group_service)

        self.group_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/group', methods=['POST'])(self.group_post_service)

        self.group_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/group/list', methods=['GET'])(self.group_list_service)

    def group_service(self, gid):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        ur = request.environ['role']

        if not number.isint(gid):
            return jsonify({'error': 'invalid group id'})

        if request.method == 'GET':
            return self.get(db, gid, ur)

        if request.method == 'DELETE':
            return self.delete(db, gid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # get group
    def get(self, db, gid, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        g = group.get_group_by(db, ['*'], 'Id', gid)
        if g is None:
            return jsonify({'status': 404, 'error': 'record not found'}), 404

        return jsonify(g.__dict__), 200

    # delete group
    def delete(self, db, gid, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        try:
            g = group.delete(db, gid)
            return jsonify({'status': 200, 'id': g}), 200
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

    # post services POST/PATCH
    def group_post_service(self):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        ur = request.environ['role']

        if request.method == 'POST':
            return self.post(db, uid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # POST group
    def post(self, db, user_id, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # set user id
        data['CreatedBy'] = user_id
        data['ModifiedBy'] = user_id

        # set dates
        date = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        data['CreatedDate'] = date
        data['DataUseDate'] = date
        data['ModifiedDate'] = date

        print(data)

        # validate fields
        g, err = self.validate(data, user_id)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        # insert data
        try:
            id = group.insert(db, g)
            g['Id'] = id
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return jsonify(g), 200

    # list service handlers
    def group_list_service(self):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        ur = request.environ['role']

        if request.method == 'GET':
            return self.list(db, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    def list(self, db, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        colsAvailable = ['Id', 'Name', 'Status', 'Code']
        dirAvailable = ['ASC', 'DESC']

        args = request.args
        sort = args.get('sort', default='Id', type=str)
        page = args.get('page', default=0, type=int)
        limit = args.get('limit', default=0, type=int)
        search = args.get('search', default='', type=str)

        # sorting
        col = 'Id'
        direction = 'ASC'
        sp = sort.split(':')
        if len(sp) == 2:
            if sp[0] in colsAvailable:
                col = sp[0]
            if sp[1].upper() in dirAvailable:
                direction = sp[1].upper()

        # query db for count and results
        count = group.count(db, search)
        groups = group.get_groups(db, col, direction, page * limit, limit, search)

        resp = {
            'total': count,
            'count': len(groups),
            'page': page,
            'limit': limit if limit > 0 else count,
            'data': [g.__dict__ for g in groups]
        }

        return jsonify(resp), 200

    @staticmethod
    def validate(data, uid):
        errors = []

        # todo: validation

        return data, errors
