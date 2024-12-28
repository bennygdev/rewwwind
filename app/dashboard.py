from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .forms import UpdatePersonalInformation, ChangePasswordForm
from .models import User
from .roleDecorator import role_required
from . import db
import secrets
import os
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/overview')
@login_required
@role_required(1, 2, 3)
def overview():
  return render_template("dashboard/overview.html", user=current_user)

@dashboard.route('/profile')
@login_required
@role_required(1, 2, 3)
def user_profile():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)
  return render_template("dashboard/profile/profile.html", user=current_user, image_file=image_file)

@dashboard.route('/settings')
@login_required
@role_required(1, 2, 3)
def user_settings():
  return render_template("dashboard/settings/settings.html", user=current_user)

@dashboard.route('/update-personal-information')
@login_required
@role_required(1, 2, 3)
def update_personal_information():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)
  return render_template("dashboard/settings/updatePersonalInfo.html", user=current_user, image_file=image_file)


def save_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_fn = random_hex + f_ext
  picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

  output_size = (125, 125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)

  i.save(picture_path)

  prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image)
  if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'profile_image_default.jpg':
    os.remove(prev_picture)

  return picture_fn

@dashboard.route('/update-personal-information-form', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_personal_information_form():
  form = UpdatePersonalInformation()
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    image_file = url_for('static', filename="profile_pics/" + current_user.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  # current user because logged in user
  if form.validate_on_submit():

    if form.username.data != current_user.username:
      user = User.query.filter_by(username=form.username.data).first()
      if user:
        flash("That username is taken. Please choose another one.", "error")
        return render_template('dashboard/settings/updatePersonalInfoForm.html', user=current_user, form=form)

    if form.email.data != current_user.email:
      user = User.query.filter_by(email=form.email.data).first()
      if user:
        flash("That email is taken. Please choose another one.", "error")
        return render_template('dashboard/settings/updatePersonalInfoForm.html', user=current_user, form=form)

    if form.picture.data:
      picture_file = save_picture(form.picture.data)
      current_user.image = picture_file
    elif 'remove_image' in request.form and request.form['remove_image'] == 'remove':
      prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image)
      if os.path.exists(prev_picture) and current_user.image != 'profile_image_default.jpg':
        os.remove(prev_picture)
      current_user.image = 'profile_image_default.jpg' 

    current_user.first_name = form.firstName.data
    current_user.last_name = form.lastName.data
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash("Your account has been updated!", 'success')
    return redirect(url_for('dashboard.update_personal_information'))

  elif request.method == 'GET':
    form.firstName.data = current_user.first_name
    form.lastName.data = current_user.last_name
    form.username.data = current_user.username
    form.email.data = current_user.email

  if form.picture.errors:
    flash("File does not have an approved extension: jpg, png", "error")

  return render_template("dashboard/settings/updatePersonalInfoForm.html", user=current_user, form=form, image_file=image_file)

@dashboard.route('/change-password', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def change_password():
  form = ChangePasswordForm()

  if form.validate_on_submit():
    if check_password_hash(current_user.password, form.password.data):
      flash("New password cannot be the same as the previous password", "error")
      return render_template('dashboard/settings/changePassword.html', user=current_user, form=form)
    
    # update
    current_user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
    db.session.commit()
    flash("Password updated successfully!", "success")
    return redirect(url_for('dashboard.update_personal_information'))
  
  if form.confirmPassword.data != form.password.data:
    flash("Both passwords must match.", "error")
    return render_template('dashboard/settings/changePassword.html', user=current_user, form=form)
  
  if form.password.errors:
    flash("Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.", "error")
    return render_template('dashboard/settings/changePassword.html', user=current_user, form=form)

  return render_template('dashboard/settings/changePassword.html', user=current_user, form=form)
  
@dashboard.route('/update-billing-address')
@login_required
@role_required(1, 2, 3)
def update_billing_address():
  return render_template("dashboard/settings/updateBillingAddress.html", user=current_user)

@dashboard.route('/update-payment-information')
@login_required
@role_required(1, 2, 3)
def update_payment_information():
  return render_template("dashboard/settings/updatePaymentInfo.html", user=current_user)