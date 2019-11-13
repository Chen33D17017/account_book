from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#import secrets
#secrets.token_hex(16)
app.config['SECRET_KEY'] = '5f7c56f34d74f2d33a0748048209df29'

from account_book import routes
