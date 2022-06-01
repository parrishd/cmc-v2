import json
import pyodbc

from datetime import datetime
from flask import jsonify, request
from api.util import validation, datetimeutil
from api.middleware import role_validation
from api.model import \
    group, \
    station, \
    asp_net_user, \
    benthic_event, \
    benthic_sample, \
    benthic_parameter, \
    benthic_condition, \
    benthic_monitor_log, \
    benthic_event_condition, \
    benthic_condition_category


class BenthicIntegrationService:
    roles = []

    def __init__(self, app):
        self.benthic_roles = ['Admin', 'Officer', 'Member']
        app.route('/integration/benthic', methods=['POST', 'DELETE'])(self.integration_benthic)

    def integration_benthic(self):
        if request.method == 'POST':
            return self.post(request.json)

        if request.method == 'DELETE':
            return self.delete(request.json)

        resp = {'status': 400, 'error': 'method not allowed'}
        return jsonify(resp), 400

    def post(self, data):
        # validate roles
        ur = request.environ['role']
        if not role_validation.validate(self.benthic_roles, ur):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        # fetch the db connection used to validate data
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        bise, errors = self.validate(db, data, uid, ur)

        if len(errors) > 0:
            return jsonify({'error': 'data validation error(s)', 'errors': errors})

        # print(json.dumps(bise, default=vars))

        eid, errors = self.insert(bise, db)

        if len(errors) > 0:
            return jsonify({'error': 'data insert error(s)', 'errors': errors})

        resp = {'message': f'benthic event {eid} has been added', 'status': 200}
        return jsonify(resp), 200

    def delete(self, data):
        # validate roles
        ur = request.environ['role']
        if not role_validation.validate(self.benthic_roles, ur):
            return jsonify({'status': 403, 'error': 'permission denied'}), 403

        # fetch our authed user
        uid = request.environ['user_id']
        if uid is None or uid == '':
            return jsonify({'error': 'unable to determine user'}), 400

        # fetch the db connection used to validate data
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        # validate source (ie groupCode)
        if 'source' not in data:
            return jsonify({'error': 'invalid payload'})
        else:
            g = group.get_group_by(
                db,
                [
                    'Id',
                    'Name',
                    'Code',
                    'BenthicMethod',
                    'CmcMember',
                    'CmcMember2',
                    'CmcMember3',
                    'CmcMember4',
                    'CmcMember5'
                ],
                'Code',
                data['source']
            )
            if g is None:
                return jsonify({'error': 'invalid source'})
            else:
                # validate the uid is a cmcMember IF user role is Member
                if ur['name'] == 'Member':
                    cmc = group.cmc_members_to_array(g)
                    if uid not in cmc:
                        return jsonify({'error': 'invalid group membership'})

        # validate station
        if 'station' not in data:
            return jsonify({'error': 'invalid payload'})
        else:
            s = station.get_station_by(db, ['Id', 'Name', 'Code'], 'Code', data['station'])
            if s is None:
                return jsonify({'error': 'invalid station'})

        # validate datetime
        if 'datetime' not in data:
            return jsonify({'error': 'invalid payload'})
        else:
            dateTime = datetimeutil.getdatetime(data['datetime'])

            if dateTime is None:
                return jsonify({'error': 'datetime format is invalid'})

        # check to see if a benthic event already exists
        be = benthic_event.get_benthic_event_by_group_station_datetime(
            db,
            ['Id'],
            g.Id,
            s.Id,
            dateTime
        )
        if be is None:
            return jsonify({'error': 'event does not exist'})

        print(be.Id)
        res = benthic_event.delete_benthic_event_by_id(db, be.Id)
        print(res)

        return jsonify({'status': 200})

    @staticmethod
    def validate(db, data, uid, user_role):
        errors = []
        bise = BenthicIntegrationServiceEvent(uid)

        # validate source (ie groupCode)
        if 'source' not in data:
            errors.append('invalid data set: source is required')
        else:
            g = group.get_group_by(
                db,
                [
                    'Id',
                    'Name',
                    'Code',
                    'BenthicMethod',
                    'CmcMember',
                    'CmcMember2',
                    'CmcMember3',
                    'CmcMember4',
                    'CmcMember5'
                ],
                'Code',
                data['source']
            )
            if g is None:
                errors.append('invalid data: source could not be found')
            else:
                # validate the uid is a cmcMember IF user role is Member
                if user_role['name'] == 'Member':
                    cmc = group.cmc_members_to_array(g)
                    if uid not in cmc:
                        return None, ['invalid group membership']

                bise.group = g

        # validate station
        if 'station' not in data:
            errors.append('invalid data set: station is required')
        else:
            s = station.get_station_by(db, ['Id', 'Name', 'Code'], 'Code', data['station'])
            if s is None:
                errors.append('invalid data: station could not be found')
            else:
                bise.station = s

        # validate datetime
        if 'datetime' not in data:
            errors.append('invalid data set: datetime is required')
        else:
            dateTime = datetimeutil.getdatetime(data['datetime'])

            if dateTime is None:
                errors.append('invalid data: datetime format is invalid')
            else:
                bise.dateTime = datetime.strftime(dateTime, '%Y-%m-%dT%H:%M:%S')

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
                          'tallies, conditions, monitors')

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
            'Comments': comments,
            'StationId': bise.station.Id,
            'GroupId': bise.group.Id,
            'CreatedBy': uid,
            'CreatedDate': datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S'),
            'ModifiedBy': uid,
            'ModifiedDate': datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        })

        # validate the event tallies
        idx = 0
        for t in tallies:
            # verify correct keys
            if 'name' not in t or 'value' not in t:
                errors.append(f'tally {idx}: invalid data. missing name or value keys')
            else:
                tallySample = BenthicIntegrationServiceSample(t['name'], t['value'])

                # check if value is a number
                if not validation.isfloat(t['value']):
                    errors.append(f'tally {idx}: value is not a number for parameter_type tally')

                # check if valid parameter name
                bp = benthic_parameter.get_benthic_parameter_by(db, ['Id', 'Code', 'Name'], 'Code', t['name'])
                if bp is None:
                    errors.append(f'tally {idx}: has an invalid parameter_name for parameter_type of tally')
                else:
                    tallySample.paramId = bp.Id

                # check if this sample already exists in data set and if not append it to the event tallies
                if tallySample.paramId is not None:
                    found = False
                    for et in bise.tallies:
                        if et.paramId == tallySample.paramId:
                            found = True
                            break

                    if found:
                        errors.append(f'tally {idx} a duplicate entry for this parameter name')
                    else:
                        bise.tallies.append(tallySample)

            idx += 1

        # validate the event conditions
        idx = 0
        for c in conditions:
            # verify correct keys
            if 'name' not in c or 'value' not in c:
                errors.append(f'condition {idx}: invalid data. missing name or value keys')
            else:
                condSample = BenthicIntegrationServiceSample(c['name'], c['value'])

                # check if value is empty
                if c['value'].strip() == '':
                    errors.append(f'condition {idx}: value is empty for parameter_type condition')

                # check if valid parameter name
                bc = benthic_condition.get_benthic_condition_by(db, ['Id', 'isCategorical'], 'Code', c['name'])
                if bc is None:
                    errors.append(f'condition {idx}: has an invalid parameter_name for parameter_type of tally')
                else:
                    condSample.paramId = bc.Id

                    # check if valid categorically
                    if bc.isCategorical:
                        bcc = benthic_condition_category.get_benthic_condition_category_by_condition_id_category(
                            db,
                            ['Id'],
                            bc.Id,
                            c['value']
                        )
                        if bcc is None:
                            errors.append(f'condition {idx}: invalid benthic condition value')

                # check if this sample already exists in data set and if not append it to the event tallies
                if condSample.paramId is not None:
                    found = False
                    for ec in bise.conditions:
                        if ec.paramId == condSample.paramId:
                            found = True
                            break

                    if found:
                        errors.append(f'condition {idx}: a duplicate entry for this parameter name')
                    else:
                        bise.conditions.append(condSample)

            idx += 1

        # validate event monitors
        idx = 0
        for m in monitors:
            # verify correct keys
            if 'name' not in m or 'value' not in m:
                errors.append(f'monitor {idx}: invalid data. missing name or value keys')
            else:
                monitorSample = BenthicIntegrationServiceSample(m['name'], m['value'])

                # verify user code
                anu = asp_net_user.get_asp_net_user_by(db, ['Id'], 'Code', m['name'])
                if anu is None:
                    errors.append(f'monitor {idx}: does not match a user code')
                else:
                    monitorSample.paramId = anu.Id

                # check if value is a number
                if not validation.isfloat(m['value']):
                    errors.append(f'monitor {idx}: value is not a number for parameter_type monitor')

                if monitorSample.paramId is not None:
                    found = False
                    for em in bise.monitors:
                        if em.paramId == monitorSample.paramId:
                            found = True
                            break

                    if found:
                        errors.append(f'monitor {idx}: a duplicate entry for this parameter name')
                    else:
                        bise.monitors.append(monitorSample)

            idx += 1

        return bise, errors

    @staticmethod
    def insert(bise, db):
        errors = []
        eventId = None

        db.autocommit = False

        try:
            eventId = benthic_event.insert_benthic_event(db, bise.event)

            # loop through tally samples and insert
            for t in bise.tallies:
                bs = benthic_sample.BenthicSample(**{
                    'Value': t.value,
                    'Comments': bise.event.Comments,
                    'QaFlagId': 1,
                    'CreatedBy': bise.userId,
                    'CreatedDate': bise.event.CreatedDate,
                    'ModifiedBy': bise.userId,
                    'ModifiedDate': bise.event.ModifiedDate,
                    'BenthicEventId': eventId,
                    'BenthicParameterId': t.paramId,
                })
                try:
                    benthic_sample.insert_benthic_sample(db, bs)
                except Exception as err:
                    errors.append(str(err))

            # loop through monitor samples and insert
            for m in bise.monitors:
                ml = benthic_monitor_log.BenthicMonitorLog(**{
                    'UserId': m.paramId,
                    'Hours': m.value,
                    'BenthicEventId': eventId,
                    'CreatedBy': bise.userId,
                    'CreatedDate': bise.event.CreatedDate,
                    'ModifiedBy': bise.userId,
                    'ModifiedDate': bise.event.ModifiedDate,
                })
                try:
                    benthic_monitor_log.insert_benthic_monitor_log(db, ml)
                except Exception as err:
                    errors.append(str(err))

            # loop through condition samples and insert
            for c in bise.conditions:
                ec = benthic_event_condition.BenthicEventCondition(**{
                    'BenthicEventId': eventId,
                    'BenthicConditionId': c.paramId,
                    'Value': c.value
                })
                try:
                    benthic_event_condition.insert_benthic_event_condition(db, ec)
                except Exception as err:
                    errors.append(str(err))

        except Exception as err:
            errors.append(str(err))

        # no insertion errors occurred. commit
        if len(errors) == 0:
            db.cursor.commit()

        return eventId, errors


class BenthicIntegrationServiceEvent:
    def __init__(self, uid):
        self.userId = uid
        self.event = None
        self.group = None
        self.station = None
        self.dateTime = None
        self.comments = None

        self.tallies = []
        self.conditions = []
        self.monitors = []


class BenthicIntegrationServiceSample:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.paramId = None

#
