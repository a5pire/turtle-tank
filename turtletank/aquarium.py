from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from turtletank.auth import login_required
from turtletank.db import get_db

bp = Blueprint('aquarium', __name__)


@bp.route('/')
def index():
    db = get_db()
    tanks = db.execute(
        'SELECT t.id, name, length, width, depth, tank_owner, username'
        ' FROM tank t JOIN aquarist a ON t.tank_owner = a.id'
        ' ORDER BY name DESC'
    ).fetchall()
    return render_template('aquarium/index.html', tanks=tanks)


# creates a tank
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        length = request.form['length']
        width = request.form['width']
        depth = request.form['depth']
        volume = round((length * width) * depth / 1000000, 2)
        error = None

        if not name or length or width or depth or volume:
            error = 'Please enter required fields.'

        if error:
        # if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tank (name, length, width, depth, volume, tank_owner)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (name, g.user['id'])
            )
            db.commit()
            return redirect(url_for('aquarium.index'))

    return render_template('aquarium/create.html')


def get_tank(id, check_aquarist=True):
    tank = get_db().execute(
        'SELECT t.id, name, length, width, depth, volume, tank_owner'
        ' FROM tank t JOIN aquarist a ON t.tank_owner = a.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if tank is None:
        abort(404, "Tank id {0} doesn't exist.".format(id))

    if check_aquarist and tank['tank_owner'] != g.user['id']:
        abort(403)

    return tank


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    tank = get_tank(id)

    if request.method == 'POST':
        name = request.form['name']
        length = request.form['length']
        width = request.form['width']
        depth = request.form['depth']
        volume = round((length * width) * depth / 1000000, 2)
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tank SET name = ?, length = ?, width = ?, depth = ?, volume = ?'
                ' WHERE id = ?',
                (name, length, width, depth, volume, id)
            )
            db.commit()
            return redirect(url_for('aquarium.index'))

    return render_template('aquarium/update.html', post=tank)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_tank(id)
    db = get_db()
    db.execute('DELETE FROM tank WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('aquarium.index'))
