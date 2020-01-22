from account_book import db

def db_add(db_obj):
    db.session.add(db_obj)
    db.session.commit()