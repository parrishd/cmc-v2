from werkzeug.wsgi import ClosingIterator


class DBCloseMiddleware:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, close_response):
        print('-- DBCloseMiddleware')
        iterator = self.app(environ, close_response)
        self.db = environ['db']
        return ClosingIterator(iterator, [self.close_db])

    def close_db(self):
        if self.db is not None:
            self.db.close()
