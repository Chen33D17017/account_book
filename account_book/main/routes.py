from flask import Blueprint
from flask import render_template
from account_book import db, app
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_login import current_user, login_required
from account_book.model import Category, Bill
from sqlalchemy import func


main = Blueprint('main', __name__)


@app.context_processor
def categories_list():
    return {} if not current_user.is_authenticated else dict(
        categories = [ (category.category_id, category.category_name)
                       for category in Category.query.filter_by(owner_id=current_user.user_id).all()]
    )


@main.route("/home")
@login_required
def home():
    total_cost = {}
    sum_query = db.session.query(func.sum(Bill.amount)).join(Category).filter(Category.owner_id == current_user.user_id)
    today = datetime.combine(date.today(), datetime.min.time())
    day_cost_result = sum_query.filter(Category.count_in_day == True, Bill.date == today).first()[0]
    total_cost['day'] = day_cost_result if day_cost_result else 0

    week_first_day = today - timedelta(days=today.weekday())
    week_last_day = today + timedelta(days=(7 - today.weekday()))
    week_cost_result = sum_query\
        .filter(Category.count_in_week == True, Bill.date >= week_first_day, Bill.date < week_last_day).first()[0]
    total_cost['week'] = week_cost_result if week_cost_result else 0
    
    this_month = datetime(today.year, today.month, 1)
    next_month = this_month + relativedelta(months=1)
    month_cost_result = sum_query\
        .filter(Category.count_in_month == True, Bill.date >= this_month, Bill.date < next_month).first()[0]
    total_cost['month'] = month_cost_result if month_cost_result else 0

    sum_result = [0, 0]
    group_show = [False, False]
    group_result = {}

    cost_group_query = db.session.query(Category.category_name, func.sum(Bill.amount)).join(Category)\
        .filter(Category.owner_id == current_user.user_id).group_by(Bill.category_id)
    sum_result[1] = sum_query.filter(Bill.date >= this_month, Bill.date < next_month).first()[0]
    group_this_month = cost_group_query.filter(Bill.date >= this_month, Bill.date < next_month).all()
    if group_this_month:
        group_show[1] = True
        group_result['this_month'] = [[item[0] for item in group_this_month], [item[1] for item in group_this_month]]
    else:
        group_result['this_month'] = []
    
    last_month = this_month - relativedelta(months=1)
    sum_result[0] = sum_query.filter(Bill.date >= last_month, Bill.date < this_month).first()[0]
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
        month_cost = sum_query.filter(Bill.date >= start, Bill.date < end).first()
        month_static[0].append(start.strftime("%b"))
        month_static[1].append(month_cost[0] if month_cost[0] else 0)

    day_static = [[], []]
    today = date.today()
    end_day = (datetime(today.year, today.month, 1) + relativedelta(months=1) - timedelta(days=1)).day
    for i in range(1, end_day+1, 1):
        day = datetime(today.year, today.month, i)
        day_cost = sum_query.filter(Bill.date == day).first()
        day_static[0].append(i)
        day_static[1].append(day_cost[0] if day_cost[0] else 0 )    
    
    return render_template('home.html', title="Home", total_cost=total_cost, group_result=group_result,
                           month_static=month_static, day_static=day_static, today=today, group_show=group_show,
                           sum_result=sum_result)
