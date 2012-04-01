from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(Text, unique=True)
    password_hash = Column(Text)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = pwd_context.encrypt(password)

    def check_password(self, attempted_password):
        return pwd_context.verify(attempted_password, self.password_hash)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
