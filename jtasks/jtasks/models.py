import datetime
import json
import os

from sqlalchemy import (
    BigInteger, Boolean, Column, Integer, ForeignKey, Text, text,
    )
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship, backref
import sqlalchemy.orm.session

from . import jsonb

object_session = sqlalchemy.orm.session.Session.object_session

Base = sqlalchemy.ext.declarative.declarative_base()

class Identified:
    # These objects need their ids before commit
    id = Column(BigInteger, primary_key=True)

    __tablename__ = None

    def set_id(self, session):
        [[self.id]] = session.execute("select nextval('%s_id_seq')" %
                                      self.__tablename__)

class Site(Base):
    __tablename__ = 'site'

    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    boards = relationship('Board', backref='site')
    users = relationship('User', backref='site')

    def __init__(self, name):
        self.name = name

    def json_reduce(self):
        return dict(boards=self.boards, users=self.users)

class User(Base, Identified):
    __tablename__ = 'user'

    email = Column(Text, nullable=False)
    site_id = Column(BigInteger, ForeignKey('site.id'))
    admin = Column(Boolean, default=False)

    def __init__(self, site, email):
        self.set_id(object_session(site))
        self.site = site
        self.email = email

    def json_reduce(self):
        return dict(id=self.id, email=self.email, )

class Board(Base, Identified):
    __tablename__ = 'board'

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    site_id = Column(BigInteger, ForeignKey('site.id'), nullable=False)
    states = Column(jsonb.JSONB())

    def __init__(self, site, title, description=''):
        session = object_session(site)
        self.set_id(session)
        self.site = site # SUBTLE: can use magic because site existed
        self.title = title
        self.description = description
        self.initialize_states(session)

    def initialize_states(self, session):
        with open(os.path.join(os.path.dirname(__file__), 'states.json')) as f:
            state_data = json.load(f)

        i = 0
        states = {}
        for state in state_data:
            i += 1
            if isinstance(state, str):
                state = dict(title=state)
            substates = state.pop("substates", ())
            state['order'] = state['id'] = i
            states[str(i)] = state
            for sub in substates:
                i += 1
                sub['parent_id'] = state['id']
                states[str(i)] = sub

        self.states = states

    def json_reduce(self):
        return dict(id=self.id, title=self.title, description=self.description)

    def load(self):
        return dict(states=self.states, tasks=self.tasks)

    @property
    def tasks(self):
        return (object_session(self)
                .query(Task)
                .from_statement(text("""
                select *
                from task
                where "ATTRS" @> ('{"board_id": ' || :board_id || '}')::jsonb
                """).params(board_id=self.id))
                .all())

class Task(Base, jsonb.Object, Identified):
    __tablename__ = 'task'

    def __init__(self, board, state_id, title, order,
                 description='', assigned=None, size=1, blocked='',
                 parent_id=None):
        jsonb.Object.__init__(self)
        self.set_id(object_session(board))
        self.board_id = board.id
        self.state_id = state_id
        self.title = title
        self.order = order
        self.description = description
        self.assigned = assigned
        self.size = size
        self.blocked = blocked
        self.created = datetime.datetime.utcnow().isoformat()
