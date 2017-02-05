import bcrypt
from sqlalchemy import Column, Integer, String, Boolean
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
        # N.B. the salt is tored with the password - no need to store separately.
        self.pw_hash = bcrypt.hashpw(password, pw_salt)

    def check_password(self, password):
        return bcrypt.checkpw(str(password), str(self.pw_hash))

    def __repr__(self):
        return '<User %r>' % (self.name)
