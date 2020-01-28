from flask import Blueprint
from flask import render_template, request, url_for, redirect, flash
from account_book import bcrypt, db
from account_book.users.forms import LoginForm, RegistrationForm, UserProfileForm, ChangePasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from account_book.model import User
from account_book.users.utils import save_picture, delete_old_pic
from account_book.utils import db_add


users = Blueprint('users', __name__)


@users.route("/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.home'))
            else:
                flash("Login Unsuccessful, please check your username and password", "danger")
        else:
            flash("User doesn't exist, please try again or register new user", "danger")
    return render_template('login.html', form=form, title="Login")


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email = form.email.data
        new_user = User(username=username, name=name, password=hashed_password, email=email)
        try:
            db_add(new_user)
            return redirect(url_for('users.login'))
        except Exception as e:
            flash("Something Wrong", 'danger')
    return render_template('register.html', form=form, title="Registration")


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route("/user_profile", methods=['POST', 'GET'])
@login_required
def user_profile():
    user_form = UserProfileForm()
    password_form = ChangePasswordForm()
    if user_form.validate_on_submit():
        if user_form.picture.data:
            picture_file = save_picture(user_form.picture.data)
            delete_old_pic(current_user.image_file)
            current_user.image_file = picture_file
        current_user.name = user_form.name.data
        current_user.email = user_form.email.data
        current_user.month_budget = user_form.month_budget.data
        current_user.week_budget = user_form.week_budget.data
        current_user.day_budget = user_form.day_budget.data
        db.session.commit()
        flash(" Your account has been updated! ", "success")
        return redirect(url_for('users.user_profile'))
    if password_form.validate_on_submit():
        password = password_form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash(" Your account has been updated! ", "success")
        
        return redirect(url_for('main.home'))
    return render_template('user_profile.html', user_form=user_form,
                           password_form=password_form, title="User Profile", user=current_user)
