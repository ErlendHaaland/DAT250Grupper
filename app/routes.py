from flask import render_template, flash, redirect, url_for, abort
from flask_login import LoginManager, login_required, login_user, logout_user, fresh_login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, LoginForm, is_safe_url, User
from datetime import datetime
import os

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if form.login.is_submitted() and form.login.submit.data:
        user = query_db("SELECT * FROM Users WHERE username = ?", [form.login.username.data], one=True)
        if user is None:
            flash('Sorry, this user does not exist!')
        elif check_password_hash(user['password'], form.login.password.data):
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong password!')

    # Runs validation check after "Sign Up" button is pressed.
    elif form.register.is_submitted() and form.register.submit.data:
        if form.validate():
            query_db("INSERT INTO Users (username, first_name, last_name, password) VALUES(?, ?, ?, ?)",
                     [form.register.username.data, form.register.first_name.data, form.register.last_name.data,
                      generate_password_hash(form.register.password.data)])
            return redirect(url_for('index'))

        flash("Error during registration, one or more fields do not meet minimum requirements.")

    return render_template('index.html', title='Welcome', form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    form = PostForm()
    user = query_db("SELECT * FROM Users WHERE username=?", [username], one=True)
    if form.is_submitted():
        if form.image.data and allowed_file(form.image.data.filename):
            path = os.path.join(app.config['UPLOAD_PATH'], secure_filename(form.image.data.filename))
            form.image.data.save(path)
            query_db("INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?)",
                     [user['id'], form.content.data, secure_filename(form.image.data.filename), datetime.now()])
        else:
            flash("Invalid upload file, please ensure you only upload images with: .png, .jpeg or .jpg, extensions.")

        return redirect(url_for('stream', username=username))

    posts = query_db(
        "SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?1) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?1) OR p.u_id=?1 ORDER BY p.creation_time DESC",
        [user['id']])

    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)


# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    form = CommentsForm()
    if form.is_submitted():
        user = query_db("SELECT * FROM Users WHERE username= ?", [username], one=True)
        query_db("INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?)",
                 [p_id, user['id'], form.comment.data, datetime.now()])

    post = query_db("SELECT * FROM Posts WHERE id=?", [p_id], one=True)
    all_comments = query_db(
        "SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id=? ORDER BY c.creation_time DESC",
        [p_id])
    return render_template('comments.html', title='Comments', username=username, form=form, post=post,
                           comments=all_comments)


# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    form = FriendsForm()
    user = query_db("SELECT * FROM Users WHERE username=?", [username], one=True)
    if form.is_submitted():
        friend = query_db("SELECT * FROM Users WHERE username=?", [form.username.data], one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db("INSERT INTO Friends (u_id, f_id) VALUES(?, ?)", [user['id'], friend['id']])

    all_friends = query_db("SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=?",
                           [user['id'], user['id']])
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        query_db(
            "UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=?",
            [form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data,
             form.birthday.data, username])
        return redirect(url_for('profile', username=username))

    user = query_db("SELECT * FROM Users WHERE username=?", [username], one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)


# flask login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"
# login_manager.anonymous_user = MyAnonymousUser # if we want to restrict users who are not logged in


# callback to reload the user objext
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/settings")
@login_required
def settings():
    pass


# Method to log in user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Logging in, and confirms that the user is part of the class User
    if form.validate_on_submit():
        userpass = form.password.data
        username = form.username.data
        user = User(username)
        login_user(user)
        flash('Logged in successfully!')
        # the line below, ads a simple but effective 'rememer_me', aka cookie, which acording to flask_login, is tamperproof
        login_user(user, remember=True, force=False, fresh=True)
        # The if below, checks if the url is safe, so that login is not vonerable
        # next = flask.request.args.get('next') # imported from forms.py instead
        if not is_safe_url(next):
            return abort(400)
        return redirect('/')
    return render_template('login.html', title='Sign in', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
