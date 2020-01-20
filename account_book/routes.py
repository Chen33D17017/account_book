from flask import render_template, request, url_for, redirect, current_app, flash, session
from account_book import app, bcrypt, db
from account_book.forms import LoginForm, BillInputForm, NewCategoryForm, RegistrationForm, EditBillForm, UserProfileForm, ChangePasswordForm, ChangeCategoryOption
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from PIL import Image
import secrets
from flask_login import login_user, current_user, logout_user, login_required
from account_book.model import User, Category, Bill, User_date
import os
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

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
def home():
    # flash(f"Welcome Back, {current_user.name}", 'success')
    total_cost = {}
    count_query = db.session.query(func.sum(Bill.amount)).join(Category).filter(Category.owner_id == 1)
    today = datetime.combine(date.today(), datetime.min.time())
    day_cost_result = count_query.filter(Category.count_in_day == True, Bill.date == today).first()[0]
    total_cost['day'] = day_cost_result if day_cost_result else 0

    week_first_day = today - timedelta(days=today.weekday())
    week_last_day = today + timedelta(days=(7 - today.weekday()))
    week_cost_result = count_query.filter(Category.count_in_week == True, Bill.date >= week_first_day, Bill.date < week_last_day).first()[0]
    total_cost['week'] = week_cost_result if week_cost_result else 0
    
    this_month = datetime(today.year, today.month, 1)
    next_month = this_month + relativedelta(months=1)
    month_cost_result = count_query.filter(Category.count_in_month == True, Bill.date >= this_month, Bill.date < next_month).first()[0]
    total_cost['month'] = month_cost_result if month_cost_result else 0

    group_show = [False, False]
    group_result = {}
    cost_group_query = db.session.query(Category.category_name, func.sum(Bill.amount)).join(Category).filter(Category.owner_id == 1).group_by(Bill.category_id)
    group_this_month = cost_group_query.filter(Bill.date >= this_month, Bill.date < next_month).all()
    if group_this_month:
        group_show[1] = True
        group_result['this_month'] = [[item[0] for item in group_this_month], [item[1] for item in group_this_month]]
    else:
        group_result['this_month'] = []
    
    last_month = this_month - relativedelta(months=1)
    group_last_month = cost_group_query.filter(Bill.date >= last_month, Bill.date < this_month).all()
    if group_last_month:
        group_show[0]= True
        group_result['last_month'] = [[item[0] for item in group_last_month], [item[1] for item in group_last_month]]
    else:
        group_result['last_month'] = []

    month_static = [[], []]
    for i in range(1, 13, 1):
        start = datetime(date.today().year, i, 1)
        end = start + relativedelta(months=1)
        month_cost = count_query.filter(Bill.date >= start, Bill.date < end).first()
        month_static[0].append(start.strftime("%b"))
        month_static[1].append(month_cost[0] if month_cost[0] else 0)

    day_static = [[], []]
    today = date.today()
    end_day = (datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)).day
    for i in range(1, end_day+1, 1):
        day = datetime(today.year, today.month, i)
        day_cost = count_query.filter(Bill.date == day).first()
        day_static[0].append(i)
        day_static[1].append(day_cost[0] if day_cost[0] else 0 )    
    
    return render_template('home.html', title="Home", total_cost=total_cost, group_result=group_result, month_static=month_static, day_static=day_static, today=today, group_show=group_show)

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
    bill_add_today = Bill.query.filter(Bill.add_date >= today, Bill.add_date < tomorrow).order_by(Bill.date.desc()).all()
    bill_bracket = []
    for i in bill_add_today:
        tmp = {
            "id" : i.bill_id,
            "amount" : i.amount,
            "category" : i.category_type.category_name,
            "comment" : i.comment,
            "date" : i.date.date()
        }
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
                db_add(Category(category_name=new_category, owner_id=current_user.user_id))
                flash("Success to Add New Category", "success")
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
        return redirect(url_for('add_bill'))
    return render_template('add_bill.html', form=form, c_form=c_form, \
                           bills=bill_bracket, e_form=e_form, title="Add Bill")


def edit_or_delete_bill(request_form):
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
            search_records = User_date.query.filter_by(user_id=current_user.user_id, year=new_date.year, month=new_date.month).first()
            if search_records:
                search_records.count += 1;
            else:
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
    records = bills.order_by(Bill.date.desc()).all()
    if records:
        response['bills'] = [bill.to_dict() for bill in records]
    return json.dumps(response)


@app.route("/search_bill", methods=['POST', 'GET'])
@login_required
def search_bill():
    e_form = EditBillForm()
    e_form.category.choices = [(c.category_name, c.category_name) for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    distinct_years = db.session.query(User_date.year).filter(User_date.user_id==current_user.user_id).distinct().all()
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
    e_form = EditBillForm()
    bill_TODO = []
    category_records = Category.query.filter_by(category_id=category_id).first()
    category_name = category_records.category_name
    bills = Bill.query.filter(Bill.category_id==category_id).order_by(Bill.date.desc()).all()
    e_form.category.choices = [(c.category_name, c.category_name) for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    bill_bracket = []
    for i in bills:
        tmp = {
            "id" : i.bill_id,
            "amount" : i.amount,
            "category" : i.category_type.category_name,
            "comment" : i.comment,
            "date" : i.date.date()
        }
        bill_bracket.append(tmp)
    count_records = Category.query.filter_by(category_id=category_id).first()
    count_in_list = [count_records.count_in_day, count_records.count_in_week, count_records.count_in_month]
    sum_query = db.session.query(func.sum(Bill.amount)).filter(Bill.category_id==category_id)
    today = datetime.combine(date.today(), datetime.min.time())

    # Calculate sum for each days
    day_sum = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        sum_value = sum_query.filter(Bill.date == target_date).first()
        str_day = target_date.strftime("%m-%d")
        day_sum.append((f"{str_day}", sum_value[0] if sum_value[0] else 0))
        
    # Calculate sum for each months
    year, month = today.year, today.month
    start_day = datetime(year, month, 1)
    month_sum = []    
    for i in range(5):
        end_day = start_day + relativedelta(months=1)
        query_result = sum_query.filter(Bill.date >= start_day, Bill.date < end_day).first()[0]
        sum_value = query_result if query_result else 0
        str_month = start_day.strftime("%b")
        month_sum.append((f"{str_month}", sum_value))
        start_day = start_day - relativedelta(months=1)
    month_sum = month_sum[::-1]

    if request.method == 'POST':
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
        else:
            if 'submit' in request.form:
                print("submit")
                print(form.count_in_day.data)
                count_records.count_in_day = form.count_in_day.data
                count_records.count_in_week = form.count_in_week.data
                count_records.count_in_month = form.count_in_month.data
                db.session.commit()
            elif 'delete' in request.form:
                # TODO : Delete this category                
                for bill in Bill.query.filter_by(category_id=category_id).all():
                    safe_delete_bill(bill)
                db.session.delete(Category.query.filter_by(category_id=category_id).first())
                db.session.commit()
                return redirect(url_for('home'))
            else:
                pass
        return redirect(url_for('category_page', category_id=category_id)) 
    return render_template('category_page.html', title=f"{category_name}", category=category_name, bills=bill_bracket, form=form, e_form=e_form, count_in_list=count_in_list, day_sum=day_sum, month_sum=month_sum)

def check_delete_user_date_record(year, month):
    check_record = User_date.query.filter_by(user_id=current_user.user_id, year=year, month=month).first()
    if not check_record:
        flash("Somthing wrong in the User date model", "danger")
        return
    elif check_record.count == 1:
        db.session.delete(check_record)
    else:
        check_record.count -= 1
    return

def safe_delete_bill(bill):
    old_year = bill.date.date().year
    old_month = bill.date.date().month
    check_delete_user_date_record(old_year, old_month)
    db.session.delete(bill)
