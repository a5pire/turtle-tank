import functools
from werkzeug.security import check_password_hash, generate_password_hash
from turtletank.db import get_db
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM aquarist WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'Aquarist {username} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO aquarist (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        aquarist = db.execute(
            'SELECT * FROM aquarist WHERE username = ?', (username,)
        ).fetchone()

        if aquarist is None:
            error = 'Username is incorrect or doesnt exist.'
        elif not check_password_hash(aquarist['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['aquarist_id'] = aquarist['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    aquarist_id = session.get('aquarist_id')

    if aquarist_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM aquarist WHERE id = ?', (aquarist_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
