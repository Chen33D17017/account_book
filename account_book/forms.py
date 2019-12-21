from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField, TextField, IntegerField
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
    
class BillInputForm(FlaskForm):
    cost = IntegerField('Cost', validators=[DataRequired()], render_kw={"placeholder": "$"})
    category = SelectField('Category')
    comment = StringField('Comment', validators=[DataRequired()], render_kw={"placeholder": "Dinner: KFC"})
    tax_rate = FloatField('Tax rate',default=0.08, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewCategoryForm(FlaskForm):
    category = StringField('New :', validators=[DataRequired()], render_kw={"placeholder" : "Category"})
    submit = SubmitField('Add')

    
class EditBillForm(FlaskForm):
    def __init__(self, index, cost, category, comment, date, **kw):
        super(EditBillForm, self).__init__(**kw)
        self.index_value = index
        self.cost_value = cost
        self.category_value = category
        self.comment_value = comment
        self.date_value = date

    cost = IntegerField("COST",validators=[DataRequired()], render_kw={"placeholder": "$"})
    category = SelectField('Category')
    comment = TextField('Comment', validators=[DataRequired()], render_kw={"placeholder": "Dinner: KFC"})
    tax_rate = FloatField('Tax rate',default=0.08, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    date = DateField('Date', validators=[DataRequired()])
    update = SubmitField('Update')
    delete = SubmitField('Delete')


class SearchBillForm(FlaskForm):
    category = SelectField('Category')
    date = DateField('Date')
    year = SelectField('Year')
    month = SelectField('Month')
    submit = SubmitField('Search')
    
        
class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    month_budget = IntegerField('Month Budget', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    slack_token = StringField('Slack Token')
    submit = SubmitField('Update')
    # def validate_username(serf, username):
    #     if username.data != current_user.username:
    #         user = User.query.filter_by(username=username.data).first()
    #         if user:
    #             raise ValidationError('That username is taken. Please choose another name')

    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email.data).first()
    #         if user:
    #             raise ValidationError('That username is taken. Please choose another name')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

class ChangeCategoryOption(FlaskForm):
    count_in_day_budget = BooleanField('Count in Day Budget')
    count_in_week_budget = BooleanField('Count in Week Budget')
    count_in_month_budget = BooleanField('Count in Month Budget')
    submit = SubmitField('Update')
    delete = SubmitField('Delete')
    
