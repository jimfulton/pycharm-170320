import flask.json
import os
import sqlalchemy.orm

app = flask.Flask('rtasks')

class JSONEncoder(flask.json.JSONEncoder):

    def default(self, o):
        if hasattr(o, 'json_reduce'):
            return o.json_reduce()
        return flask.json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder
dsn = os.environ['TASKS_DSN']
engine = sqlalchemy.create_engine(dsn, isolation_level='SERIALIZABLE')
Session = sqlalchemy.orm.sessionmaker(bind=engine)

@app.before_request
def start_session():
    flask.g.session = Session()

@app.teardown_request
def stop_session(err=None):
    if err is None:
        flask.g.session.commit()
    else:
        flask.g.session.rollback()
    flask.g.session.close()

def setup_db():
    from . import models
    models.Base.metadata.create_all(engine)
    from . import email
    email.create_queue_table(engine)