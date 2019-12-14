from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField

#from flask_login import current_user

class LoginForm(FlaskForm):
    # userAccount = StringField('User Account', validators=[DataRequired()], render_kw={"placeholder" : "User Account"})
    userAccount = StringField('User Account', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remenber Me')
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm):
    user_account = StringField('User Account', 
            validators=[DataRequired(), Length(min=2, max=20)])  
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')
    # Must start with 'validate' ?
    # def validate_username(serf, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError('That username is taken. Please choose another name')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user:
    #         raise ValidationError('That username is taken. Please choose another name')
    
class AccountInputForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    # dummy_catgory = [('food','Food'), ('household good', 'Household good'), ('rent', 'Rent')]
    # category = SelectField('Category', choices=dummy_catgory)
    category = SelectField('Category')
    comment = StringField('Comment', validators=[DataRequired()])
    tax_rate = FloatField('Tax rate',default=0.08, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CategoryInputForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()], render_kw={"placeholder" : "New Category"})
    picture = FileField('Picture: ', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Category')
    
