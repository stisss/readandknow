"""@package docstring
Pakiet blog zawiera funkcje odpowiedzialne za dostarczanie danych dla widoków aplikacji i 
zapisywanie danych podanych przez użytkownika do bazy danych.
"""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from randk.auth import login_required
from randk.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    """Funkcja obsługująca stronę główną. Pobiera posty z bazy danych.
    
    Return:
        Renderuje szablon html dla strony głównej
    """
    db = get_db()
    articles = db.execute(
        'SELECT article.id, title, description, body, article.created, author_id, name, last_name'
        ' FROM article JOIN user u ON article.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=articles)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Funkcja zawierająca obsługę tworzenia nowego artykułu. Łączy się z bazą danych i umieszcza w niej nowy artykuł.
    
    Return:
        W przypadku zapytania POST: Przekierowuje użytownika na stronę główną
        W przypadku zapytania GET: Renderuje szablon html dla tworzenia artykułu
    """
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
    """Getter artykułu, pobiera artykuł o podanym id z bazy danych
    Argumenty:
        id:             id artykułu
        check_author:   domyślnie sprawdza czy artykuł jest przypisany do zalogowanego użytkownika
    Return:
        article:        artykuł o podanym id
    """    
    article = get_db().execute(
        'SELECT p.id, title, description, body, created, author_id, name, last_name'
        ' FROM article p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if article is None:
        abort(404, "Article id {0} doesn't exist.".format(id))

    if check_author and article['author_id'] != g.user['id']:
        abort(403)

    return article

def get_user(id):
    """Getter użytkownika, pobiera użytkownika o podanym id z bazy danych
    Argumenty:
        id:             id użytkownika 
    Return:
        user:        użytkownik o podanym id
    """  
    user = get_db().execute(
        'SELECT id, email, name, last_name, institution'
        ' FROM user'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))
    
    return user


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Funkcja zawierająca obsługę modyfikacji artykułu. Pobiera artykuł z bazą danych i zapisuje w niej edytowaną wersję.
    Argumenty:
        id:     id artykułu
    Return:
        W przypadku zapytania POST: Przekierowuje użytownika na stronę główną
        W przypadku zapytania GET: Renderuje szablon html dla edycji artykułu
    """
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
    """Funkcja zawierająca obsługę usuwania artykułu. Łączy się z bazą danych i usuwa artykuł o podanym id.
    
    Argumenty:
        id:     id artykułu    
    Return:
        Przekierowuje użytownika na stronę główną
    """
    get_article(id)
    db = get_db()
    db.execute('DELETE FROM article WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/save', methods=('POST',))
@login_required
def save(id):
    """Funkcja zawierająca obsługę umieszczania artykułu w zakładce "Zapisane". Umieszcza w bazie danych artykuł o podanym id.
    
    Argumenty:
        id:     id artykułu    
    Return:
        Przekierowuje użytownika na stronę podglądu zapisywanego artykułu
    """
    db=get_db()

    check_duplicates = db.execute(
        'SELECT * FROM saved s'
        ' WHERE s.id_user=? AND s.id_article=?', (g.user['id'], id)
    ).fetchone()

    if check_duplicates is None:
        db.execute('INSERT INTO saved VALUES (?, ?)', (g.user['id'], id))
        db.commit()
    else:
        flash('Ten artykuł został już zapisany')
    return redirect(url_for('blog.display_article', id=id))
    
@bp.route('/saved')
@login_required
def saved():
    """Funkcja zawierająca obsługę wyświetlania zapisanych artykułów. Pobiera artykuły z bazy danych.
    
    Return:
        Renderuje szablon html dla widoku zapisanych artykułów
    """
    articles = get_db().execute(
        'SELECT a.id, title, description, body, a.created, author_id, name, last_name'
        ' FROM article a JOIN user u ON a.author_id = u.id JOIN saved s ON s.id_article=a.id'
        ' WHERE s.id_user = ?'
        ' ORDER BY created DESC', (g.user['id'],)).fetchall()
    x = get_db().execute('SELECT * FROM saved').fetchall()
    if articles is not None:
        print(articles)
        print(g.user['id'])
        print(x)
    return render_template('blog/saved.html', articles=articles)


def get_users_articles(author_id):
    """Getter artykułów danego użytkownika, pobiera artykuły autora o podanym id z bazy danych.
    
    Argumenty:
        author_id:             id autora postów
    Return:
        articles:        artykuły autora o podanym id
    """ 
    articles = get_db().execute(
        'SELECT p.id, title, description, body, created, author_id'
        ' FROM article p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ?',
        (author_id,)
    ).fetchall()
    
    return articles


@bp.route('/<int:id>/profile')
def display_profile(id):
    """Funkcja zawierająca obsługę wyświetlania profilu użytkownika.
    
    Return:
        Renderuje szablon html dla widoku profilu użytkownika
    """
    user = get_user(id)
    articles = get_users_articles(id)
    return render_template('blog/profile.html', articles=articles, user=user)


@bp.route('/<int:id>/article', methods=('GET',))
def display_article(id):
    """Funkcja zawierająca obsługę wyświetlania danego artykułów.
    
    Argumenty:
        id:     id wyświetlanego artykułu
    Return:
        Renderuje szablon html dla widoku wybranego artykułu
    """
    article = get_article(id, check_author=False)
    user = get_user(article['author_id'])
    return render_template('blog/article.html', article=article, author=user)