from account_book import db
from datetime import date, datetime
from account_book.model import Bill, Category, User_date
from flask import flash
from flask_login import current_user


def edit_or_delete_bill(request_form):
    index = int(request_form['edit-id'])
    target_bill = Bill.query.filter_by(bill_id=index).first()
    old_year = target_bill.date.date().year
    old_month = target_bill.date.date().month
    if 'update' in request_form:
        target_bill.amount = int((1 + float(request_form['tax_rate'])) * int(request_form['cost'])) \
            if 'tax_bool' in request_form else int(request_form['cost'])
        target_bill.category_id = Category.query.filter_by(category_name=request_form['category'], owner_id=current_user.user_id).first().category_id
        new_date = datetime.strptime(request_form['date'], "%Y-%m-%d")
        if new_date.year != old_year or new_date.month != old_month:
            check_delete_user_date_record(old_year, old_month)
            search_records = User_date.query.\
                filter_by(user_id=current_user.user_id, year=new_date.year, month=new_date.month).first()
            if search_records:
                search_records.count += 1
            else:
                db.session.add(User_date(user_id=current_user.user_id, year=new_date.year, month=new_date.month))
        target_bill.date = new_date
        target_bill.comment = request_form['comment']
    if 'delete' in request_form:
        check_delete_user_date_record(old_year, old_month)
        db.session.delete(target_bill)
    db.session.commit()

    
def check_delete_user_date_record(year, month):
    check_record = User_date.query.filter_by(user_id=current_user.user_id, year=year, month=month).first()
    if not check_record:
        flash("Something wrong in the User date model", "danger")
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
