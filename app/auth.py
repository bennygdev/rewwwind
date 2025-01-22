from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from . import db, mail, oauth
from .models import User
from .forms import LoginForm, RegisterForm, UsernameForm, RequestResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from dotenv import load_dotenv
import os
from secrets import token_urlsafe

auth = Blueprint('auth', __name__)

load_dotenv()

# Google login
@auth.route('/login/google')
def google_login():
  nonce = token_urlsafe(32)
  session['nonce'] = nonce
  redirect_uri = url_for('auth.google_callback', _external=True)
  return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

@auth.route('/callback')
def google_callback():
  token = oauth.google.authorize_access_token()
  user_info = oauth.google.parse_id_token(token, nonce=session.pop('nonce', None))
    
  # print(user_info)

  user = User.query.filter_by(email=user_info['email']).first()

  if user:
    if not user.google_account:
      flash("Email already registered. Use your email and password to login.", "error")
      return redirect(url_for('auth.login'))
  else:
    user = User(
      first_name=user_info.get('given_name', ''),
      last_name=user_info.get('family_name', ''),
      username=user_info.get('name', ''),
      email=user_info['email'],
      image=user_info.get('picture', 'profile_image_default.jpg'),
      google_account=True,
      orderCount=0,
      role_id=1 
    )
    db.session.add(user)
    db.session.commit()

  login_user(user, remember=True)
  # flash('Logged in successfully!', 'success')
  return redirect(url_for('views.home'))

# Normal login
@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    emailUsername = form.emailUsername.data
    password = form.password.data
        
    user = User.query.filter((User.email == emailUsername) | (User.username == emailUsername)).first()

    if user:
      if not user.google_account:  # check if user is a regular account
        if check_password_hash(user.password, password):
          login_user(user, remember=True)
          return redirect(url_for('views.home'))
        else:
          flash('Invalid password', 'error')
      else:  # if user signed up with google, display message
        flash('This account was created with Google Sign-In. Please use Google login.', 'info')
    else:
      flash('Invalid email or username.', 'error')

  return render_template("auth/login.html", user=current_user, form=form)

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  try: # shelve removal (for addproductform)
    shelve_path = os.path.join(current_app.instance_path, 'shelve.db')
    # if os.path.exists(shelve_path):
    #   os.remove(shelve_path)
    #   print("Shelve db has been removed.")
    for ext in ['.bak', '.dat', '.dir']:
      aux = shelve_path + ext
      if os.path.exists(aux):
        os.remove(aux)
        print(f"Shelve auxiliary file {aux} has been removed.")
  except Exception as e:
    print(f"Error removing shelve in auth.py: {e}")
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
          image = None,
          password = generate_password_hash(password, method='pbkdf2:sha256'),
          orderCount = 0,
          role_id = 1
        )
        db.session.add(new_user)
        db.session.commit()
        print('account created successfully')
        
        session['user_id'] = new_user.id
        return redirect(url_for('auth.register_step2'))
    
    # actually not proper validation, needs to be updated later
    if form.confirmPassword.data != form.password.data:
      flash("Passwords must match", "error")

    if form.password.errors:
      flash("Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.", "error")

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
    flash("Account created successfully! Please log in with your new account.", "success")
    return redirect(url_for('auth.login'))

  return render_template("auth/setUsername.html", user=current_user, form=form)

def send_reset_email(user):
  token = user.get_reset_token()
  msg = Message('Password Reset Request', sender='rewwwindhelp@gmail.com', recipients=[user.email])
  msg.body = f'''To reset your password, visit the following link:
  {url_for('auth.reset_token', token=token, _external=True)}

  The link will expire in 30 minutes.

  If you did not make this request then simply ignore this email and no changes will be made.
  '''
  mail.send(msg)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
  print(os.getenv("EMAIL_USER")) 
  print(os.getenv("EMAIL_PASS")) 

  if current_user.is_authenticated:
    return redirect(url_for('views.home'))

  form = RequestResetForm() 

  if form.validate_on_submit():
    # Add this validation to auth later
    user = User.query.filter_by(email=form.email.data).first()
    
    if user:
      if user.google_account: 
        flash("This email is linked to a Google account. Please sign in with Google.", "info")
        return redirect(url_for('auth.login'))
      else:
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    else:
      # Flash message for non-existing accounts
      flash('There is no account with that email. You must register first', 'error')
      return render_template("auth/resetPasswordRequest.html", user=current_user, form=form)

  return render_template("auth/resetPasswordRequest.html", user=current_user, form=form)

# need to update: disallow same previous password and both passwords need to match
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  form = ResetPasswordForm()
  if current_user.is_authenticated:
    return redirect(url_for('views.home'))
  
  user = User.verify_reset_token(token)
  if user is None:
    flash("That is an invalid or expired token", "error")
    return redirect(url_for('auth.reset_password_request'))
  
  if form.validate_on_submit():
    if check_password_hash(user.password, form.password.data):
      flash("New password cannot be the same as the previous password", "error")
      return redirect(url_for('auth.reset_token', token=token, _external=True))

    # update
    user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

    db.session.commit()
    flash("Your password has been updated! You are now able to log in. ", "success")
    return redirect(url_for('auth.login'))
  
  if form.confirmPassword.data != form.password.data:
    flash("Both passwords must match.", "error")
    return redirect(url_for('auth.reset_token', token=token, _external=True))
  
  if form.password.errors:
    flash("Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.", "error")
    return redirect(url_for('auth.reset_token', token=token, _external=True))
  
  form = ResetPasswordForm()
  return render_template("auth/reset_token.html", user=current_user, form=form)

# @auth.route('/resettest')
# def resettest():
#   form = ResetPasswordForm()
#   return render_template("auth/reset_token.html", user=current_user, form=form)