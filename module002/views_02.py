from flask import Blueprint, render_template, abort
from flask_login import login_required
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import User, get_db, Course, Follow, ParticipationCode, ParticipationRedeem, Comment
from sqlalchemy import or_, and_
from module002.forms import *
import random


module002 = Blueprint("module002", __name__,static_folder="static",template_folder="templates")
db = get_db()



@module002.route('/')
@login_required
def module002_index():
    follows = Follow.query.filter_by(user_id=current_user.id)
    return render_template("module002_index.html",module='module002', rows=follows)

def _post_comment(course_id, form):
    if form.validate_on_submit():
        print(request.form)
        comment = Comment(user_id=current_user.id,
                          course_id=course_id,
                          comment=request.form.get('comment'))
        db.session.add(comment)
        db.session.commit()
        flash("Comment added!")
    else:
        flash("Error adding comment!")
    return redirect(url_for('module002.module002_forum', course_id=course_id))

def _get_comments(course_id, form):
    follows = Follow.query.filter_by(user_id=current_user.id)
    msgs = Comment.query.filter_by(course_id=course_id).all()

    msg_user_ids = tuple(msg.user_id for msg in msgs)
    users = User.query.filter(User.id.in_(msg_user_ids)).all()
    users = {user.id: user for user in users}

    return render_template("module002_forum.html", module='module002', course_id=course_id,
                           form=form, followed=follows, msgs=msgs, user=current_user, users=users)

@module002.route('/forum/<course_id>', methods=['GET', 'POST'])
@login_required
def module002_forum(course_id):
    user_course = Follow.query.filter_by(user_id=current_user.id)\
                              .filter_by(course_id=course_id)\
                              .first()

    if user_course is None:
        abort(403)

    form = CommentForm()
    if request.method == 'GET':
        return _get_comments(course_id, form)
    elif request.method == 'POST':
        return _post_comment(course_id, form)


@module002.route('/change', methods=['POST'])
@login_required
def module002_update_comment():
    hide_comment = request.form.get('show_comment')
    comment_id = request.form.get('comment_id')

    comment = Comment.query.filter_by(id=comment_id)\
                           .filter_by(user_id=current_user.id)\
                           .first_or_404()

    if hide_comment == "true" : #Hide comment true ==> guardamos 0 ==> para no mostrar
        comment.shows = 0
    else:
        comment.shows = 1

    db.session.commit()
    return "Comment update", 204




@module002.route('/test')
def module002_test():
    return 'OK'




