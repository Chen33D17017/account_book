from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from account_book.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# import secrets
# secrets.token_hex(16)

# export SECRET_KEY=''
# export SQLALCHEMY_DATABASE_URL=''

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = "info"

from account_book.users.routes import users
from account_book.bills.routes import bills
from account_book.main.routes import main

app.register_blueprint(users)
app.register_blueprint(bills)
app.register_blueprint(main)

if __name__ == "__main__":
    app.run()
