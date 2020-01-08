from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from randk.auth import login_required
from randk.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    articles = db.execute(
        'SELECT a.id, title, description, body, created, author_id, username'
        ' FROM article a JOIN user u ON a.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=articles)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO article (title, description, body, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_article(id, check_author=True):
    article = get_db().execute(
        'SELECT p.id, title, description, body, created, author_id, username'
        ' FROM article p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if article is None:
        abort(404, "Article id {0} doesn't exist.".format(id))

    if check_author and article['author_id'] != g.user['id']:
        abort(403)

    return article


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    article = get_article(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE article SET title = ?, description = ?, body = ?'
                ' WHERE id = ?',
                (title, description, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=article)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_article(id)
    db = get_db()
    db.execute('DELETE FROM article WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


def get_user(id):
    user = get_db().execute(
        'SELECT id, username, surname, last_name, email, institution'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if article is None:
        abort(404, "Article id {0} doesn't exist.".format(id))

    if check_author and article['author_id'] != g.user['id']:
        abort(403)

    return article
@bp.route('/<int:id>/delete', methods=('POST',))
def display_user(id):
    get_article(id)
    db = get_db()
    db.execute('DELETE FROM article WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))