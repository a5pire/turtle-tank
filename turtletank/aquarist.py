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
        length = float(request.form['length'])
        width = float(request.form['width'])
        depth = float(request.form['depth'])
        error = None

        if not (name and length and width and depth):
            error = 'Please enter all fields.'

        if error is not None:
            flash(error)
        else:
            volume = round((length * width) * depth / 1000000, 2)

            db = get_db()
            db.execute(
                'INSERT INTO tank (tank_owner, name, length, width, depth, volume)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (g.user['id'], name, length, width, depth, volume)
                )

            db.commit()
            flash('New tank created!')

            return redirect(url_for('aquarium.index'))

    return render_template('aquarium/index.html')


# retrieves a tank from the db
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


# update tank based on aquarist id
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    tank = get_tank(id)

    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            length = float(request.form['length'])
            width = float(request.form['width'])
            depth = float(request.form['depth'])
            volume = round((length * width) * depth / 1000000, 2)
            db = get_db()
            db.execute(
                'UPDATE tank SET name = ?, length = ?, width = ?, depth = ?, volume = ?'
                ' WHERE id = ?',
                (name, length, width, depth, volume, id)
            )
            db.commit()
            flash('Tank updated!')

            return redirect(url_for('aquarium.index'))

    return render_template('aquarium/index.html', tank=tank)


# delete tank based on aquarist id
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_tank(id)
    db = get_db()
    db.execute('DELETE FROM tank WHERE id = ?', (id,))
    db.commit()
    flash('Tank deleted!')

    return redirect(url_for('aquarium.index'))
