from flask import render_template, request, url_for, redirect
from account_book import app
from account_book.forms import LoginForm, AccountInputForm

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

@app.route("/", methods=['GET', 'POST'])
@app.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title="login")

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/add_bill", methods=['GET', 'POST'])
def add_bill():
    form = AccountInputForm()
    if form.validate_on_submit():
        print("HELLO WORLD")
    return render_template('add_bill.html', form=form, title="Add Bill")
