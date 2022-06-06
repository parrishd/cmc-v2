from flask import jsonify, request
from datetime import datetime

from api.util import validation
from api.model import group
from api.middleware import role_validation


class GroupService:

    def __init__(self, app):
        self.group_service_get_roles = ['Admin', 'Officer', 'Member']
        self.group_service_delete_roles = ['Admin', 'Officer', 'Member']
        app.route('/group/<gid>', methods=['GET', 'DELETE', 'PUT'])(self.param_service)

        self.group_service_post_roles = ['Admin', 'Officer', 'Member']
        app.route('/group', methods=['POST'])(self.param_post_service)

        self.group_list_service_roles = ['Admin', 'Officer', 'Member']
        app.route('/group/list', methods=['GET'])(self.param_list_service)
