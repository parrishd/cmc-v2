import json

from datetime import datetime
from flask import jsonify, request
from api.util import number
from api.model import \
    group, \
    station, \
    asp_net_user, \
    benthic_event, \
    benthic_sample, \
    benthic_parameter, \
    benthic_condition, \
    benthic_condition_category


class BenthicIntegrationService:
    roles = []

    def __init__(self, app, roles):
        self.roles = roles
        app.route('/integration/benthic', methods=['POST'])(self.integration_benthic)

    def integration_benthic(self):
        # todo: validate roles

        if request.method == 'POST':
            return self.post(request.json)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 200

    def post(self, data):
        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        # verify the data
        # if not isinstance(data, list):
        #     return jsonify({'error': 'invalid data set'}), 400

        # if len(data) == 0:
        #     return jsonify({'error': 'empty data set'}), 400

        # fetch the db connection used to validate data
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        print(data)

        bise, errors = self.validate(data, uid, db)

        if len(errors) > 0:
            return jsonify({'error': 'data validation error(s)', 'errors': errors})

        #
        # # insert all the records
        # idx = 0
        # for s in samples:
        #     err = self.insert(s, idx, db)
        #     idx += 1

        resp = {'status': 200}
        return jsonify(resp), 200

    @staticmethod
    def validate(data, uid, db):
        errors = []
        bise = BenthicIntegrationServiceEvent(data)

        # validate source (ie groupCode)
        if 'source' not in data:
            errors.append('invalid data set: source is required')
        else:
            g = group.get_group_by(db, ['Id', 'Name', 'Code', 'BenthicMethod'], 'Code', d['source'])
            if g is None:
                errors.append('invalid data: source could not be found')
            else:
                bise.group = g

        # validate station
        if 'station' not in data:
            errors.append('invalid data set: station is required')
        else:
            s = station.get_station_by(db, ['Id', 'Name', 'Code'], 'Code', d['station'])
            if s is None:
                errors.append('invalid data: station could not be found')
            else:
                bise.station = s

        # validate datetime
        if 'datetime' not in data:
            errors.append('invalid data set: datetime is required')
        else:
            dateTime = None
            formats = [
                '%m/%d/%Y %I:%M %p',  # current format 1
                '%m/%d/%Y %H:%M %p',  # current format 2
                '%Y-%m-%d %H:%M:%S',  # iso8601 formats
                '%Y-%m-%d %H:%M:%S.%f',  # iso8601 formats
                '%Y-%m-%dT%H:%M:%S.%f',  # iso8601 formats
                '%Y-%m-%dT%H:%M:%S.%f',  # iso8601 formats
                '%Y-%m-%dT%H:%M:%S.%f%z',  # iso8601 formats
            ]

            for f in formats:
                try:
                    dateTime = datetime.strptime(d['dateTime'], f)
                    break
                except ValueError:
                    pass

            if dateTime is None:
                errors.append('invalid data: datetime format is invalid')
            else:
                bise.dateTime = datetime.strftime(dateTime, '%Y-%m-%d %H:%M:%S.%f')

        # validate comments
        comments = ''
        if 'comments' not in data:
            errors.append('invalid data set: comments is required')
        else:
            comments = data['comments']

        tallies = []
        if 'tallies' in data:
            tallies = data['tallies']

        conditions = []
        if 'conditions' in data:
            conditions = data['conditions']

        monitors = []
        if 'monitors' in data:
            monitors = data['monitors']

        if len(tallies) == 0 and len(conditions) == 0 and len(monitors):
            errors.append('event must have at least one of the following sample sets with sample data:'
                          'tally_samples, condition_samples, monitor_samples')

        # return any errors at this point. no need to process any further
        if len(errors) > 0:
            return None, errors

        # check to see if a benthic event already exists
        be = benthic_event.get_benthic_event_by_group_station_datetime(
            db,
            ['Id'],
            bise.group.Id,
            bise.station.Id,
            bise.dateTime
        )
        if be is not None:
            return None, ['event exists: delete existing event before resubmitting']

        # setup a new event
        bise.event = benthic_event.BenthicEvent(**{
            'DateTime': bise.dateTime,
            'Project': '',
            'Comments': comments,
            'StationId': bise.station.Id,
            'GroupId': bise.group.Id,
            'CreatedBy': uid,
            'CreatedDate': datetime.now(),
            'ModifiedBy': uid,
            'ModifiedDate': datetime.now()
        })

        # todo: loop through tallies data and validate
        idx = 0
        for t in tallies:
            # verify correct keys
            if 'name' not in t or 'value' not in t:
                errors.append(f'tally {idx}: invalid data. missing name or value keys')
            else:
                print('continue validation of tally variables')

        # todo: loop through conditions and validate
        idx = 0
        for c in conditions:
            # verify correct keys
            if 'name' not in c or 'value' not in c:
                errors.append(f'condition {idx}: invalid data. missing name or value keys')
            else:
                print('continue validation of condition variables')

        # todo: loop through monitors and validate
        idx = 0
        for c in monitors:
            # verify correct keys
            if 'name' not in c or 'value' not in c:
                errors.append(f'condition {idx}: invalid data. missing name or value keys')
            else:
                print('continue validation of condition variables')

        # return any sample errors at this point
        if len(errors) > 0:
            return None, errors

        return bise, errors

    @staticmethod
    def insert(sample, i, db):
        errors = []

        # todo: create the event if needed
        # check the parameter type and insert tally, monitor, or condition

        return errors


class BenthicIntegrationServiceEvent:
    data = None
    event = None
    group = None
    station = None
    dateTime = None

    tallies = []
    conditions = []
    monitors = []

    def __init__(self, data):
        self.data = data

#
