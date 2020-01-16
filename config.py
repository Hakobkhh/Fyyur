import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
user_name = os.environ.get('USER')
password = os.environ.get('password')

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{user_name}:{password}' \
                                            '@localhost:5432/fyyrdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
