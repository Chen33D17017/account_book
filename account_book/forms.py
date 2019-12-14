from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField

#from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder" : "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "Password"})
    remember = BooleanField('Remenber Me')
    submit = SubmitField('Submit')

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
    
