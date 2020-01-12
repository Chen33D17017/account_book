from account_book import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    # TODO: Add the limitation on the form about username
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    budget = db.Column(db.Integer, nullable=False, default=120000)
    slacktoken = db.Column(db.String(60))

    categories = db.relationship('Category', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.name}')"

    def get_id(self):
        return (self.user_id)


class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    # TODO: Limitation for category name on form
    category_name = db.Column(db.String(15), nullable=False)
    count_in_day = db.Column(db.Boolean, nullable=False, default=True)
    count_in_week = db.Column(db.Boolean, nullable=False, default=True)
    count_in_month = db.Column(db.Boolean, nullable=False, default=True)
    
    bills = db.relationship('Bill', backref='category_type', lazy=True)

    def __repr__(self):
        return f"Category('{self.category_name}', '{self.owner.username}')"
    
class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.String(120))

    def __repr__(self):
        return f"Bill('{self.category.owner.username}', '{self.category.category_name}', '{self.date}', '{self.comment}')"
    
