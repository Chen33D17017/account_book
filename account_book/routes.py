from flask import render_template, request, url_for, redirect
from account_book import app
from account_book.forms import LoginForm, BillInputForm, NewCategoryForm, RegistrationForm, EditBillForm, SearchBillForm, UserProfileForm, ChangePasswordForm, ChangeCategoryOption
from datetime import date

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
    return dict(
        categories = dummy_category
    )


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


@app.route("/home")
def home():
    return render_template('home.html', title="Home")


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
    if request.method == 'POST':
        form_keys = list(request.form.keys())
        if 'form-name' in form_keys:
            form_name = request.form['form-name']
            if form_name == 'add-bill':
                cost = float(form.cost.data)
                if form.tax_bool.data:
                    cost = int((1 + float(form.tax_rate.data)) * cost)
                category = form.category.data
                bill_date = form.date.data
                comment = form.comment.data
                # TODO: Add the bill into database
                dummy_bill.append({
                    'id': len(dummy_bill)+1,
                    'user' : 'Chen',
                    'date' : bill_date,
                    'category' : dummy_category[int(category)-1][1],
                    'cost' : cost,
                    'comment' : comment
                })
            if form_name == 'add-category':
                new_category = c_form.category.data
                # TODO: Add new category into database
                dummy_category.append((len(dummy_category)+1, new_category))
        if 'edit-index' in form_keys:
            edit_or_delete_bill(request.form)
        return redirect(url_for('add_bill'))
    return render_template('add_bill.html', form=form, c_form=c_form, \
                           bills=bill_bracket, title="Add Bill")


def edit_or_delete_bill(request_form):
    form_keys = list(request_form.keys())
    index = int(request_form['edit-index'])
    if 'update' in form_keys:
        cost = float(request_form['cost'])
        if 'tax_bool' in form_keys:
            cost = int((1 + float(request_form['tax_rate'])) * cost)
            category = request_form['category']
            bill_date = request_form['date']
            comment = request_form['comment']
            # TODO: Update the bill with bill index
        print(f"Update bill {index}")
    if 'delete' in form_keys:
        # TODO: Delete the bill with bill index
        print(f"Delete bill {index}")


@app.route("/search_bill", methods=['POST', 'GET'])
def search_bill(category=0, time_condition=(0, date.today())):
    form = SearchBillForm()
    # TODO: Get Year month and category data here
    # category: 0 for all
    # time condition 0 for specific date
    #                1 for specific year and month
    #                2 for specific year
    #                3 for specific month
    form.category.choices = dummy_category
    form.category.choices.append((0, 'All'))
    form.year.choices = dummy_year
    form.month.choices = dummy_month
    bill_bracket = []
    # TODO: Get bill data from the category and search_date
    for i in dummy_bill:
        tmp = EditBillForm(i['id'], i['cost'], i['category'], i['comment'], i['date'])
        tmp.category.choices = dummy_category
        bill_bracket.append(tmp)
    if request.method == 'POST':
        form_keys = list(request.form.keys())
        if 'form-name' in form_keys:
            if request.form['form-name'] == 'search-bill':
                if all( x in form_keys for x in ['date', 'month', 'year', 'category']):
                    category = int(request.form['category'])
                    if request.form['date']:
                        time_condition = date(request.form['date'])
                    else:
                        if request.form['year'] != 0 and request.form['month'] != 0:
                            time_condition = (1, (int(request.form['year']), int(request.form['month'])))
                        elif request.form['year'] != 0:
                            time_condition = (2, int(request.form['year']))
                        elif request.form['month'] != 0:
                            time_condition = (3, int(request.form['month']))
                        else:
                            print("Unexpect situation from searching")
                            # Flash and return search 
                else:
                    print("Unexpect situation that year, month, date not in request")
            else:
                print("Unexpect form-name")
                return redirect(url_for('add_bill', category=category, time_condition=time_condition))
        elif 'edit-index' in form_keys:
            edit_or_delete_bill(request.form)
        else:
            # Nothing happend with POST method?
            redirect(url_for('add_bill'))
        return redirect(url_for('add_bill'))
    return render_template('search_bill.html', form=form, bills=bill_bracket, title='Search Bill')


@app.route("/user_profile")
def user_profile():
    user_form = UserProfileForm()
    password_form = ChangePasswordForm()
    if user_form.validate_on_submit():
        return redirect(url_for('user_profile'))
    if password_form.validate_on_submit():
        return redirect(url_for('user_profile'))
    # TODO: Direct to the home page
    return render_template('user_profile.html', user_form=user_form, \
                           password_form=password_form, title="User Profile", user=dummy_user)

@app.route("/categroy/<int:category_id>")
def category_page(category_id):
    form = ChangeCategoryOption()
    bill_bracket = []
    # TODO: Bill this month or last seven days
    for i in dummy_bill:
        tmp = EditBillForm(i['id'], i['cost'], i['category'], i['comment'], i['date'])
        tmp.category.choices = dummy_category
        bill_bracket.append(tmp)
    return render_template('category_page.html', category=dummy_category[category_id-1][1], bills=bill_bracket, form=form)

