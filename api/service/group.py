from flask import jsonify, request

from api.model import group
from api.middleware import role_validation

class GroupService:
    roles = []

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

        if request.method == 'GET':
            return self.get(gid, db, ur)

        if request.method == 'DELETE':
            return self.delete(request.json)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # get group
    def get(self, gid, db, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        g = group.get_group_by(db, ['*'], 'Id', gid)
        if g is None:
            return jsonify({'error': 'record not found'}), 404

        return jsonify(g.__dict__), 200

    # post services POST/PATCH
    def group_post_service(self):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        ur = request.environ['role']

        if request.method == 'POST':
            return self.post(db, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # POST group
    def post(self, db, user_roles):
        # validate roles
        if not role_validation.validate(self.group_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        print('here')

        return jsonify({}), 200

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
