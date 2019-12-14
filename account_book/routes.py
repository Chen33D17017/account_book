from flask import render_template, request, url_for, redirect
from account_book import app
from account_book.forms import LoginForm, AccountInputForm, CategoryInputForm, RegistrationForm

dummy_catgory = [( 1,'Food'), ( 2, 'Household good'), ( 3, 'Rent')]

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
        'user' : 'Chen',
        'date' : '2020-11-20',
        'category' : 'Food',
        'category_pics' : 'food.png',
        'amount' : '500',
        'comment' : 'Mcdonald'
        },
        {
        'user' : 'Chen',
        'date' : '2020-11-19',
        'category_pics' : 'food.png',
        'category' : 'Food',
        'amount' : '600',
        'comment' : 'KFC'
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


# @app.route("/home")
# def home():
#     return render_template('home.html')

# @app.route("/add_bill", methods=['GET', 'POST'])
# def add_bill():
#     form = AccountInputForm()
#     c_form = CategoryInputForm()
#     form.category.choices = dummy_catgory
#     if form.validate_on_submit():
#         return redirect(url_for('home'))
#     if c_form.validate_on_submit():
#         dummy_catgory.append((len(dummy_catgory)+1, form.category.data))
#         return redirect(url_for('add_bill'))
#     return render_template('add_bill.html', form=form, c_form=c_form, \
#             bills=dummy_bill, title="Add Bill")

