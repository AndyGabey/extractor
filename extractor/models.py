import bcrypt

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from extractor.database import Base

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
        Column('right_id', Integer, ForeignKey('variables.id'))
    )


class Dataset(Base):
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    long_name = Column(String(100))

    start_date = Column(DateTime)
    end_date = Column(DateTime)
    time_res = Column(Integer)
    instrument = Column(String(100))
    level = Column(Integer)
    file_pattern = Column(String(100))
    date_col_name = Column(String(100))
    date_pattern = Column(String(100))
    time_col_name = Column(String(100))
    time_pattern = Column(String(100))

    # variables = relationship('Variable', backref='dataset')
    variables = relationship('Variable',
                             secondary=association_table,
                             backref='datasets')

    def __init__(self, name, long_name, start_date, end_date, time_res,
                 instrument, level, file_pattern, date_col_name, date_pattern, 
                 time_col_name, time_pattern):
        self.name = name
        self.long_name = long_name
        self.start_date = start_date
        self.end_date = end_date
        self.time_res = time_res
        self.instrument = instrument
        self.level = level
        self.file_pattern = file_pattern
        self.date_col_name = date_col_name
        self.date_pattern = date_pattern
        self.time_col_name = time_col_name
        self.time_pattern = time_pattern

    def __repr__(self):
        return '<Dataset {}>'.format(self.name)


class Variable(Base):
    __tablename__ = 'variables'

    id = Column(Integer, primary_key=True)
    var = Column(String(40))
    long_name = Column(String(100))
    units = Column(String(100))
    vartype = Column(String(100))

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
    notes = Column(String)

    def __init__(self, token, expiry_date, notes):
        self.token = token
        self.expiry_date = expiry_date
        self.notes = notes

    def __repr__(self):
        return '<UserToken {}>'.format(self.token)
