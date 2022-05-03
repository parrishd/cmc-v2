import pyodbc

from flask import current_app, g
from flask.cli import with_appcontext


# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port


class DB:
    cursor = None

    server = ''
    port = '1433'
    database = ''
    username = ''
    password = ''

    def __init__(self, app, server, port, database, username, password):
        self.server = server
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def connect(self):
        try:
            conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ',' + self.port + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
            print('@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(f'connected to database: {self.server}')
            print('@@@@@@@@@@@@@@@@@@@@@@@@@')
            self.cursor = conn.cursor()
            return True
        except pyodbc.Error as ex:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(ex.args)
            print('!!!!!!!!!!!!!!!!!!!!!!!!!')
            return False

    def close(self):
        if self.cursor is not None:
            print('@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(f'closing connection for: {self.server}')
            print('@@@@@@@@@@@@@@@@@@@@@@@@@')
            self.cursor.close()
