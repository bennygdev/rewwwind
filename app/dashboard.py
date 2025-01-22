from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .forms import UpdatePersonalInformation, ChangePasswordForm, BillingAddressForm, PaymentMethodForm, ChangeEmailForm
from .models import User, BillingAddress, PaymentInformation, PaymentType, Review, Cart
from .roleDecorator import role_required
from . import db
import secrets
import os
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

dashboard = Blueprint('dashboard', __name__)
# Overview, profile page, settings page

@dashboard.route('/overview')
@login_required
@role_required(1, 2, 3)
def overview():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    if current_user.image.startswith('http'):
      image_file = current_user.image
    else:
      image_file = url_for('static', filename="profile_pics/" + current_user.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  # Header statistics
  customer_label1 = "Total Products Bought"
  customer_label2 = "Total Money Spent"
  customer_label3 = "Total Vouchers Available"
  
  admin_label1 = "Total Customers"
  admin_label2 = "Total Revenue"
  admin_label3 = "Total Orders"

  # do an if statement to check role, to return the variable of the value of either admin or customer

  # revenue - just sum the cost of all orders total paid
  # but even that we're paying the trade-ins, but that wouldn't be practical since trade-ins are rewarded with store credits instead

  return render_template("dashboard/overview.html", user=current_user, image_file=image_file)

@dashboard.route('/profile')
@login_required
@role_required(1, 2, 3)
def user_profile():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    if current_user.image.startswith('http'):
      image_file = current_user.image
    else:
      image_file = url_for('static', filename="profile_pics/" + current_user.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  return render_template("dashboard/profile/profile.html", user=current_user, image_file=image_file)

@dashboard.route('/settings')
@login_required
@role_required(1, 2, 3)
def user_settings():
  return render_template("dashboard/settings/settings.html", user=current_user)

@dashboard.route('/settings/update-personal-information')
@login_required
@role_required(1, 2, 3)
def update_personal_information():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    if current_user.image.startswith('http'):
      image_file = current_user.image
    else:
      image_file = url_for('static', filename="profile_pics/" + current_user.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  return render_template("dashboard/settings/updatePersonalInfo.html", user=current_user, image_file=image_file)

@dashboard.route('/settings/change-email', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def change_email():
  form = ChangeEmailForm()

  if form.validate_on_submit():
    email_exists = User.query.filter_by(email=form.email.data).first()

    if form.email.data == current_user.email:
      flash("New email cannot be the same as your email.", "error")
      return render_template("dashboard/settings/changeEmail.html", user=current_user, form=form)

    if email_exists:
      flash("This email is already taken. Please try again.", "error")
      return render_template("dashboard/settings/changeEmail.html", user=current_user, form=form)
    
    current_user.email = form.email.data
    db.session.commit()
    flash("Your email has been updated!", "success")
    return redirect(url_for('dashboard.update_personal_information'))

  return render_template("dashboard/settings/changeEmail.html", user=current_user, form=form)

@dashboard.route('/settings/delete-account', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def delete_account():
  selectedUser = User.query.get_or_404(current_user.id)

  try:
    # Delete all user related info
    PaymentInformation.query.filter_by(user_id=selectedUser.id).delete()
    BillingAddress.query.filter_by(user_id=selectedUser.id).delete()
    Review.query.filter_by(user_id=selectedUser.id).delete()
    Cart.query.filter_by(user_id=selectedUser.id).delete()

    # No orders and tradeins since i think website should store them as safety
        
    db.session.delete(selectedUser)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    flash("An error occurred while deleting the account. Please try again.", "error")
    print(f"Error deleting account: {str(e)}")

  return redirect(url_for('views.home'))

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

@dashboard.route('/settings/update-personal-information-form', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_personal_information_form():
  form = UpdatePersonalInformation()
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    if current_user.image.startswith('http'):
      image_file = current_user.image
    else:
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

@dashboard.route('/settings/change-password', methods=['GET', 'POST'])
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
  
@dashboard.route('/settings/update-billing-address', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_billing_address():
  form = BillingAddressForm()
  billing_addresses = BillingAddress.query.filter_by(user_id=current_user.id).all()

  if form.validate_on_submit():
    billing_id = request.form.get('billing_id')  # get billing id from hidden field
    billing_address = BillingAddress.query.get(billing_id)
        
    if billing_address and billing_address.user_id == current_user.id:
      billing_address.address_one = form.address_one.data
      billing_address.address_two = form.address_two.data
      billing_address.unit_number = form.unit_number.data
      billing_address.postal_code = form.postal_code.data
      billing_address.phone_number = form.phone_number.data
            
      db.session.commit()
      flash("Billing address updated successfully!", "success")
    else:
      flash("Invalid billing address or unauthorized access.", "error")
        
    return redirect(url_for('dashboard.update_billing_address'))
  
  if form.postal_code.errors:
    flash("Postal code must be in numbers.", "error")

  return render_template("dashboard/settings/updateBillingAddress.html", user=current_user, billing_addresses=billing_addresses, form=form)

@dashboard.route('/settings/add-billing-address', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_billing_address():
  form = BillingAddressForm()

  if form.validate_on_submit():
    billing_address = BillingAddress(
      user_id = current_user.id,
      address_one = form.address_one.data,
      address_two = form.address_two.data,
      unit_number = form.unit_number.data,
      postal_code = form.postal_code.data,
      phone_number = form.phone_number.data
    )

    db.session.add(billing_address)
    db.session.commit()
    flash("Billing address added!", "success")
    return redirect(url_for('dashboard.update_billing_address'))

  if form.postal_code.errors:
    flash("Postal code must be in numbers.", "error")

  return render_template("dashboard/settings/addBillingAddress.html", user=current_user, form=form)

@dashboard.route('/settings/delete-billing/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def delete_billing(id):
  billing_address = BillingAddress.query.get_or_404(id)

  if billing_address and billing_address.user_id == current_user.id:
    db.session.delete(billing_address)
    db.session.commit()
    flash("Billing address deleted.", "success")
    return redirect(url_for('dashboard.update_billing_address'))
  else:
    flash("Invalid billing address or unauthorized access.", "error")
    return redirect(url_for('dashboard.update_billing_address'))
  
@dashboard.route('/settings/update-payment-information', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_payment_information():
  form = PaymentMethodForm()
  payment_methods = PaymentInformation.query.filter_by(user_id=current_user.id).all()

  payment_types = PaymentType.query.all()

  if form.validate_on_submit():
    method_id = request.form.get('method_id')  # get payment id from hidden field
    payment_method = PaymentInformation.query.get(method_id)
        
    if payment_method and payment_method.user_id == current_user.id:
      payment_method.paymentType_id = form.paymentType_id.data
      payment_method.card_name = form.card_name.data
      payment_method.card_number = form.card_number.data
      payment_method.expiry_date = form.expiry_date.data
      payment_method.card_cvv = form.card_cvv.data
            
      db.session.commit()
      flash("Payment method updated successfully!", "success")
    else:
      flash("Invalid Payment method or unauthorized access.", "error")
        
    return redirect(url_for('dashboard.update_payment_information'))
  
  # Handle specific validation errors for any scenario
  if form.errors:
    for field, errors in form.errors.items():
      for error in errors:
        # Convert field name to more readable format
        field_name = {
          'paymentType_id': 'Card Type',
          'card_name': 'Card Name',
          'card_number': 'Card Number',
          'expiry_date': 'Expiry Date',
          'card_cvv': 'CVV'
        }.get(field, field.replace('_', ' ').title())
                
        # Don't include field name if it's already in the error message
        if error.startswith('This appears to be') or error.startswith('Invalid'):
          flash(error, "error")
        else:
          flash(f"{field_name}: {error}", "error")

  return render_template("dashboard/settings/updatePaymentInfo.html", user=current_user, payment_methods=payment_methods, payment_types=payment_types, form=form)

@dashboard.route('/settings/add-payment-method', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_payment_method():
  form = PaymentMethodForm()

  if form.validate_on_submit():
    payment_method = PaymentInformation(
      user_id = current_user.id,
      paymentType_id = form.paymentType_id.data,
      card_name = form.card_name.data,
      card_number = form.card_number.data,
      expiry_date = form.expiry_date.data,
      card_cvv = form.card_cvv.data
    )

    db.session.add(payment_method)
    db.session.commit()
    flash("Payment Method added!", "success")
    return redirect(url_for('dashboard.update_payment_information'))

  # Handle specific validation errors for any scenario
  if form.errors:
    for field, errors in form.errors.items():
      for error in errors:
        # Convert field name to more readable format
        field_name = {
          'paymentType_id': 'Card Type',
          'card_name': 'Card Name',
          'card_number': 'Card Number',
          'expiry_date': 'Expiry Date',
          'card_cvv': 'CVV'
        }.get(field, field.replace('_', ' ').title())
                
        # Don't include field name if it's already in the error message
        if error.startswith('This appears to be') or error.startswith('Invalid'):
          flash(error, "error")
        else:
          flash(f"{field_name}: {error}", "error")

  return render_template("dashboard/settings/addPaymentMethod.html", user=current_user, form=form)

@dashboard.route('/settings/delete-payment-method/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def delete_payment_method(id):
  payment_method = PaymentInformation.query.get_or_404(id)

  if payment_method and payment_method.user_id == current_user.id:
    db.session.delete(payment_method)
    db.session.commit()
    flash("Payment method deleted.", "success")
    return redirect(url_for('dashboard.update_payment_information'))
  else:
    flash("Invalid billing address or unauthorized access.", "error")
    return redirect(url_for('dashboard.update_payment_information'))