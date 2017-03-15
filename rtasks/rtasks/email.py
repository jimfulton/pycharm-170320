import contextlib
import flask
import pq

def create_queue_table(engine):
    with contextlib.closing(engine.raw_connection()) as conn:
        pq.PQ(conn).create()

def send(to, **kw):
    conn = flask.g.session.connection().connection
    with contextlib.closing(conn.cursor()) as cursor:
        pq.Queue('email', cursor=cursor).put(dict(to=to, **kw))
