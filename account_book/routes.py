from flask import render_template, request, url_for, redirect, current_app, flash, session
from account_book import app, bcrypt, db
from account_book.forms import LoginForm, BillInputForm, NewCategoryForm, RegistrationForm, EditBillForm, SearchBillForm, UserProfileForm, ChangePasswordForm, ChangeCategoryOption
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from PIL import Image
import secrets
from flask_login import login_user, current_user, logout_user, login_required
from account_book.model import User, Category, Bill, User_date
import os
import json
from sqlalchemy.exc import IntegrityError

dummy_category = [( 1,'Food'), ( 2, 'Household good'), ( 3, 'Rent')]
dummy_year = [(0, '-'), (1, '2019'), (2, '2018')]
dummy_month = [(0, '-'), (1, '11'), (2, '12')]

accounts = {'user': 'admin', 'password': 'admin'}

dummy_user = {
    'username' : 'Chen',
    'month_budget' : 120000,
    'email' : 'xxxxxx@gmail.com'
}

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


@app.context_processor
def categories_list():
    return {} if not current_user.is_authenticated else dict(
        # categories = dummy_category
        categories = [ (category.category_id, category.category_name) for category in Category.query.filter_by(owner_id=current_user.user_id).all()] 
    )


@app.route("/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home', user=current_user.name))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(url_for(next_page)[1:]) if next_page else redirect(url_for('home', user=user.name))
            else:
                flash("Login Unsecessful, please check your username and password", "danger")
        else:
            flash("Unexist user, please try again or register new user", "danger")
    return render_template('login.html', form=form, title="Login")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home', user=current_user.name))
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email = form.email.data
        new_user = User(username=username, name=name, password=hashed_password, email=email)
        try:
            db_add(new_user)
            return redirect(url_for('login'))
        except Exception as e:
            flash("Something Wrong", 'danger')
    return render_template('register.html', form=form, title="Registration")

def db_add(db_obj):
    db.session.add(db_obj)
    db.session.commit()

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/home")
@login_required
def home(user=None):
    user = request.args.get('user')
    if user:
        print(user)
        flash(f"Welcome Back, {user}", 'success')
    return render_template('home.html', title="Home")

def date_convert(date_data):
    min_time = datetime.min.time()
    date_time = datetime.combine(date_data, min_time)
    return date_time

@app.route("/add_bill", methods=['GET', 'POST'])
@login_required
def add_bill():
    form = BillInputForm()
    c_form = NewCategoryForm()
    e_form = EditBillForm()
    category_choices = [(c.category_name, c.category_name) for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    form.category.choices = category_choices
    e_form.category.choices = category_choices
    today = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    bill_add_today = Bill.query.filter(Bill.add_date >= today, Bill.add_date < tomorrow).all()
    bill_bracket = []
    for i in bill_add_today:
        tmp = {
            "id" : i.bill_id,
            "amount" : i.amount,
            "category" : i.category_type.category_name,
            "comment" : i.comment,
            "date" : i.date.date()
        }
        # tmp = EditBillForm(i.bill_id, i.amount, i.category_type.category_name, i.category_id, i.comment, i.date.date())
        bill_bracket.append(tmp)
    if request.method == 'POST':
        form_keys = list(request.form.keys())
        print(request.form)
        if 'form-name' in request.form:
            form_name = request.form['form-name']
            # Add bill
            if form_name == 'add-bill':
                cost = int((1 + float(form.tax_rate.data)) * form.cost.data) if form.tax_bool.data else int(form.cost.data)
                category = form.category.data
                category = Category.query.filter_by(category_name=category).first().category_id
                bill_date = form.date.data
                comment = form.comment.data
                user_date = User_date.query.filter_by(user_id=current_user.user_id, year=bill_date.year, month=bill_date.month).first()
                if user_date:
                    user_date.count += 1
                else:
                    db.session.add(User_date(user_id=current_user.user_id, year=bill_date.year, month=bill_date.month))
                db.session.add(Bill(amount=cost, category_id=category, date=bill_date, comment=comment))
                db.session.commit()
                flash("Success to Add Bill", "success")
            if form_name == 'add-category':
                new_category = c_form.category.data
                db_add(Category(category_name=new_qcategory, owner_id=current_user.user_id))
                flash("Success to Add New Category", "success")
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
        return redirect(url_for('add_bill'))
    return render_template('add_bill.html', form=form, c_form=c_form, \
                           bills=bill_bracket, e_form=e_form, title="Add Bill")


def edit_or_delete_bill(request_form):
    
    def check_delete_user_date_record(year, month):
        check_record = User_date.query.filter_by(user_id=current_user.user_id, year=year, month=month).first()
        if not check_record:
            print("Somthing wrong in the User date model")
            return
        elif check_record.count == 1:
            db.session.delete(check_record)
        else:
            check_record.count -= 1
        return
    
    index = int(request_form['edit-id'])
    target_bill = Bill.query.filter_by(bill_id=index).first()
    old_year = target_bill.date.date().year
    old_month = target_bill.date.date().month
    if 'update' in request_form:
        target_bill.amount = int((1 + float(request_form['tax_rate'])) * int(request_form['cost'])) if 'tax_bool' in request_form else int(request_form['cost'])
        target_bill.category_id = Category.query.filter_by(category_name=request_form['category']).first().category_id
        new_date = date.fromisoformat(request_form['date'])
        if new_date.year != old_year or new_date.month != old_month:
            check_delete_user_date_record(old_year, old_month)
            db.session.add(User_date(user_id=current_user.user_id, year=new_date.year, month=new_date.month))
        target_bill.date = new_date
        target_bill.comment = request_form['comment']
    if 'delete' in request_form:
        check_delete_user_date_record(old_year, old_month)
        db.session.delete(target_bill)
    db.session.commit()


@app.route('/_search_bill', methods=["POST"])
def _search_bill():
    recieve_data = json.loads(request.data)
    response = {}
    bills = Bill.query.join(Category).filter_by(owner_id=1)
    if 'category' in recieve_data:
        category = recieve_data['category']
        bills = bills.filter_by(category_name=category) if category else bills
        if recieve_data['date']:
            search_date = date.fromisoformat(recieve_data['date'])
            search_date = datetime.combine(search_date, datetime.min.time())
            bills = bills.filter(Bill.date==search_date)
        else:
            if recieve_data['year']:
                year = int(recieve_data['year'])
                target_user_date = User_date.query.filter_by(user_id=current_user.user_id, year=year)
                response['month_choices'] = [item.month for item in target_user_date.all()]
                start_day, last_day = datetime(year, 1, 1), datetime(year+1, 1, 1)
                if recieve_data['month']:
                    month = int(recieve_data['month'])
                    start_day = datetime(year, month, 1)
                    last_day = start_day + relativedelta(months=1)
                bills = bills.filter(Bill.date >= start_day, Bill.date < last_day)
    else:
        search_date = datetime.combine(date.today(), datetime.min.time())
        bills = bills.filter(Bill.date==search_date)
    records = bills.all()
    if records:
        response['bills'] = [bill.to_dict() for bill in records]
    return json.dumps(response)


@app.route("/search_bill", methods=['POST', 'GET'])
@login_required
def search_bill():
    e_form = EditBillForm()
    e_form.category.choices = [(c.category_name, c.category_name) for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    distinct_years = db.session.query(User_date.year).distinct().all()
    year_choices = [year[0] for year in distinct_years]
    if request.method == 'POST':
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
    return render_template('search_bill.html', e_form=e_form, title='Search Bill', years=year_choices)


@app.route("/user_profile", methods=['POST', 'GET'])
@login_required
def user_profile():
    user_form = UserProfileForm()
    password_form = ChangePasswordForm()
    if user_form.validate_on_submit():
        print(user_form.picture)
        print(user_form.picture.data)
        if user_form.picture.data:
           picture_file = save_picture(user_form.picture.data)
           # delete_old_pic(current_user.image_file)
           image_file = picture_file
        username = user_form.username.data
        email = user_form.email.data
        month_budget = user_form.month_budget.data
        slack_token = user_form.slack_token.data
        print(f"username: {username}")
        print(f"email: {email}")
        print(f"month_budget: {month_budget}")
        print(f"slack_token: {slack_token}")
        # TODO: Save data into database
        # flash(" Your account has been updated! ", "success")
        return redirect(url_for('user_profile'))
    if password_form.validate_on_submit():
        password = password_form.password.data
        confirm_password = password_form.confirm_password.data
        print(f"password : {password}")
        print(f"confirm_password : {confirm_password}")
        return redirect(url_for('user_profile'))
    # TODO: Direct to the home page
    return render_template('user_profile.html', user_form=user_form, \
                           password_form=password_form, title="User Profile", user=dummy_user)

def absolute_path(path):
    return os.path.join(current_app.root_path, 'static/profile_pics', path)


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    create_dir(os.path.join(current_app.root_path, 'static/profile_pics'))
    picture_path = absolute_path(picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def delete_old_pic(old_pic):
    if old_pic != 'default.jpg':
        os.remove(absolute_path(old_pic))
        

@app.route("/categroy/<int:category_id>", methods=['POST', 'GET'])
@login_required
def category_page(category_id):
    form = ChangeCategoryOption()
    bill_bracket = []
    # TODO: Bill this month or last seven days
    for i in dummy_bill:
        tmp = EditBillForm(i['id'], i['cost'], i['category'], i['comment'], i['date'])
        tmp.category.choices = dummy_category
        bill_bracket.append(tmp)
    if request.method == 'POST':
        form_keys = list(request.form.keys())
        if 'edit-index' in form_keys:
            edit_or_delete_bill(request.form)
        else:
            if 'submit' in form_keys:
                day_budget = form.count_in_day_budget.data
                week_budget = form.count_in_week_budget.data
                month_budget = form.count_in_month_budget.data
                print(f"budget in day, week, month: {day_budget}, {week_budget}, {month_budget}")
            elif 'delete' in form_keys:
                # TODO : Delete this category
                print("Delete this category")
            else:
                # Nothing happend with POST method?
                pass
        return redirect(url_for('category_page', category_id=category_id)) 
    return render_template('category_page.html', title="Category", category=dummy_category[category_id-1][1], bills=bill_bracket, form=form)

