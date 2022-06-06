from flask import jsonify, request
from datetime import datetime

from api.util import validation
from api.model import station
from api.middleware import role_validation


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
        app.route('/station/<gid>', methods=['GET', 'DELETE', 'PUT'])(self.station_service)

        self.station_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/station', methods=['POST'])(self.station_post_service)

        self.station_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/station/list', methods=['GET'])(self.station_list_service)

    def station_service(self, gid):
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        ur = request.environ['role']

        if not validation.isint(gid):
            return jsonify({'error': 'invalid group id'})

        if request.method == 'GET':
            return self.get(db, gid, ur)
        #
        # if request.method == 'DELETE':
        #     return self.delete(db, gid, ur)
        #
        # if request.method == 'PUT':
        #     return self.put(db, gid, uid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    # GET station
    def get(self, db, gid, user_roles):
        # validate roles
        if not role_validation.validate(self.station_list_service_roles, user_roles):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        g = station.get_station_by(db, ['*'], 'Id', gid)
        if g is None:
            return jsonify({'status': 404, 'error': 'record not found'}), 404

        return jsonify(g.__dict__), 200

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

        # if request.method == 'POST':
        #     return self.post(db, uid, ur)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

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
