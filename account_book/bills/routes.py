import json
from flask import Blueprint
from account_book import db
from sqlalchemy import func
from account_book.utils import db_add
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_login import current_user, login_required
from account_book.model import Category, Bill, User_date
from flask import render_template, request, url_for, redirect, flash
from account_book.bills.utils import safe_delete_bill, edit_or_delete_bill
from account_book.bills.forms import BillInputForm, NewCategoryForm, EditBillForm, ChangeCategoryOption

bills = Blueprint('bills', __name__)

@bills.route("/add_bill", methods=['GET', 'POST'])
@login_required
def add_bill():
    form = BillInputForm()
    c_form = NewCategoryForm()
    e_form = EditBillForm()
    category_choices = [(c.category_name, c.category_name)
                        for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    form.category.choices = category_choices
    e_form.category.choices = category_choices
    today = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    bill_add_today = db.session.query(Bill).join(Category).filter(Bill.add_date >= today, Bill.add_date < tomorrow, Category.owner_id==current_user.user_id).\
                     order_by(Bill.date.desc()).all()
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
        if 'form-name' in request.form:
            form_name = request.form['form-name']
            # Add bill
            if form_name == 'add-bill':
                cost = int((1 + float(form.tax_rate.data)) * form.cost.data) \
                    if form.tax_bool.data else int(form.cost.data)
                category = form.category.data
                category = Category.query.filter_by(category_name=category, owner_id=current_user.user_id).first().category_id
                bill_date = form.date.data
                comment = form.comment.data
                user_date = User_date.query.\
                    filter_by(user_id=current_user.user_id, year=bill_date.year, month=bill_date.month).first()
                if user_date:
                    user_date.count += 1
                else:
                    db.session.add(User_date(user_id=current_user.user_id, year=bill_date.year, month=bill_date.month))
                db.session.add(Bill(amount=cost, category_id=category, date=bill_date, comment=comment))
                db.session.commit()
                flash("Success to Add Bill", "success")
            if form_name == 'add-category':
                new_category = c_form.category.data
                print(new_category)
                db_add(Category(category_name=new_category, owner_id=current_user.user_id))
                flash("Success to Add New Category", "success")
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
        return redirect(url_for('bills.add_bill'))
    return render_template('add_bill.html', form=form, c_form=c_form,
                           bills=bill_bracket, e_form=e_form, title="Add Bill", today=f"{date.today()}")


@bills.route('/_search_bill', methods=["POST"])
def _search_bill():
    recieve_data = json.loads(request.data)
    response = {}
    bills = Bill.query.join(Category).filter_by(owner_id=current_user.user_id)
    if 'category' in recieve_data:
        category = recieve_data['category']
        bills = bills.filter_by(category_name=category) if category else bills
        if recieve_data['date']:
            search_date = datetime.strptime(recieve_data['date'], "%Y-%m-%d")
            # search_date = date.fromisoformat(recieve_data['d::ate'])
            # search_date = datetime.combine(search_date, datetime.min.time())
            bills = bills.filter(Bill.date==search_date)
        elif recieve_data['year']:
            year = int(recieve_data['year'])
            target_user_date = User_date.query.filter_by(user_id=current_user.user_id, year=year)
            response['month_choices'] = [item.month for item in target_user_date.all()]
            start_day, last_day = datetime(year, 1, 1), datetime(year+1, 1, 1)
            if recieve_data['month']:
                month = int(recieve_data['month'])
                start_day = datetime(year, month, 1)
                last_day = start_day + relativedelta(months=1)
                response['selected'] = month        
            bills = bills.filter(Bill.date >= start_day, Bill.date < last_day)
    else:
        search_date = datetime.combine(date.today(), datetime.min.time())
        bills = bills.filter(Bill.date==search_date)
    records = bills.order_by(Bill.date.desc()).all()
    if records:
        response['bills'] = [bill.to_dict() for bill in records]
    return json.dumps(response)


@bills.route("/search_bill", methods=['POST', 'GET'])
@login_required
def search_bill():
    e_form = EditBillForm()
    e_form.category.choices = [(c.category_name, c.category_name)
                               for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
    distinct_years = db.session.query(User_date.year).filter(User_date.user_id==current_user.user_id).distinct().all()
    year_choices = [year[0] for year in distinct_years]
    if request.method == 'POST':
        if 'edit-id' in request.form:
            edit_or_delete_bill(request.form)
    return render_template('search_bill.html', e_form=e_form, title='Search Bill', years=year_choices)


@bills.route("/category/<int:category_id>", methods=['POST', 'GET'])
@login_required
def category_page(category_id):
    form = ChangeCategoryOption()
    e_form = EditBillForm()
    bill_TODO = []
    category_records = Category.query.filter_by(category_id=category_id).first()
    category_name = category_records.category_name
    bills = Bill.query.filter(Bill.category_id==category_id).order_by(Bill.date.desc()).all()
    e_form.category.choices = [(c.category_name, c.category_name)
                               for c in Category.query.filter_by(owner_id=current_user.user_id).all()]
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
                count_records.count_in_day = form.count_in_day.data
                count_records.count_in_week = form.count_in_week.data
                count_records.count_in_month = form.count_in_month.data
                db.session.commit()
            elif 'delete' in request.form:
                for bill in Bill.query.filter_by(category_id=category_id).all():
                    safe_delete_bill(bill)
                db.session.delete(Category.query.filter_by(category_id=category_id).first())
                db.session.commit()
                return redirect(url_for('main.home'))
            else:
                pass
        return redirect(url_for('bills.category_page', category_id=category_id))
    return render_template('category_page.html', title=f"{category_name}", category=category_name,
                           bills=bill_bracket, form=form, e_form=e_form, count_in_list=count_in_list,
                           day_sum=day_sum, month_sum=month_sum)
