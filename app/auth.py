from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from . import db, mail, oauth
from .models import User, UserVoucher, Voucher
from .forms import LoginForm, RegisterForm, UsernameForm, RequestResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from dotenv import load_dotenv
import os
from secrets import token_urlsafe
from .identicon import create_identicon
from datetime import datetime, timedelta

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

    # add voucher
    firstoff_voucher = Voucher.query.filter_by(voucher_code='FIRSTOFF10').first()
    if firstoff_voucher:
      user_voucher = UserVoucher(
        user_id=user.id,
        voucher_id=firstoff_voucher.id,
        expires_at=datetime.now() + timedelta(days=firstoff_voucher.expiry_days)
      )
      db.session.add(user_voucher)
      db.session.commit()
      print('First-time purchase voucher assigned to Google user')

    freeship_voucher = Voucher.query.filter_by(voucher_code='FREESHIP').first()
    if freeship_voucher:
      user_voucher = UserVoucher(
        user_id=user.id,
        voucher_id=freeship_voucher.id,
        expires_at=datetime.now() + timedelta(days=freeship_voucher.expiry_days)
      )
      db.session.add(user_voucher)
      db.session.commit()
      print('Free-ship purchase voucher assigned to Google user')

  login_user(user, remember=True)
  # flash('Logged in successfully!', 'success')
  return redirect(url_for('views.home'))

# Normal login
@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    try:
      login_user(form.user, remember=True)
      return redirect(url_for('views.home'))
    except Exception as e:
      flash('An unexpected error occurred. Please try again.', 'error')
      return render_template("auth/login.html", user=current_user, form=form)

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
      try:
        # Extract form data
        first_name = form.firstName.data
        last_name = form.lastName.data
        email = form.email.data
        password = form.password.data
        
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
        
        # add voucher
        firstoff_voucher = Voucher.query.filter_by(voucher_code='FIRSTOFF10').first()
        if firstoff_voucher:
          user_voucher = UserVoucher(
              user_id=new_user.id,
              voucher_id=firstoff_voucher.id,
              expires_at=datetime.now() + timedelta(days=firstoff_voucher.expiry_days)
          )
          db.session.add(user_voucher)
          db.session.commit()
          print('First-time purchase voucher assigned successfully')

        session['user_id'] = new_user.id
        return redirect(url_for('auth.register_step2'))
      except Exception as e:
        db.session.rollback()
        flash("An unexpected error occurred. Please try again.", "error")

    return render_template("auth/register.html", user=current_user, form=form)

def generate_user_identicon(username):
  filename = f"identicon_{username}.png"
    
  static_folder = os.path.join(current_app.root_path, 'static', 'profile_pics')
    
  os.makedirs(static_folder, exist_ok=True)
    
  filepath = os.path.join(static_folder, filename)
    
  try:
    create_identicon(
      username=username,
      filename=filepath,
      avatar_size=5, # 5x5 grid
      img_size_per_cell=100 # 100 pixels per cell
    )
        
    # Return just the filename
    return filename
  except Exception as e:
    print(f"Error generating identicon: {e}")
    return 'profile_image_default.jpg'

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
    try:
      # update
      user.username = form.username.data

      identicon_path = generate_user_identicon(user.username)
      user.image = identicon_path

      db.session.commit()
      session.pop('user_id', None)
      flash("Account created successfully! Please log in with your new account.", "success")
      return redirect(url_for('auth.login'))
    except Exception as e:
      db.session.rollback()
      flash("An unexpected error occurred. Please try again.", "error")

  return render_template("auth/setUsername.html", user=None, form=form)

def send_reset_email(user):
  current_app.config['UPDATE_MAIL_CONFIG']('auth')

  token = user.get_reset_token()

  reset_link = url_for('auth.reset_token', token=token, _external=True)

  # image_path = os.path.join(current_app.root_path, 'static', 'media', 'abstractheader1.jpg')

  html_body = render_template('email/reset_password.html', user=user,reset_link=reset_link)

  msg = Message(
    'Password Reset Request', 
    sender=('Rewwwind Help', current_app.config['MAIL_USERNAME']), 
    recipients=[user.email],
    html=html_body
  )

  # with open(image_path, 'rb') as img:
  #   msg.attach(
  #     'abstractheader1.jpg',
  #     'image/jpeg',
  #     img.read(),
  #     'inline',
  #     headers={'Content-ID': '<header_image>'} 
  #   )
  mail.send(msg)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
  if current_user.is_authenticated:
    return redirect(url_for('views.home'))

  form = RequestResetForm() 

  if form.validate_on_submit():
    try:
      send_reset_email(form.user)
      flash('An email has been sent with instructions to reset your password.', 'info')
      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
      return redirect(url_for('auth.login'))
    except Exception as e:
      print(e)
      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
          'success': False,
          'message': 'Failed to send reset email'
        })
      flash('An unexpected error occurred. Please try again.', 'error')
  elif request.method == 'POST':
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      return jsonify({
        'success': False,
        'errors': {field: errors for field, errors in form.errors.items()}
      })

  return render_template("auth/resetPasswordRequest.html", user=current_user, form=form)

# need to update: disallow same previous password and both passwords need to match
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for('views.home'))
  
  user = User.verify_reset_token(token)
  if user is None:
    flash("That is an invalid or expired token", "error")
    return redirect(url_for('auth.reset_password_request'))
  
  form = ResetPasswordForm(user)
  if form.validate_on_submit():
    try:
      # update
      user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

      db.session.commit()
      flash("Your password has been updated! You are now able to log in. ", "success")
      return redirect(url_for('auth.login'))
    except Exception as e:
      db.session.rollback()
      flash("An unexpected error occurred. Please try again.", "error")
  
  return render_template("auth/reset_token.html", user=current_user, form=form)