from account_book import db, login_manager
from flask_login import UserMixin
from datetime import datetime


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
    month_budget = db.Column(db.Integer, nullable=False, default=120000)
    week_budget = db.Column(db.Integer, nullable=False, default=30000)
    day_budget = db.Column(db.Integer, nullable=False, default=4000)
    slacktoken = db.Column(db.String(60))

    categories = db.relationship('Category', backref='owner', lazy=True)
    date_data = db.relationship('User_date', backref='user', lazy=True)

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
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.String(120))

    def to_dict(self):
        return {
            'id': self.bill_id,
            'amount' : self.amount,
            'category': self.category_type.category_name,
            'date': f"{self.date}".split()[0],
            'comment': self.comment
        }

    def __repr__(self):
        return f"Bill('{self.amount}','{self.category_type.owner.username}', '{self.category_type.category_name}', '{self.date}', '{self.comment}')"



class User_date(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "year", "month"),
    )

    date_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)


    
