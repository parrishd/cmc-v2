import json

from datetime import datetime
from flask import jsonify, request
from api.util import validation
from api.model import \
    group, \
    station, \
    asp_net_user, \
    benthic_event, \
    benthic_sample, \
    benthic_parameter, \
    benthic_condition, \
    benthic_condition_category

# todo: this was copied over from the original api integration.
# updated logic to only import if ALL records are correct
class BenthicImportService:
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
        if not isinstance(data, list):
            return jsonify({'error': 'invalid data set'}), 400

        if len(data) == 0:
            return jsonify({'error': 'empty data set'}), 400

        # fetch the db connection used to validate data
        db = request.environ['db']

        # loop through dataset and validate
        idx = 0
        errors = []
        samples = []
        for sample in data:
            print(f'--{idx}: {sample}')
            biss, err = self.validate(sample, idx, samples, uid, db)
            if len(err) == 0:
                samples.append(biss)
            else:
                errors.append(err)

            idx += 1

        print(errors)
        # errors validating data return with validation errors
        if len(errors) > 0:
            return jsonify({'error': 'data parsing error(s)', 'errors': errors})

        # insert all the records
        idx = 0
        for s in samples:
            err = self.insert(s, idx, db)
            idx += 1

        resp = {'status': 200}
        return jsonify(resp), 200

    # @staticmethod
    def validate(self, d, i, ds, uid, db):
        # todo: iwl DataTable validation checks TBD

        biss = BenthicIntegrationServiceSample(d)
        errors = []

        # validate source (ie groupCode)
        if 'source' not in d:
            errors.append(f'record: {i} is missing key source')
        else:
            g = group.get_group_by(db, ['Id', 'Name', 'Code', 'BenthicMethod'], 'Code', d['source'])
            if g is None:
                errors.append(f'record: {i} has an invalid group code')
            else:
                biss.group = g

        # validate station
        if 'station' not in d:
            errors.append(f'record: {i} is missing key station')
        else:
            s = station.get_station_by(db, ['Id', 'Name', 'Code'], 'Code', d['station'])
            if s is None:
                errors.append(f'record: {i} has an invalid station code')
            else:
                biss.station = s

        # validate dateTime
        if 'dateTime' not in d:
            errors.append(f'record: {i} is missing key dateTime')
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

            tempDate = datetime.strptime('1994-04-01 12:00:00', '%Y-%m-%d %H:%M:%S')
            print(tempDate)

            for f in formats:
                print(f)
                try:
                    dateTime = datetime.strptime(d['dateTime'], f)
                    break
                except ValueError:
                    pass

            if dateTime is None:
                errors.append(f'record: {i} has invalid date/time format')
            else:
                # ref['dateTime'] = datetime.strftime(dateTime, '%Y-%m-%d %H:%M:%S.%f')
                biss.dateTime = datetime.strftime(dateTime, '%Y-%m-%d %H:%M:%S.%f')

        # validate comments
        comments = ''
        if 'comments' not in d:
            errors.append(f'record: {i} is missing key comments')
        else:
            comments = d['comments']

        # generate a 'key' for the event
        biss.eventKey = f'{biss.group.Id}-{biss.station.Id}-{biss.dateTime}'

        # load the event if one already exists
        be = benthic_event.get_benthic_event_by_group_station_datetime(
            db,
            ['Id'],
            biss.group.Id,
            biss.station.Id,
            biss.dateTime
        )
        if be is not None:
            biss.event = be
        else:
            # loop through 'new' events and use it as the event
            dse = self.get_event_from_ds(biss.eventKey, ds)
            if dse is not None:
                biss.event = dse
            else:
                # make a new event
                biss.event = benthic_event.BenthicEvent(**{
                    'Id': biss.eventKey,
                    'DateTime': biss.dateTime,
                    'Project': '',
                    'Comments': comments,
                    'StationId': biss.station.Id,
                    'GroupId': biss.group.Id,
                    'CreatedBy': uid,
                    'CreatedDate': datetime.now(),
                    'ModifiedBy': uid,
                    'ModifiedDate': datetime.now()
                })

        # validate parameter type, name, and value
        if 'parameter_type' not in d \
                or 'parameter_name' not in d \
                or 'value' not in d:
            errors.append(f'record: {i} is missing key parameter_type and/or parameter_name')
        else:
            # validate tally parameters
            if d['parameter_type'].lower() == 'tally':
                # set the type for insert
                biss.paramType = 'tally'

                # check if value is a number
                if not validation.isfloat(d['value']):
                    errors.append(f'record: {i} value is not a number for parameter_type tally')

                # check if valid parameter name
                bp = benthic_parameter.get_benthic_parameter_by(db, ['Id', 'Code', 'Name'], 'Code', d['parameter_name'])
                if bp is None:
                    errors.append(f'record: {i} has an invalid parameter_name for parameter_type of tally')
                else:
                    biss.benthicParam = bp

                # check if there is already a BenthicSample for this event id
                if biss.event is not None:
                    bs = benthic_sample.get_benthic_sample_by(db, ['Id'], 'BenthicEventId', biss.event.Id)
                    if bs is not None:
                        errors.append(f'record: {i} has a sample already associated with an event')
                    else:
                        # loop through to see if this parameter is already in our dataset
                        bp = self.get_benthic_sample_from_ds(biss.eventKey, biss.benthicParam.Id, ds)
                        if bp is not None:
                            errors.append(f'record: {i} duplicate benthic parameter associated with this event')

            # validate monitor parameters
            elif d['parameter_type'].lower() == 'monitor':
                biss.paramType = 'monitor'

                # verify user code
                anu = asp_net_user.get_asp_net_user_by(db, ['Id'], 'Code', d['parameter_name'])
                if anu is None:
                    errors.append(f'record: {i} does not match a user code')
                else:
                    biss.user = anu

                # check if value is a number
                if not validation.isfloat(d['value']):
                    errors.append(f'record: {i} value is not a number for parameter_type tally')

                # check if an event has already been added
                if biss.event is not None:
                    errors.append(f'record: {i} has an entry already associated with an event')

                # todo: left off here
                # todo: needed? appears redundant
                if biss.user is not None and biss.event is not None:
                    # not needed? already validating that the event has not been added
                    print(f'not needed? should already have an error because an event already exists for this entry')

            # validate condition parameters
            elif d['parameter_type'].lower() == 'condition':
                # verify the code exists
                bc = benthic_condition.get_benthic_condition_by(db, ['Id', 'isCategorical'], 'Code', d['parameter_name'])
                if bc is None:
                    errors.append(f'record: {i} parameter_name does not match a condition code')
                else:
                    biss.benthicCondition = bc

                    # verify the value provided
                    if d['value'] == '':
                        errors.append(f'record: {i} invalid benthic condition value')
                    else:
                        # verify condition category
                        if bc.isCategorical:
                            bcc = benthic_condition_category.get_benthic_condition_category_by_condition_id_category(
                                db,
                                ['Id'],
                                bc.Id,
                                d['value']
                            )
                            if bcc is None:
                                errors.append(f'record: {i} invalid benthic condition value')

                # check if an event has already been added
                if biss.event is not None:
                    errors.append(f'record: {i} has an entry already associated with an event')

                # todo: needed? appears redundant
                if biss.benthicCondition is not None and biss.event is not None:
                    # not needed? already validating that the event has not been added
                    print(f'not needed? should already have an error because an event already exists for this entry')

            # invalid parameter type
            else:
                errors.append(f'record: {i} has an invalid parameter_type')



        print(json.dumps(biss, default=vars))
        return biss, errors

    @staticmethod
    def insert(sample, i, db):
        errors = []

        # todo: create the event if needed
        # check the parameter type and insert tally, monitor, or condition

        return errors

    @staticmethod
    def get_event_from_ds(key, ds):
        for s in ds:
            if s.event.Id == key:
                return s.event
        return None

    @staticmethod
    def get_benthic_sample_from_ds(key, bsid, ds):
        for s in ds:
            if s.event.Id == key and s.benthicParam is not None:
                if s.benthicParam.Id == bsid:
                    return s.benthicParam
        return None


class BenthicIntegrationServiceSample:
    sample = None
    user = None
    event = None
    eventKey = None
    group = None
    station = None
    dateTime = None
    paramType = None
    description = None
    benthicParam = None
    benthicCondition = None

    def __init__(self, data):
        self.data = data



#

