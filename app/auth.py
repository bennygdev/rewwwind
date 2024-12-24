from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from . import db
from .models import User
from .forms import LoginForm, RegisterForm, UsernameForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    emailUsername = form.emailUsername.data
    password = form.password.data
        
    user = User.query.filter((User.email == emailUsername) | (User.username == emailUsername)).first()

    if user and check_password_hash(user.password, password):
      login_user(user, remember=True)
      return redirect(url_for('views.home'))
    else:
      # form.password.errors.append('Invalid email or password')
      flash('Invalid email or password', 'error')

  return render_template("auth/login.html", user=current_user, form=form)

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  print("Logged out user")
  return redirect(url_for('views.home')) # switch to home

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Extract form data
        first_name = form.firstName.data
        last_name = form.lastName.data
        email = form.email.data
        password = form.password.data
        
        # Check if the email already exists
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('An account with that email already exists.', 'error')
            return render_template("auth/register.html", user=current_user, form=form)
        
        # Additional validation checks (already handled by WTForms)
        if not first_name or not last_name:
            flash('All fields are required.', 'error')
            return render_template("auth/register.html", user=current_user, form=form)

        # add user to database
        new_user = User(
          first_name = first_name, 
          last_name = last_name,
          username = f"User{User.query.count() + 1}",
          email = email,
          password = generate_password_hash(password, method='pbkdf2:sha256'),
          role_id = 1
        )
        db.session.add(new_user)
        db.session.commit()
        print('account created successfully')
        
        session['user_id'] = new_user.id
        return redirect(url_for('auth.register_step2'))
    
    # actually not proper validation, needs to be updated later
    if form.confirmPassword.errors:
      flash("Passwords must match", "error")

    if form.password.errors:
       flash("Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")

    # debugger
    if form.errors:
        print("Form validation errors:")
        for field, error_messages in form.errors.items():
            print(f"{field}: {error_messages}")

    return render_template("auth/register.html", user=current_user, form=form)

@auth.route('/register-2', methods=['GET', 'POST'])
def register_step2():
  form = UsernameForm()
  user_id = session.get('user_id')

  if user_id is None:
    flash("Please register an account first.", "error")
    return redirect(url_for('auth.register'))
  
  user = User.query.get(user_id)
  if not user:
    flash("User not found. Please register again.", "error")
    return redirect(url_for('auth.register'))
  
  if form.validate_on_submit():
    username_exists = User.query.filter_by(username=form.username.data).first()
    if username_exists:
      flash('An account with that username already exists.', 'error')
      return render_template("auth/setUsername.html", user=current_user, form=form)

    # update
    user.username = form.username.data

    db.session.commit()
    session.pop('user_id', None)
    print("Name change success")
    return redirect(url_for('auth.login'))

  return render_template("auth/setUsername.html", user=current_user, form=form)