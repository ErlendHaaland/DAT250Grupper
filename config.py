import os


# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'F5Dfj1LN7fMelExqPqfmAe0MFodsy9QfhfzVrjIoaS0'  # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'jpeg', 'png', 'jpg'}
