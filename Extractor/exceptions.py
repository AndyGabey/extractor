class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, hint='', status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.hint = hint
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv



