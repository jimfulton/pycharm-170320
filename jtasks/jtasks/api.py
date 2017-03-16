from flask import g, request
from flask.json import jsonify
from sqlalchemy import text

from . import email, models
from .app import app

# site creation is external process. Name will come from domain
site_name = "demo"

def get_site():
    [site] = g.session.query(models.Site).filter_by(name=site_name).all()
    return site

@app.route('/', methods=['GET'])
def load():
    return jsonify(get_site())

@app.route('/users', methods=['POST'])
def add_user():
    site = get_site()
    user = models.User(site, **request.get_json(True))
    g.session.add(user)
    return jsonify(dict(id=user.id))


@app.route('/boards', methods=['POST'])
def add_board():
    site = get_site()
    board = models.Board(site, **request.get_json(True))
    g.session.add(board)
    return jsonify(dict(id=board.id))

@app.route('/boards/<int:id>', methods=['GET'])
def get_board(id):
    site = get_site()
    [board] = (g.session
                 .query(models.Board)
                 .filter_by(id=id, site_id=site.id)
                 .all())
    return jsonify(dict(data=board.load()))

@app.route('/boards/<int:board_id>/states/<string:id>/tasks', methods=['POST'])
def add_task(board_id, id):
    site = get_site()
    [board] = (g.session
                 .query(models.Board)
                 .filter_by(id=board_id, site_id=site.id)
                 .all())

    state = board.states[id]
    data = request.get_json(True)
    assigned_id = data.get('assigned_id')
    if assigned_id is not None:
        [assigned] = (g.session
                       .query(models.User)
                       .filter_by(site_id=site.id, id=assigned_id)
                       .all())
        email.send(assigned.email, task=id)
    task = models.Task(board, id, **data)
    g.session.add(task)
    return jsonify(dict(id=task.id))


if __name__ == '__main__':
    app.run()
