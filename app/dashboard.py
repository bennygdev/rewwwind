from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify, abort
from flask_login import login_required, current_user
from .forms import UpdatePersonalInformation, ChangePasswordForm, BillingAddressForm, PaymentMethodForm, ChangeEmailForm, Enable2FAForm, Verify2FAForm
from .models import User, BillingAddress, PaymentInformation, PaymentType, Review, Cart, Order, UserVoucher, MailingList, Product, OrderItem
from .roleDecorator import role_required
from . import db, mail
import secrets
import os
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

dashboard = Blueprint('dashboard', __name__)
# Profile page, settings page

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

  orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).limit(6).all()

  # Get recommended products
  recommended_products = get_recommended_products(current_user.id)

  return render_template("dashboard/profile/profile.html", user=current_user, image_file=image_file, orders=orders, recommended_products=recommended_products)

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

  if current_user.google_account:
    abort(404)

  if form.validate_on_submit():
    try:
      current_user.email = form.email.data
      db.session.commit()
      flash("Your email has been updated!", "success")
      return redirect(url_for('dashboard.update_personal_information'))
    except Exception as e:
      db.session.rollback()
      flash("An unexpected error occurred. Please try again.", "error")

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
    UserVoucher.query.filter_by(user_id=selectedUser.id).delete()

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
    db.session.commit()
    flash("Your account has been updated!", 'success')
    return redirect(url_for('dashboard.update_personal_information'))

  elif request.method == 'GET':
    form.firstName.data = current_user.first_name
    form.lastName.data = current_user.last_name
    form.username.data = current_user.username

  return render_template("dashboard/settings/updatePersonalInfoForm.html", user=current_user, form=form, image_file=image_file)

@dashboard.route('/settings/change-password', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def change_password():
  form = ChangePasswordForm()

  if current_user.google_account:
    abort(404)

  if form.validate_on_submit():
    try:
      current_user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
      db.session.commit()
      flash("Password updated successfully!", "success")
      return redirect(url_for('dashboard.security_settings'))
    except Exception as e:
      db.session.rollback()
      flash("An unexpected error occurred. Please try again.", "error")

  return render_template('dashboard/settings/changePassword.html', user=current_user, form=form)
  
@dashboard.route('/settings/update-billing-address', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_billing_address():
  form = BillingAddressForm()
  billing_addresses = BillingAddress.query.filter_by(user_id=current_user.id).all()

  if form.validate_on_submit():
    try:
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
        return jsonify({
          'success': True,
          'message': "Billing address updated successfully!"
        })
      else:
        flash("Invalid billing address or unauthorized access.", "error")
        return jsonify({
          'success': False,
          'message': "Invalid billing address or unauthorized access.",
          'errors': {}
        })
    except Exception as e:
      db.session.rollback()
      flash("Unexpected error occurred while saving billing address.", "error")
      return jsonify({
        'success': False,
        'message': "Unexpected error occurred while saving billing address.",
        'errors': {}
      })

  if form.errors:
    return jsonify({
      'success': False,
      'message': "Please correct the errors below.",
      'errors': form.errors
    })

  return render_template("dashboard/settings/updateBillingAddress.html", user=current_user, billing_addresses=billing_addresses, form=form)

@dashboard.route('/settings/add-billing-address', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_billing_address():
  form = BillingAddressForm()

  if form.validate_on_submit():
    try:
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
    except Exception as e:
      db.session.rollback()
      flash("Unexpected error occurred while saving billing address.", "error")

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
    try:
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
        return jsonify({
          'success': True,
          'message': "Payment information updated successfully!"
        })
      else:
        flash("Invalid Payment method or unauthorized access.", "error")
        return jsonify({
          'success': False,
          'message': "Invalid payment information or unauthorized access.",
          'errors': {}
        })    
    except Exception as e:
      db.session.rollback()
      flash("Unexpected error occurred while saving payment information.", "error")
      return jsonify({
        'success': False,
        'message': "Unexpected error occurred while saving payment information.",
        'errors': {}
      })

  if form.errors:
    return jsonify({
      'success': False,
      'message': "Please correct the errors below.",
      'errors': form.errors
    })

  return render_template("dashboard/settings/updatePaymentInfo.html", user=current_user, payment_methods=payment_methods, payment_types=payment_types, form=form)

@dashboard.route('/settings/add-payment-method', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_payment_method():
  form = PaymentMethodForm()

  if form.validate_on_submit():
    try:
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
    except Exception as e:
      db.session.rollback()
      flash("Unexpected error occurred while saving payment information.", "error")

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
  
@dashboard.route('/settings/manage-notifications')
@login_required
@role_required(1, 2, 3)
def manage_notifications():
  mailing_list_entry = MailingList.query.filter_by(email=current_user.email).first()

  return render_template("dashboard/settings/manageNotifications.html", user=current_user, mailing_list_entry=mailing_list_entry)

@dashboard.route('/settings/toggle-marketing-emails', methods=['POST'])
@login_required
@role_required(1, 2, 3)
def toggle_marketing_emails():
  data = request.get_json()
  subscribed = data.get('subscribed', False)
    
  try:
    mailing_list_entry = MailingList.query.filter_by(email=current_user.email).first()
        
    if subscribed and not mailing_list_entry:
      new_entry = MailingList(
        email=current_user.email,
        unsubscribe_token=secrets.token_urlsafe(32)
      )
      db.session.add(new_entry)
    elif not subscribed and mailing_list_entry:
      db.session.delete(mailing_list_entry)
        
    db.session.commit()
    return jsonify({'success': True})
  except Exception as e:
    db.session.rollback()
    return jsonify({'success': False, 'error': str(e)}), 500
  

# PRODUCT RECOMMENDATION ALGORITHM
# HOW THIS WORKS: It analyses the user order history first regardless if it's approved or not. 
# It calculates the ratio of vinyl to books purchased
# It then suggests products based on this ratio, with a maximum of 5 recommendations
# It then ensures the minority category gets at least one recommendation if it's more than 1% of purchases
# It shows products from only one category if the user has only ordered from that category
def get_recommended_products(user_id):
  from collections import defaultdict
  from sqlalchemy import and_
  
  # Get all order items for the user
  orders = Order.query.filter_by(user_id=user_id).all()
  if not orders:
    return None  # No orders, no recommendations
  
  # Count products by category
  category_counts = defaultdict(int)
  order_ids = [order.id for order in orders]
  order_items = OrderItem.query.filter(OrderItem.order_id.in_(order_ids)).all()
  
  for item in order_items:
    product = Product.query.get(item.product_id)
    if product:
      category_counts[product.category_id] += item.quantity
  
  # Calculate ratios
  total_products = sum(category_counts.values())
  if total_products == 0:
    return None
  
  vinyl_count = category_counts.get(1, 0)  # Vinyl category ID = 1
  book_count = category_counts.get(2, 0)   # Book category ID = 2
  
  # Calculate percentage of each category
  vinyl_percentage = (vinyl_count / total_products) * 100 if total_products > 0 else 0
  book_percentage = (book_count / total_products) * 100 if total_products > 0 else 0
  
  # Determine number of recommendations for each category
  max_recommendations = 5
  vinyl_recommendations = 0
  book_recommendations = 0
  
  # If only one category has been ordered
  if vinyl_count > 0 and book_count == 0:
    vinyl_recommendations = max_recommendations
  elif book_count > 0 and vinyl_count == 0:
    book_recommendations = max_recommendations
  else:
    # Enforce minimum of 1 product for minority category if it's at least 1%
    if 1 <= vinyl_percentage < 20:
      vinyl_recommendations = 1
      book_recommendations = min(max_recommendations - vinyl_recommendations, 4)
    elif 1 <= book_percentage < 20:
      book_recommendations = 1
      vinyl_recommendations = min(max_recommendations - book_recommendations, 4)
    else:
      # Calculate recommendations based on percentages
      vinyl_recommendations = round((vinyl_percentage / 100) * max_recommendations)
      book_recommendations = max_recommendations - vinyl_recommendations
      
      # Adjust if rounding error exceeds max_recommendations
      if vinyl_recommendations + book_recommendations > max_recommendations:
        if vinyl_percentage >= book_percentage:
          vinyl_recommendations = max_recommendations - book_recommendations
        else:
          book_recommendations = max_recommendations - vinyl_recommendations
  
  # Get recommended products
  recommended_products = []
  
  # Get vinyl recommendations
  if vinyl_recommendations > 0:
    vinyl_products = Product.query.filter_by(category_id=1).order_by(Product.created_at.desc()).limit(vinyl_recommendations).all()
    recommended_products.extend(vinyl_products)
  
  # Get book recommendations
  if book_recommendations > 0:
    book_products = Product.query.filter_by(category_id=2).order_by(Product.created_at.desc()).limit(book_recommendations).all()
    recommended_products.extend(book_products)
  
  return recommended_products

@dashboard.route('/settings/security')
@login_required
@role_required(1, 2, 3)
def security_settings():
  # no google accounts
  if current_user.google_account:
    flash('Two-factor authentication is not available for Google accounts.', 'warning')
    return redirect(url_for('dashboard.user_settings'))
    
  return render_template("dashboard/settings/security.html", user=current_user)

@dashboard.route('/settings/security/enable-2fa', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def enable_2fa():
  # Only allow non-Google users to access 2FA settings
  if current_user.google_account:
    flash('Two-factor authentication is not available for Google accounts.', 'warning')
    return redirect(url_for('dashboard.user_settings'))
    
  form = Enable2FAForm()
    
  if form.validate_on_submit():
    if current_user.two_factor_enabled:
      flash('Two-factor authentication is already enabled.', 'info')
      return redirect(url_for('dashboard.security_settings'))
        
    # Generate a 6-digit code
    code = current_user.generate_2fa_code()
        
    # Send email with code
    send_2fa_setup_email(current_user, code)
        
    db.session.commit()
    flash('A verification code has been sent to your email. Please verify to enable 2FA.', 'info')
    return redirect(url_for('dashboard.verify_2fa_setup'))
    
  return render_template("dashboard/settings/enable_2fa.html", user=current_user, form=form)

@dashboard.route('/settings/security/verify-2fa', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def verify_2fa_setup():
  # Only non-google can
  if current_user.google_account:
    flash('Two-factor authentication is not available for Google accounts.', 'warning')
    return redirect(url_for('dashboard.user_settings'))
    
  form = Verify2FAForm()
    
  if form.validate_on_submit():
    if current_user.verify_2fa_code(form.code.data):
      current_user.two_factor_enabled = True
      current_user.two_factor_secret = None
      current_user.two_factor_expiry = None
      db.session.commit()
      flash('Two-factor authentication has been successfully enabled.', 'success')
      return redirect(url_for('dashboard.security_settings'))
    else:
      flash('Invalid or expired verification code. Please try again.', 'error')
    
  return render_template("dashboard/settings/verify_2fa.html", user=current_user, form=form)

@dashboard.route('/settings/security/disable-2fa', methods=['POST'])
@login_required
@role_required(1, 2, 3)
def disable_2fa():
  # Only non google can
  if current_user.google_account:
    flash('Two-factor authentication is not available for Google accounts.', 'warning')
    return redirect(url_for('dashboard.user_settings'))
    
  if current_user.two_factor_enabled:
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_expiry = None
    db.session.commit()
    flash('Two-factor authentication has been disabled.', 'success')
    
  return redirect(url_for('dashboard.security_settings'))

def send_2fa_setup_email(user, code):
  current_app.config['UPDATE_MAIL_CONFIG']('auth')
  
  html_body = render_template('email/2fa_setup.html', user=user, code=code)
  
  msg = Message(
    'Set Up Two-Factor Authentication', 
    sender=('Rewwwind Help', current_app.config['MAIL_USERNAME']), 
    recipients=[user.email],
    html=html_body
  )
  
  mail.send(msg)