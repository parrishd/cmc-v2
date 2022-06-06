from flask import jsonify, request
from datetime import datetime
from uuid import UUID

from api.util import validation
from api.model import condition
from api.middleware import role_validation


class ConditionService:
    fields = [
        'Id',
        'Code',
        'Name',
        'Description',
        'Status',
        'isCategorical',
        'Order'
    ]

    def __init__(self, app):
        self.condition_service_get_roles = ['Admin', 'Officer', 'Member']
        self.condition_service_delete_roles = ['Admin', 'Officer', 'Member']
        app.route('/condition/<cid>', methods=['GET', 'DELETE', 'PUT'])(self.condition_service)

        self.condition_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/condition', methods=['POST'])(self.condition_post_service)

        self.condition_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/condition/list', methods=['GET'])(self.condition_list_service)

    def condition_service(self, cid):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        ur = request.environ['role']

        if not validation.isint(cid):
            return jsonify({'error': 'invalid condition id'})

        if request.method == 'GET':
            return self.get(db, cid, ur)

        if request.method == 'DELETE':
            return self.delete(db, cid, ur)

        if request.method == 'PUT':
            return self.put(db, cid, uid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # GET Condition
    def get(self, db, cid, user_roles):
        # validate roles
        if not role_validation.validate(self.condition_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        c = condition.get_condition_by(
            db,
            [
                'Id',
                '[Code]',
                'Name',
                'Description',
                'Status',
                '[Order]',
                'isCategorical',
            ],
            'Id',
            cid
        )
        if c is None:
            return jsonify({'status': 404, 'error': 'record not found'}), 404

        return jsonify(c.__dict__), 200

    # DELETE condition
    def delete(self, db, cid, user_roles):
        # validate roles
        if not role_validation.validate(self.condition_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        try:
            c = condition.delete(db, cid)
            return jsonify({'status': 200, 'id': c}), 200
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

    # PUT condition
    def put(self, db, cid, user_id, user_roles):
        # validate roles
        if not role_validation.validate(self.condition_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # validate fields
        c, err = self.validate(data, post=False)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        # insert data
        try:
            _ = condition.update(db, cid, c)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, cid, user_roles)

    # post services POST/PATCH
    def condition_post_service(self):
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

    # POST condition
    def post(self, db, user_id, user_roles):
        # validate roles
        if not role_validation.validate(self.condition_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # validate fields
        c, err = self.validate(data, post=True)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        # insert data
        try:
            id = condition.insert(db, c)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, id, user_roles)

    # list service handlers
    def condition_list_service(self):
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
        if not role_validation.validate(self.condition_list_service_roles, user_roles):
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
        count = condition.count(db, search)
        conditions = condition.get_conditions(db, col, direction, page * limit, limit, search)

        resp = {
            'total': count,
            'count': len(conditions),
            'page': page,
            'limit': limit if limit > 0 else count,
            'data': [c.__dict__ for c in conditions]
        }

        return jsonify(resp), 200

    @staticmethod
    def validate(data, post=False):
        errors = []
        # todo: check validation
        if post:
            if 'Code' not in data:
                errors.append('Code is required 1')

            if 'Name' not in data:
                errors.append('Name is required')

            # if 'Order' not in data:
            #     errors.append('Order is required')

            if 'Status' not in data:
                errors.append('Status is required')

            if 'isCategorical' not in data:
                errors.append('isCategorical is required')

        if 'Id' in data:
            errors.append('Id should not be include')

        if 'Status' in data and data['Status'] is not None:
            if not validation.isBool(data['Status']):
                errors.append('Status must be of type boolean')

        if 'isCategorical' in data and data['isCategorical'] is not None:
            if not validation.isBool(data['isCategorical']):
                errors.append('isCategorical must be of type boolean')

        return data, errors
