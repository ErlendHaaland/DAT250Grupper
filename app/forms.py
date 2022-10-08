# from re import RegexFlag
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, \
    HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import Regexp, EqualTo
from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect
from flask_login import UserMixin

# FLASK_RUN_CERT= adhoc
# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# used the flask function @login_required, which require a user to be logged in reasently to do the task.
#   If not, they are 'unauthorized, and must login again.
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField(
        'Remember me')  # TODO: It would be nice to have this feature implemented, probably by using cookies
    # See forms.py line 84
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,256})',
               message="1. At least one lower-cased letter and one upper-cased letter. 2. At least 1 number. "
                       "3. Minimum length of 8 and maximum of 256. 4. At least one special character '#@!$'")],
                             render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[EqualTo('password', message='Passwords must match')],
                                     render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')


class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)


class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')


class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')


class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')


class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')


# method to verify that the url is safe
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))
# code considered publci domain, origined from the url:https://web.archive.org/web/20120501162055/http://flask.pocoo.org/snippets/63/


# the User model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
