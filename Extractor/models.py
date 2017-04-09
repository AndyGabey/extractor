import bcrypt
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship

from Extractor.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    pw_hash = Column(String(60))

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self):
        return self.id

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        pw_salt = bcrypt.gensalt()
        # N.B. the salt is stored with the password - no need to store separately.
        self.pw_hash = bcrypt.hashpw(password, pw_salt)

    def check_password(self, password):
        return bcrypt.checkpw(str(password), str(self.pw_hash))

    def __repr__(self):
        return '<User {}>'.format(self.name)


association_table = Table('association', Base.metadata,
                          Column('left_id', Integer, ForeignKey('datasets.id')),
                          Column('right_id', Integer, ForeignKey('user_tokens.id'))
                          )


class Dataset(Base):
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    long_name = Column(String(100))

    start_date = Column(DateTime)
    end_date = Column(DateTime)
    time_res = Column(Integer)
    file_fmt = Column(String(100))
    date_col_name = Column(String(100))
    time_col_name = Column(String(100))
    datetime_fmt = Column(String(100))
    file_freq = Column(Enum('daily', 'yearly'))

    variables = relationship('Variable', backref='dataset')
    user_tokens = relationship('UserToken', secondary=association_table, backref='datasets')

    def __init__(self, name, long_name, start_date, end_date, time_res,
                 file_fmt, date_col_name,
                 time_col_name, datetime_fmt, file_freq):
        self.name = name
        self.long_name = long_name
        self.start_date = start_date
        self.end_date = end_date
        self.time_res = time_res
        self.file_fmt = file_fmt
        self.date_col_name = date_col_name
        self.time_col_name = time_col_name
        self.datetime_fmt = datetime_fmt
        self.file_freq = file_freq

    def __repr__(self):
        return '<Dataset {}>'.format(self.name)


class Variable(Base):
    __tablename__ = 'variables'

    id = Column(Integer, primary_key=True)
    var = Column(String(40))
    long_name = Column(String(100))
    units = Column(String(100))
    vartype = Column(String(100))
    dataset_id = Column(Integer, ForeignKey('datasets.id'))

    def __init__(self, var, long_name, units, vartype):
        self.var = var
        self.long_name = long_name
        self.units = units
        self.vartype = vartype

    def __repr__(self):
        return '<Variable {}>'.format(self.long_name)


class UserToken(Base):
    __tablename__ = 'user_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(10))
    expiry_date = Column(DateTime)
    max_request_time_hours = Column(Float)
    max_request_rows = Column(Integer)
    max_request_files = Column(Integer)
    notes = Column(String)

    dataset_id = Column(Integer, ForeignKey('datasets.id'))

    def __init__(self, token, expiry_date,
                 max_request_time_hours=12,
                 max_request_rows=100000,
                 max_request_files=5,
                 notes=''):
        self.token = token
        self.expiry_date = expiry_date
        self.max_request_time_hours = max_request_time_hours
        self.max_request_rows = max_request_rows
        self.max_request_files = max_request_files
        self.notes = notes

    def __repr__(self):
        return '<UserToken {}>'.format(self.token)
