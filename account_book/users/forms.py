from flask_wtf import FlaskForm
from account_book.model import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField

class LoginForm(FlaskForm):
    username = StringField('User Account', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('User not exist, Please register as new user')

class RegistrationForm(FlaskForm):
    username = StringField('User Account', 
            validators=[DataRequired(), Length(min=2, max=20)])  
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Your Name:', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another name')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another name')

class UserProfileForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    day_budget = IntegerField('Day Budget', validators=[DataRequired()])
    week_budget = IntegerField('Week Budget', validators=[DataRequired()])
    month_budget = IntegerField('Month Budget', validators=[DataRequired()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
            
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another name')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')
