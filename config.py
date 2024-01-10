"""
This module will store all necessary configuration or import statements
for the Flask application.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Config variables for Flask application"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "temp-secret-key"
    
    # Use a more specific environment variable for your database URI
    DATABASE_URI = os.environ.get("MY_APP_DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "sqlite.db")
    
    # Ensure that the URI is compatible with different operating systems
    SQLALCHEMY_DATABASE_URI = DATABASE_URI.replace("sqlite:///", "sqlite:///" + os.path.join(basedir, ""))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
