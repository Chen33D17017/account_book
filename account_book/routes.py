from flask import render_template, request, url_for, redirect
from account_book import app
from account_book.forms import LoginForm, BillInputForm, NewCategoryForm, RegistrationForm, EditBillForm, SearchBillForm

dummy_category = [( 1,'Food'), ( 2, 'Household good'), ( 3, 'Rent')]
dummy_year = [(0, '-'), (1, '2019'), (2, '2018')]
dummy_month = [(0, '-'), (1, '11'), (2, '12')]


accounts = [
    {
        'user': 'admin',
        'password': 'admin'
    },
    {
        'user': 'chen',
        'password': 'chen'
    }
]

dummy_bill = [
    {
        'id': '1',
        'user' : 'Chen',
        'date' : '2020-11-20',
        'category' : 'Food',
        'cost' : '500',
        'comment' : 'Mcdonald'
    },
    {
        'id':'2',
        'user' : 'Chen',
        'date' : '2020-11-19',
        'category' : 'Rent',
        'cost' : '600',
        'comment' : 'KFC'
    },
    {
        'id':'3',
        'user' : 'Chen',
        'date' : '2020-11-12',
        'category' : 'Food',
        'cost' : '600',
        'comment' : 'MOS Burger'
    }
]

@app.route("/", methods=['GET', 'POST'])
@app.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title="Login")


@app.route("/register")
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return rediect(url_for('login'))
    return render_template('register.html', form=form, title="Registration")


@app.route("/test")
def home():
    return render_template('hello.html', title="hello")

# @app.route("/home")
# def home():
#     return render_template('home.html')

@app.route("/add_bill", methods=['GET', 'POST'])
def add_bill():
    form = BillInputForm()
    c_form = NewCategoryForm()
    form.category.choices = dummy_category
    bill_bracket = []
    for i in dummy_bill:
        tmp = EditBillForm(i['id'], i['cost'], i['category'], i['comment'], i['date'])
        tmp.category.choices = dummy_category
        bill_bracket.append(tmp)
        
    if form.validate_on_submit():
        return redirect(url_for('home'))
    if c_form.validate_on_submit():
        dummy_catgory.append((len(dummy_catgory)+1, form.category.data))
        return redirect(url_for('add_bill'))
    return render_template('add_bill.html', form=form, c_form=c_form, \
                           bills=bill_bracket, title="Add Bill")

@app.route("/search_bill")
def search_bill():
    form = SearchBillForm()
    form.category.choices = dummy_category
    form.year.choices = dummy_year
    form.month.choices = dummy_month
    bill_bracket = []
    for i in dummy_bill:
        tmp = EditBillForm(i['id'], i['cost'], i['category'], i['comment'], i['date'])
        tmp.category.choices = dummy_category
        bill_bracket.append(tmp)
    return render_template('search_bill.html', form=form, bills=bill_bracket, title='Search Bill')

