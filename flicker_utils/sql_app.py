from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, BigInteger, Sequence, CheckConstraint
from typing import Iterable
import pickle

Base = declarative_base()


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, Sequence('settings_id_seq'), primary_key=True, nullable=False)
    prefix = Column(String)
    currency_name = Column(String)
    currency_plrname = Column(String)
    currency_sign = Column(String)
    owner = Column(String)

    @property
    def owners(self):
        return pickle.loads(self.owner)

    @owners.setter
    def owners(self, value: Iterable):
        self.owner = pickle.dumps(list(value))


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, Sequence('currency_id_seq'), primary_key=True, nullable=False)
    username = Column(String, nullable=True)
    userid = Column(BigInteger, nullable=False, unique=True)
    amount = Column(Integer, CheckConstraint('amount >= 0'), nullable=False)

    def __repr__(self):
        return f"<User(name={self.username}-{self.userid}, amount={self.amount})>"
