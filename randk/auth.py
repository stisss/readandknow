"""@package docstring
Pakiet auth zawiera funkcje związane z obsługą rejestracji, logowania i uwierzytelniania.
"""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from randk.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Funkcja obsługująca formularz rejestracji w systemie Read&Know
    
    Return:
        Renderuje szablon html dla rejestracji
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        last_name = request.form['last_name']
        institution = request.form['institution']
        db = get_db()
        error = None
        
        if not email:
            error = 'E-mail address is required'
        elif not password:
            error = 'Password is required'
        elif not email or not name or not last_name:
            error = 'Fill required fields'
        elif not institution:
            institution = ''
        elif db.execute(
            'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'E-mail address {} is already registered'.format(email)
        
        if error is None:
            db.execute(
                'INSERT INTO user (email, password, name, last_name, institution) '
                'VALUES (?,?,?,?,?)',
                (email, generate_password_hash(password), name, last_name, institution)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Funkcja obsługująca formularz logowania w systemie Read&Know
    
    Return:
        Renderuje szablon html dla logowania
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect e-mail address.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Funkcja ładująca z bazy danych zalogowanego użytkownika za pomocą numeru id uzyskanego z sesji.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Funkcja służąca do wylogowania z systemu.
    
    Return:
        Wylogowuje i przekierowuje użytkownika na stronę główną
    """
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """Funkcja autoryzująca użytkownika
    
    Argumenty:
        view: aktualny widok wymagający autoryzacji
    Return:
        Renderuje szablon html, do którego wymagana była autoryzacja lub szablon html logowania
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


