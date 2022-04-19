from datetime import datetime
from flask import jsonify, request
from api.util import number, datetimeutil
from api.model import \
    group, \
    event, \
    sample, \
    station, \
    problem, \
    parameter, \
    condition, \
    qualifier, \
    monitor_log, \
    asp_net_user, \
    event_condition, \
    condition_category


class WaterQualityIntegrationService:
    roles = []

    def __init__(self, app, roles):
        self.roles = roles
        app.route('/integration/water-quality', methods=['POST'])(self.integration_water_quality)

    def integration_water_quality(self):
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

        # fetch the db connection used to validate data
        db = request.environ['db']
        if db is None:
            return jsonify({'error': 'database connection failed'})

        wqise, errors = self.validate(data, uid, db)

        if len(errors) > 0:
            return jsonify({'error': 'data validation error(s)', 'errors': errors}), 500

        eid, errors = self.insert(wqise, db)

        if len(errors) > 0:
            return jsonify({'error': 'data insert error(s)', 'errors': errors}), 500

        resp = {'message': f'water quality event {eid} has been added', 'status': 200}
        return jsonify(resp), 200

    @staticmethod
    def validate(data, uid, db):
        errors = []
        allowedDepths = [.3, .5, 1]
        wqise = WaterQualityIntegrationServiceEvent(uid)

        # validate source (ie groupCode)
        if 'source' not in data:
            errors.append('invalid data set: source is required')
        else:
            g = group.get_group_by(db, ['Id', 'Name', 'Code', 'BenthicMethod'], 'Code', data['source'])
            if g is None:
                errors.append('invalid data: source could not be found')
            else:
                wqise.group = g

        # validate station
        if 'station' not in data:
            errors.append('invalid data set: station is required')
        else:
            s = station.get_station_by(db, ['Id', 'Name', 'Code'], 'Code', data['station'])
            if s is None:
                errors.append('invalid data: station could not be found')
            else:
                wqise.station = s

        # validate datetime
        if 'datetime' not in data:
            errors.append('invalid data set: datetime is required')
        else:
            dateTime = datetimeutil.getdatetime(data['datetime'])

            if dateTime is None:
                errors.append('invalid data: datetime format is invalid')
            else:
                wqise.dateTime = datetime.strftime(dateTime, '%Y-%m-%dT%H:%M:%S')

        # validate comments
        comments = ''
        if 'comments' not in data:
            errors.append('invalid data set: comments is required')
        else:
            comments = data['comments']

        conditions = []
        if 'conditions' in data:
            conditions = data['conditions']

        monitors = []
        if 'monitors' in data:
            monitors = data['monitors']

        qualities = []
        if 'qualities' in data:
            qualities = data['qualities']

        if len(qualities) == 0 and len(conditions) == 0 and len(monitors):
            errors.append('event must have at least one of the following sample sets with sample data:'
                          'conditions, monitors, qualities')

        # return any errors at this point. no need to process any further
        if len(errors) > 0:
            return None, errors

        # check to see if a benthic event already exists
        print(f'group: {wqise.group.Id}, station: {wqise.station.Id}, datetime: {wqise.dateTime}')
        wqe = event.get_event_by_group_station_datetime(
            db,
            ['Id'],
            wqise.group.Id,
            wqise.station.Id,
            wqise.dateTime
        )
        if wqe is not None:
            return None, ['event exists: delete existing event before resubmitting']

        # setup a new event
        wqise.event = event.Event(**{
            'DateTime': wqise.dateTime,
            'Comments': comments,
            'StationId': wqise.station.Id,
            'GroupId': wqise.group.Id,
            'CreatedBy': uid,
            'CreatedDate': datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S'),
            'ModifiedBy': uid,
            'ModifiedDate': datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S')
        })

        # validate qualities
        idx = 0
        for q in qualities:
            # verify correct keys
            if 'name' not in q or 'value' not in q or 'id' not in q:
                errors.append(f'quality {idx}: invalid data. missing name, value, depth, or id keys')
            else:
                wqSample = WaterQualityIntegrationServiceQualitySample(q['name'], q['value'], q['id'])

                # check if value is a number
                if not number.isfloat(q['value']):
                    errors.append(f'quality {idx}: value is not a number for parameter_type quality')
                else:
                    wqSample.value = float(q['value'])

                # check if depth is a number
                if 'depth' in q:
                    if not number.isfloat(q['depth']):
                        errors.append(f'quality {idx}: depth is not a number for parameter_type quality')
                    else:
                        wqSample.depth = float(q['depth'])

                if 'publish' in q:
                    wqSample.publish = q['publish'] is True

                # check if value is a number
                if not number.isint(q['id']):
                    errors.append(f'quality {idx}: id is not an int for parameter_type quality')
                else:
                    sid = int(q['id'])
                    if sid < 1 or sid > 2:
                        errors.append(f'quality {idx}: id is not equal to 1 or 2')

                # check if valid parameter name
                param = parameter.get_parameter_by(
                    db,
                    ['Id', 'NonfatalLowerRange', 'NonfatalUpperRange', 'requiresSampleDepth',
                     'isCalibrationParameter', ],
                    'Code',
                    q['name']
                )
                if param is None:
                    errors.append(f'quality {idx}: has an invalid name for parameter type of quality')
                else:
                    wqSample.paramId = param.Id

                    # validate problem if exists allowed to be null as long as not provided (1270)
                    if 'problem' in q and q['problem'] != "":
                        prob = problem.get_problem_by(db, ['Id'], 'Code', q['problem'])
                        if prob is None:
                            errors.append(f'quality {idx}: problem provided but is not valid')
                        else:
                            wqSample.problem = prob

                    # validate qualifier if exists allowed to be null as long as not provided
                    if 'qualifier' in q and q['qualifier'] != "":
                        qual = qualifier.get_qualifier_by(db, ['Id'], 'Code', q['qualifier'])
                        if qual is None:
                            errors.append(f'quality {idx}: qualifier provided but is not valid')
                        else:
                            wqSample.qualifier = qual

                    # validate depth (1221)
                    if wqSample.depth is None and not param.isCalibrationParameter:
                        errors.append(f'quality {idx}: sample depth is null but required for associated parameter type')

                    # validate depth is an allowed depth
                    # nanticoke and spa creek conservancy are only groups that this error does not apply
                    nanticoke = 62
                    spaCreek = 114
                    if wqise.group.Id != nanticoke and wqise.group.Id != spaCreek \
                            and not param.isCalibrationParameter \
                            and wqSample.depth not in allowedDepths:
                        errors.append(f'quality {idx}: sample depth is not a valid depth (.3, .5, 1)')

                    # validate lower limit (1246)
                    if param.NonfatalLowerRange is not None and wqSample.value < param.NonfatalLowerRange:
                        errors.append(f'quality {idx}: value provided is lower than the lower range')

                    # validate upper limit (1257)
                    if param.NonfatalUpperRange is not None and wqSample.value > param.NonfatalUpperRange:
                        errors.append(f'quality {idx}: value provided is higher than the higher range')

                # check if this sample already exists in data set and if not append it to the event qualities
                if wqSample.paramId is not None:
                    found = False
                    for eq in wqise.qualities:
                        if eq.paramId == wqSample.paramId and eq.sampleId == wqSample.sampleId:
                            found = True
                            break

                    if found:
                        errors.append(f'quality {idx} has a duplicate entry for this parameter name and/or id')
                    else:
                        wqise.qualities.append(wqSample)

            idx += 1

        # validate monitors
        idx = 0
        for m in monitors:
            # verify correct keys
            if 'name' not in m or 'value' not in m:
                errors.append(f'monitor {idx}: invalid data. missing name or value keys')
            else:
                monitorSample = WaterQualityIntegrationServiceSample(m['name'], m['value'])

                # verify user code
                anu = asp_net_user.get_asp_net_user_by(db, ['Id'], 'Code', m['name'])
                if anu is None:
                    errors.append(f'monitor {idx}: does not match a user code')
                else:
                    monitorSample.paramId = anu.Id

                # check if value is a number
                if not number.isfloat(m['value']):
                    errors.append(f'monitor {idx}: value is not a number for parameter_type monitor')

                # check for duplicate
                if monitorSample.paramId is not None:
                    found = False
                    for em in wqise.monitors:
                        if em.paramId == monitorSample.paramId:
                            found = True
                            break

                    if found:
                        errors.append(f'monitor {idx}: a duplicate entry for this parameter name')
                    else:
                        wqise.monitors.append(monitorSample)

        # validate conditions
        idx = 0
        for c in conditions:
            # verify correct keys
            if 'name' not in c or 'value' not in c:
                errors.append(f'condition {idx}: invalid data. missing name or value keys')
            else:
                condSample = WaterQualityIntegrationServiceSample(c['name'], c['value'])

                # check if value is empty
                if c['value'].strip() == '':
                    errors.append(f'condition {idx}: value is empty for parameter_type condition')

                # check if valid parameter name
                wqc = condition.get_condition_by(db, ['Id', 'isCategorical'], 'Code', c['name'])
                if wqc is None:
                    errors.append(f'condition {idx}: has an invalid parameter_name for parameter_type of condition')
                else:
                    condSample.paramId = wqc.Id

                    # check if valid categorically
                    if wqc.isCategorical:
                        bcc = condition_category.get_condition_category_by_condition_id_category(
                            db,
                            ['Id'],
                            wqc.Id,
                            c['value']
                        )
                        if bcc is None:
                            errors.append(f'condition {idx}: invalid condition value')

                # check if this sample already exists in data set and if not append it to the event tallies
                if condSample.paramId is not None:
                    found = False
                    for ec in wqise.conditions:
                        if ec.paramId == condSample.paramId:
                            found = True
                            break

                    if found:
                        errors.append(f'condition {idx}: a duplicate entry for this parameter name')
                    else:
                        wqise.conditions.append(condSample)

        return wqise, errors

    @staticmethod
    def insert(wqise, db):
        errors = []
        eventId = None

        db.autocommit = False

        try:
            print(vars(wqise.event))
            eventId = event.insert_event(db, wqise.event)
            print(f'wq eventId: {eventId}')

            # loop through quality samples and insert
            for q in wqise.qualities:
                wqs = sample.Sample(**{
                    'Value': q.value,
                    'Depth': None if q.depth is None else q.depth,
                    'SampleId': q.sampleId,
                    'Comments': wqise.event.Comments,
                    'EventId': eventId,
                    'ParameterId': q.paramId,
                    'ProblemId': None if q.problem is None else q.problem.Id,
                    'QaFlagId': 2 if q.publish else 1,
                    'QualifierId': None if q.qualifier is None else q.qualifier.Id,
                    'CreatedBy': wqise.userId,
                    'CreatedDate': wqise.event.CreatedDate,
                    'ModifiedBy': wqise.userId,
                    'ModifiedDate': wqise.event.ModifiedDate,
                })
                try:
                    sample.insert_sample(db, wqs)
                except Exception as err:
                    errors.append(str(err))

            # loop through monitor samples and insert
            for m in wqise.monitors:
                ml = monitor_log.MonitorLog(**{
                    'UserId': m.paramId,
                    'Hours': m.value,
                    'BenthicEventId': eventId,
                    'CreatedBy': wqise.userId,
                    'CreatedDate': wqise.event.CreatedDate,
                    'ModifiedBy': wqise.userId,
                    'ModifiedDate': wqise.event.ModifiedDate,
                })
                try:
                    monitor_log.insert_monitor_log(db, ml)
                except Exception as err:
                    errors.append(str(err))

            # loop through condition samples and insert
            for c in wqise.conditions:
                ec = event_condition.EventCondition(**{
                    'EventId': eventId,
                    'ConditionId': c.paramId,
                    'Value': c.value
                })
                try:
                    event_condition.insert_event_condition(db, ec)
                except Exception as err:
                    errors.append(str(err))

        except Exception as err:
            errors.append(str(err))

        # no insertion errors occurred. commit
        if len(errors) == 0:
            print("committing...")
            db.cursor.commit()

        return eventId, errors


class WaterQualityIntegrationServiceEvent:
    def __init__(self, uid):
        self.userId = uid
        self.publish = False
        self.event = None
        self.group = None
        self.station = None
        self.dateTime = None
        self.comments = None

        self.conditions = []
        self.monitors = []
        self.qualities = []


class WaterQualityIntegrationServiceSample:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.paramId = None


class WaterQualityIntegrationServiceQualitySample:
    def __init__(self, name, value, sid):
        self.name = name
        self.value = value
        self.sampleId = sid
        self.publish = False
        self.paramId = None
        self.depth = None
        self.qualifier = None
        self.problem = None

#################################
# benthic samples api integration
#################################
# def service(app, roles):
#     @app.route('/integration/waterquality', methods=['POST'])
#     def waterquality_service():
#         if request.method == 'POST':
#             data = request.json
#             return post(data)
#
#         resp = {'status': 400, 'error': 'method not allowed'}
#         return jsonify(resp), 200
#
#
# def post(data):
#     # verify the data
#     if not isinstance(data, list):
#         return jsonify({'error': 'invalid data set'}), 400
#
#     if len(data) == 0:
#         return jsonify({'error': 'empty data set'}), 400
#
#     # fetch the db connection used to validate data
#     db = request.environ['db']
#
#     idx = 0
#     errors = []
#     records = []
#     for d in data:
#         print(f'--{idx}: {d}')
#         err = validate(d, idx, db)
#         if len(err) == 0:
#             records += d
#         else:
#             errors += err
#
#         idx += 1
#
#     # errors validating data return with validation errors
#     if len(errors) > 0:
#         return jsonify({'error': 'data parsing error(s)', 'errors': errors})
#
#     resp = {'status': 200}
#     return jsonify(resp), 200
#
#
# def validate(d, i, db):
#     errors = []
#
#     # validate source
#     if 'source' not in d:
#         errors.append(f'record: {i} is missing key source')
#     else:
#         print('todo: verify allowed source')
#
#     # validate station
#     if 'station' not in d:
#         errors.append(f'record: {i} is missing key station')
#     else:
#         print('todo: verify allowed station')
#
#     # validate date and time
#     if 'date' not in d or 'time' not in d:
#         errors.append(f'record: {i} is missing key date and/or time')
#     else:
#         print('todo: verify allowed date/time')
#
#     # validate parameter type
#     if 'parameter_type' not in d:
#         errors.append(f'record: {i} is missing key parameter_type')
#     else:
#         print('todo: verify allowed parameter_type')
#
#     # validate parameter name
#     if 'parameter_name' not in d:
#         errors.append(f'record: {i} is missing key parameter_name')
#     else:
#         print('todo: verify allowed parameter_name')
#
#     # validate value
#     if 'value' not in d:
#         errors.append(f'record: {i} is missing key value')
#     else:
#         print('todo: verify allowed value')
#
#     # validate comments
#     if 'comments' not in d:
#         errors.append(f'record: {i} is missing key comments')
#     else:
#         print('todo: verify allowed comments')
#
#     return errors
