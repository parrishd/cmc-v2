from flask import jsonify, request


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
