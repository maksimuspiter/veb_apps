from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from prog1.pr1.auth import login_required
from prog1.pr1.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/admin/all_users')
def show_all_users():
    user_id = session.get('user_id')
    if user_id == 1:
        """
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' ORDER BY p.id'
        """

        db = get_db()
        users = db.execute(
            #'SELECT * FROM user'
            'SELECT p.id, title, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY p.id'
        ).fetchall()
        return render_template('blog/show_users.html', users=users)
    else:
        flash("You don't have permissions to access this page")
        return redirect(url_for('blog.index'))


# @bp.route('/admin/user/<int:id_user>')
# def show_user(id_user: int):
#     user_id = session.get('user_id')
#     print(user_id)
#     if user_id == 1:
#
#         db = get_db()
#         user = db.execute(
#             'SELECT id, username FROM user WHERE id = ?', (id_user,)
#         )
#         print(user)
#         posts = db.execute(
#             'SELECT id, title, body, created'
#             ' FROM post WHERE author_id = ?'
#             ' ORDER BY created DESC', (id_user,)
#         ).fetchall()
#         return render_template('blog/show_user_by_id.html', user=user, posts=posts)
#     else:
#         flash("You don't have permissions to access this page")
#         return redirect(url_for('blog.index'))
