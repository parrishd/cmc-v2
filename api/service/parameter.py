from flask import jsonify, request

from api.util import validation
from api.model import parameter
from api.middleware import role_validation


class ParameterService:
    fields = [
        'Id',
        'Name',
        'Units',
        'Method',
        'Tier',
        'Matrix',
        'Tidal',
        'NonTidal',
        'AnalyticalMethod',
        'ApprovedProcedure',
        'Equipment',
        'Precision',
        'Accuracy',
        'Range',
        'QcCriteria',
        'InspectionFreq',
        'InspectionType',
        'CalibrationFrequency',
        'StandardOrCalInstrumentUsed',
        'TierIIAdditionalReqs',
        'HoldingTime',
        'SamplePreservation',
        'Code',
        'Status',
        'requiresSampleDepth',
        'isCalibrationParameter',
        'requiresDuplicate',
        'Description',
        'NonfatalUpperRange',
        'NonfatalLowerRange'
    ]

    def __init__(self, app):
        self.parameter_service_get_roles = ['Admin', 'Officer', 'Member']
        self.parameter_service_delete_roles = ['Admin', 'Officer', 'Member']
        app.route('/parameter/<pid>', methods=['GET', 'DELETE', 'PUT'])(self.parameter_service)

        self.parameter_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/parameter', methods=['POST'])(self.parameter_post_service)

        self.parameter_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/parameter/list', methods=['GET'])(self.parameter_list_service)

    def parameter_service(self, pid):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        ur = request.environ['role']

        if not validation.isint(pid):
            return jsonify({'error': 'invalid parameter id'})

        if request.method == 'GET':
            return self.get(db, pid, ur)

        if request.method == 'DELETE':
            return self.delete(db, pid, ur)

        if request.method == 'PUT':
            return self.put(db, pid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # GET parameter
    def get(self, db, pid, user_roles):
        # validate roles
        if not role_validation.validate(self.parameter_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        p = parameter.get_parameter_by(db, ['*'], 'Id', pid)
        if p is None:
            return jsonify({'status': 404, 'error': 'record not found'}), 404

        return jsonify(p.__dict__), 200

    # DELETE parameter
    def delete(self, db, cid, user_roles):
        # validate roles
        if not role_validation.validate(self.parameter_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        try:
            p = parameter.delete(db, cid)
            return jsonify({'status': 200, 'id': p}), 200
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

    # PUT parameter
    def put(self, db, pid, user_roles):
        # validate roles
        if not role_validation.validate(self.parameter_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # validate fields
        params, err = self.validate(data, post=False)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        # insert data
        try:
            _ = parameter.update(db, pid, params)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, pid, user_roles)

    # post services POST/PATCH
    def parameter_post_service(self):
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

    # POST parameter
    def post(self, db, user_id, user_roles):
        # validate roles
        if not role_validation.validate(self.parameter_list_service_roles, user_roles):
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
            id = parameter.insert(db, c)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, id, user_roles)

    # list service handlers
    def parameter_list_service(self):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        ur = request.environ['role']

        if request.method == 'GET':
            return self.list(db, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # GET all records or use params
    def list(self, db, user_roles):
        # validate roles
        if not role_validation.validate(self.parameter_list_service_roles, user_roles):
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
        count = parameter.count(db, search)
        params = parameter.get_parameters(db, col, direction, page * limit, limit, search)

        resp = {
            'total': count,
            'count': len(params),
            'page': page,
            'limit': limit if limit > 0 else count,
            'data': [c.__dict__ for c in params]
        }

        return jsonify(resp), 200

    @staticmethod
    def validate(data, post=False):
        errors = []
        # for POST request, validate required fields
        if post:
            if 'Code' not in data:
                errors.append('Code is required')

            if 'Status' not in data:
                errors.append('Status is required')

            if 'requiresSampleDepth' not in data:
                errors.append('requiresSampleDepth is required')

            if 'isCalibrationParameter' not in data:
                errors.append('isCalibrationParameter is required')

            if 'requiresDuplicate' not in data:
                errors.append('requiresDuplicate is required')

        if 'Id' in data:
            errors.append('Id should not be include')

        if 'Code' in data and data['Code'] is not None:
            if len(data['Code']) > 450:
                errors.append('Code is too long, maximum length must be 450')

        # validate data types
        if 'Method' in data and data['Method'] is not None:
            if not validation.isint(data['Method']):
                errors.append('Method must be of type integer')

        if 'NonfatalUpperRange' in data and data['NonfatalUpperRange'] is not None:
            if not validation.isfloat(data['NonfatalUpperRange']):
                errors.append('NonfatalUpperRange must be of type float')

        if 'NonfatalLowerRange' in data and data['NonfatalLowerRange'] is not None:
            if not validation.isfloat(data['NonfatalLowerRange']):
                errors.append('NonfatalLowerRange must be of type float')

        if 'Status' in data and data['Status'] is not None:
            if not validation.isBool(data['Status']):
                errors.append('Status must be of type boolean')

        if 'Tidal' in data and data['Tidal'] is not None:
            if not validation.isBool(data['Tidal']):
                errors.append('Tidal must be of type boolean')

        if 'NonTidal' in data and data['NonTidal'] is not None:
            if not validation.isBool(data['NonTidal']):
                errors.append('NonTidal must be of type boolean')

        if 'requiresSampleDepth' in data and data['requiresSampleDepth'] is not None:
            if not validation.isBool(data['requiresSampleDepth']):
                errors.append('requiresSampleDepth must be of type boolean')

        if 'isCalibrationParameter' in data and data['isCalibrationParameter'] is not None:
            if not validation.isBool(data['isCalibrationParameter']):
                errors.append('isCalibrationParameter must be of type boolean')

        if 'requiresDuplicate' in data and data['requiresDuplicate'] is not None:
            if not validation.isBool(data['requiresDuplicate']):
                errors.append('requiresDuplicate must be of type boolean')

        return data, errors
