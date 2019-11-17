from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
#from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder" : "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder" : "Password"})
    remember = BooleanField('Remenber Me')
    submit = SubmitField('Submit')

class AccountInputForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    # For SelectField: list of tuple
    # The first tuple member is the value that'll actually be submitted to your form and the second is the text that'll show to the end user.
    dummy_catgory = ['Food', 'Household good', 'Rent']
    #dummy_catgory = [('category' 'Food'), ('category', 'Household good'), ('category', 'Rent')]
    category = SelectField('Category', choices=dummy_catgory)
    comment = StringField('Comment', validators=[DataRequired()])
    tax_rate = FloatField('Tax rate',default=0.8, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    submit = SubmitField('Submit')
