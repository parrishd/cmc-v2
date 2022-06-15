from flask import jsonify, request
from datetime import datetime

from api.util import validation
from api.model import station
from api.middleware import role_validation
from api.integration.chesapeakebay import ChesapeakeBayIntegration


class StationService:
    fields = [
        'Id',
        'Name',
        'NameLong',
        'Lat',
        'Long',
        'Cbseg',
        'WaterBody',
        'Description',
        'Datum',
        'CityCounty',
        'Tidal',
        'Comments',
        'Code',
        'Status',
        'CreatedBy',
        'CreatedDate',
        'ModifiedBy',
        'ModifiedDate',
        'StationSamplingMethodId',
        'Fips',
        'Huc12',
        'State',
        'Huc6Name',
        'AltCode',
    ]

    def __init__(self, app):
        self.station_service_get_roles = ['Admin', 'Officer', 'Member']
        self.station_service_delete_roles = ['Admin', 'Officer', 'Member']
        app.route('/station/<sid>', methods=['GET', 'DELETE', 'PUT'])(self.station_service)

        self.station_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/station', methods=['POST'])(self.station_post_service)

        self.station_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/station/list', methods=['GET'])(self.station_list_service)

    def station_service(self, sid):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        ur = request.environ['role']

        if not validation.isint(sid):
            return jsonify({'error': 'invalid group id'})

        if request.method == 'GET':
            return self.get(db, sid, ur)

        if request.method == 'DELETE':
            return self.delete(db, sid, ur)

        if request.method == 'PUT':
            return self.put(db, sid, uid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # GET station
    def get(self, db, sid, user_roles):
        # validate roles
        if not role_validation.validate(self.station_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        g = station.get_station_by(db, ['*'], 'Id', sid)
        if g is None:
            return jsonify({'status': 404, 'error': 'record not found'}), 404

        return jsonify(g.__dict__), 200

    # DELETE station
    def delete(self, db, sid, user_roles):
        # validate roles
        if not role_validation.validate(self.station_service_post_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        try:
            g = station.delete(db, sid)
            return jsonify({'status': 200, 'id': g}), 200
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

    # PUT station
    def put(self, db, sid, user_id, user_roles):
        # validate roles
        if not role_validation.validate(self.station_service_post_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # validate fields
        s, err = self.validate(data, post=False)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        # set user id
        s['ModifiedBy'] = user_id

        # set dates
        date = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        s['ModifiedDate'] = date

        # insert data
        try:
            _ = station.update(db, sid, s)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, sid, user_roles)  # jsonify(g), 200

    # post services POST/PATCH
    def station_post_service(self):
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
        if not role_validation.validate(self.station_service_post_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # parse out any invalid fields
        json = request.json
        data = {}
        for k in json.keys():
            if k in self.fields:
                data[k] = json[k]

        # validate fields
        s, err = self.validate(data, post=True)
        if len(err) > 0:
            return jsonify({'status': 400, 'errors': err}), 400

        cb = ChesapeakeBayIntegration()
        loc = cb.get([])
        if loc is None:
            return jsonify({'status': 400, 'errors': ['unable to perform location lookup - chesapeake bay api']}), 400

        print(loc)

        # merge loc data in
        s = {**s, **loc}

        print(s)

        # set user id
        s['CreatedBy'] = user_id
        s['ModifiedBy'] = user_id

        # set dates
        date = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        s['CreatedDate'] = date
        s['ModifiedDate'] = date

        # insert data
        try:
            id = station.insert(db, s)
        except Exception as err:
            return jsonify({'status': 500, 'error': str(err)}), 403

        return self.get(db, id, user_roles)

    # list service handlers
    def station_list_service(self):
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
        if not role_validation.validate(self.station_list_service_roles, user_roles):
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
        count = station.count(db, search)
        groups = station.get_stations(db, col, direction, page * limit, limit, search)

        resp = {
            'total': count,
            'count': len(groups),
            'page': page,
            'limit': limit if limit > 0 else count,
            'data': [g.__dict__ for g in groups]
        }

        return jsonify(resp), 200

    @staticmethod
    def validate(data, post=False):
        errors = []

        if post:
            if 'Code' not in data:
                errors.append('Code is required')

            if 'Name' not in data:
                errors.append('Name is required')

        if 'Id' in data:
            errors.append('Id should not be include')

        if 'Status' in data and data['Status'] is not None:
            if not validation.isBool(data['Status']):
                errors.append('Status must be of type boolean')

        if 'Tidal' in data and data['Tidal'] is not None:
            if not validation.isBool(data['Tidal']):
                errors.append('Tidal must be of type boolean')

        if 'Lat' in data and data['Lat'] is not None:
            if not validation.isfloat(data['Lat']):
                errors.append('Lat must be of type float')

        if 'Long' in data and data['Long'] is not None:
            if not validation.isfloat(data['Long']):
                errors.append('Long must be of type float')

        return data, errors

