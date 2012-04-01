from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    relationship,
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

class Bill(Base):
    __tablename__ = "bill"
    id = Column(Integer, primary_key=True)

    # The "primary" user on a bill is the user that is invoicing
    # others for money. That user "paid" the bill upstream, and is
    # now requisitioning money for it.
    primary_user_id = Column(Integer, ForeignKey('user.id'))
    primary_user = relationship("User")

    total = Column(Integer)

class BillShare(Base):
    __tablename__ = "billshare"
    id = Column(Integer, primary_key=True)

    billshare_user_placeholder_id = Column(Integer, ForeignKey('billshare_user_placeholder.id'))
    billshare_user_placeholder = relationship("BillShareUserPlaceholder")

    bill_id = Column(Integer, ForeignKey("bill.id"))
    bill = relationship("Bill")

    amount = Column(Integer)

class BillShareUserPlaceholder(Base):
    __tablename__ = "billshare_user_placeholder"
    id = Column(Integer, primary_key=True)
    encrypted_id = Column(Text, unique=True)
    name = Column(Text)

    claimed_user_id = Column(Integer, ForeignKey('user.id'))
    claimed_user = relationship("User")

    def __init__(self, name=None, user=None):
        self.name = name
        if user:
            self.claimed_user_id = user.id

    def __getattribute__(self, attr):
        if attr == "name" and self.claimed_user:
            return self.claimed_user.name
        else:
            return object.__getattribute__(self, attr)

    def encrypt(self):
        # TODO(fhats): This should probably change so we don't use the same encryption algorithm/keyspace
        # for encrypted placeholder IDs as password hashing.
        self.encrypted_id = pwd_context.encrypt(str(self.id))

    def claim(self, user):
        self.claimed_user_id = user.id
