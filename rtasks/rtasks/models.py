import datetime
import json
import os

from sqlalchemy import (
    BigInteger, Boolean, Column, Integer, ForeignKey, Text, TIMESTAMP
    )
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship, backref
import sqlalchemy.orm.session

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
    tasks = relationship('Task', backref='assigned')

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
    states = relationship('State')
    site_id = Column(BigInteger, ForeignKey('site.id'), nullable=False)

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

        order = 0
        for state in state_data:
            order += 1
            if isinstance(state, str):
                state = dict(title=state)
            substates = state.pop("substates", ())
            state = State(session, self, order, **state)
            session.add(state)
            for sub in substates:
                order += 1
                sub['parent'] = state
                session.add(State(session, self, order, **sub))

    def json_reduce(self):
        return dict(id=self.id, title=self.title, description=self.description)

    def load(self):
        return dict(states=self.states)

class Task(Base, Identified):
    __tablename__ = 'task'

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    assigned_id = Column(BigInteger, ForeignKey('user.id'))
    archived = Column(Boolean, default=False)
    complete = Column(Boolean, default=False)
    order = Column(Integer, nullable=False)
    size = Column(Integer, default=1)
    blocked = Column(Text)
    state_id = Column(Integer, ForeignKey('state.id'))
    parent_id = Column(Integer, ForeignKey('task.id'))

    def __init__(self, state, title, order,
                 description='', assigned=None, size=1, blocked='',
                 parent_id=None):
        self.set_id(object_session(state))
        self.state = state
        self.title = title
        self.order = order
        self.description = description
        self.assigned = assigned
        self.size = size
        self.blocked = blocked

    def json_reduce(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            created=self.created,
            assigned=self.assigned,
            complete=self.complete,
            order=self.order,
            size=self.size,
            blocked=self.blocked,
            state_id=self.state_id,
            parent_id=self.parent_id,
        )

class State(Base, Identified):
    __tablename__ = 'state'

    # override to make parent backref def below work:
    id = Column(BigInteger, primary_key=True)
    title = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    working = Column(Boolean, default=False)
    complete = Column(Boolean, default=False)
    board_id = Column(Integer, ForeignKey('board.id'))
    parent_id = Column(Integer, ForeignKey('state.id'))
    children = relationship('State',
                            backref=backref('parent',
                                            remote_side=[id]))
    tasks = relationship('Task', backref='state')

    def __init__(self, session, board, order, title,
                 working=False, complete=False, parent=None):
        self.set_id(session)
        self.board_id = board.id # NOTE: use id here because board is new
        self.order = order
        self.title = title
        self.working = working
        self.complete = complete
        if parent is not None:
            self.parent_id = parent.id # NOTE: use id here because ...

    def json_reduce(self):
        return dict(
            id=self.id,
            title=self.title,
            order=self.order,
            working=self.working,
            complete=self.complete,
            parent_id = self.parent_id,
            tasks=self.tasks,
            )