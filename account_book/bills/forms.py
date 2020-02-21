from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields.html5 import DateField
from account_book.model import Category

class BillInputForm(FlaskForm):
    cost = IntegerField('Cost', validators=[DataRequired()], render_kw={"placeholder": "&#165;"})
    category = SelectField('Category')
    comment = StringField('Comment', validators=[DataRequired()], render_kw={"placeholder": "Dinner: KFC"})
    tax_rate = FloatField('Tax rate',default=0.08, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class NewCategoryForm(FlaskForm):
    category = StringField('New :', validators=[DataRequired()], render_kw={"placeholder" : "Category"})
    submit = SubmitField('Add')

    def validate_add_category(self, category):
        category = Category.query.filter_by(category_name=category).first()
        if category:
            raise ValidationError('Category already existed')

class EditBillForm(FlaskForm):
    cost = IntegerField("COST",validators=[DataRequired()], render_kw={"placeholder": "$"})
    category = SelectField('Category')
    comment = StringField('Comment', validators=[DataRequired()], render_kw={"placeholder": "Dinner: KFC"})
    tax_rate = FloatField('Tax rate',default=0.08, render_kw={"placeholder": "Tax Rate"})
    tax_bool = BooleanField('Tax')
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    update = SubmitField('Update')
    delete = SubmitField('Delete')

class ChangeCategoryOption(FlaskForm):
    count_in_day = BooleanField('Count in Day Budget')
    count_in_week = BooleanField('Count in Week Budget')
    count_in_month = BooleanField('Count in Month Budget')
    submit = SubmitField('Update')
    delete = SubmitField('Delete')
