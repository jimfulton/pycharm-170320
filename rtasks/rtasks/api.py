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

@app.route('/boards/<int:board_id>/states/<int:id>/tasks', methods=['POST'])
def add_task(board_id, id):
    site = get_site()
    [state] = (
        g.session
          .query(models.State)
          # Blech:
          # .filter_by(id=id, board_id=id)
          # .join(models.Board)
          # .filter_by(site_id=site.id)
          .from_statement(text("""
            select state.*
            from state join board on (state.board_id=board.id)
            where state.id = :id and
                  board.id = :board_id and
                  board.site_id = :site_id
            """).params(id=id, board_id=board_id, site_id=site.id))
          .all())

    data = request.get_json(True)
    assigned_id = data.pop('assigned_id', None)
    if assigned_id is not None:
        [assigned] = (g.session
                       .query(models.User)
                       .filter_by(site_id=site.id, id=assigned_id)
                       .all())
        data['assigned'] = assigned
        email.send(assigned.email, task=id)
    task = models.Task(state, **data)
    g.session.add(task)
    return jsonify(dict(id=task.id))


if __name__ == '__main__':
    app.run()
