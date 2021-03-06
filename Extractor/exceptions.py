class MaxRowsExceeded(Exception):
    def __init__(self, rows):
        Exception.__init__(self, '{} rows retrieved'.format(rows))
        self.rows = rows


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, hint='', status_code=None, payload=None):
        Exception.__init__(self, message)
        self.message = message
        self.hint = hint
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def __repr__(self):
        return self.message



