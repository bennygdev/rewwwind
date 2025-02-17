from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .roleDecorator import role_required
from .models import User, PaymentInformation, BillingAddress, Review, Cart, UserVoucher, Order, Voucher, VoucherType
from .forms import AdminChangeUserInfoForm, ChangePasswordForm, OwnerAddAccountForm
from . import db
from sqlalchemy import func
from datetime import datetime, timedelta
from math import ceil
from flask import request

manageAccounts = Blueprint('manageAccounts', __name__)
# Admin account (account listing) and adding accounts (Owner)

@manageAccounts.route('/manage-accounts')
@login_required
@role_required(2, 3)
def accounts_listing():
  accounts = User.query.order_by(User.created_at.desc()).all()

  totalUsers = User.query.count()

  # get new users in the last 7 days
  seven_days_ago = datetime.utcnow() - timedelta(days=7)
  newUsers = User.query.filter(User.created_at >= seven_days_ago).count()

  # newUsers = 0

  # pagination
  page = request.args.get('page', 1, type=int)
  per_page = 10

  # filters
  role_filter = request.args.get('role', '')

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
    accounts_query = User.query.filter(User.username.ilike(f"%{search_query}%"))
  else:
    accounts_query = User.query

  if role_filter:
    role_id_map = {
      'customer': 1,
      'admin': 2,
      'owner': 3
    }
    if role_filter.lower() in role_id_map:
      accounts_query = accounts_query.filter(User.role_id == role_id_map[role_filter.lower()])

  # pagination logic
  total_accounts = accounts_query.count()
  accounts = accounts_query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_accounts / per_page)

  role_choices = [
    ('customer', 'Customer'),
    ('admin', 'Admin'),
    ('owner', 'Owner')
  ]

  return render_template(
    "dashboard/manageAccounts/accounts.html", 
    user=current_user, 
    totalUsers=totalUsers, 
    newUsers=newUsers, 
    accounts=accounts, 
    total_pages=total_pages, 
    current_page=page, 
    search_query=search_query,
    role_filter=role_filter,
    role_choices=role_choices
  )

@manageAccounts.route('/manage-accounts/account-details/<int:id>')
@login_required
@role_required(2, 3)
def account_details(id):
  selectedUser = User.query.get_or_404(id)

  # admin cannot view admin and owner accounts, but owner can view any
  if current_user.role_id == 2: 
    if selectedUser.role_id in [2, 3]:
      abort(404)

  # admin can only view customer accounts
  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  billing_addresses = BillingAddress.query.filter_by(user_id=selectedUser.id).all()

  payment_informations = PaymentInformation.query.filter_by(user_id=selectedUser.id).all()

  formatted_created_at = selectedUser.created_at.strftime("%d %B %Y")

  image_file = url_for('static', filename="profile_pics/" + selectedUser.image)

  if selectedUser.image:
    if selectedUser.image.startswith('http'):
      image_file = selectedUser.image
    else:
      image_file = url_for('static', filename="profile_pics/" + selectedUser.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  # Only show charts for customers
  if selectedUser.role_id == 1:
    total_orders = Order.query.filter_by(user_id=selectedUser.id, status='Approved').count()
    total_vouchers = UserVoucher.query.filter_by(user_id=selectedUser.id).count()
    total_reviews = Review.query.filter_by(user_id=selectedUser.id).count()
  else:
    total_orders = total_vouchers = total_reviews = 0

  return render_template(
    "dashboard/manageAccounts/account_details.html", 
    user=current_user, 
    selectedUser=selectedUser, 
    formatted_created_at=formatted_created_at, 
    image_file=image_file, 
    billing_addresses=billing_addresses, 
    payment_informations=payment_informations,
    total_orders=total_orders,
    total_vouchers=total_vouchers,
    total_reviews=total_reviews
  )

@manageAccounts.route('/manage-accounts/delete-account/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def delete_account(id):
  selectedUser = User.query.get_or_404(id)

  # admin cannot delete admin and owner accounts, but owner can delete any
  if current_user.role_id == 2: 
    if selectedUser.role_id in [2, 3]:
      abort(404)

  # owner cannot delete owner
  if current_user.role_id == 3:
    if selectedUser.role_id == 3:
      abort(404)

  # admin can only delete customer accounts
  if current_user.role_id == 1: # restrict customer functions
    abort(404)

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
        
    flash("Account and all associated data successfully deleted.", "info")
  except Exception as e:
    db.session.rollback()
    flash("An error occurred while deleting the account. Please try again.", "error")
    print(f"Error deleting account: {str(e)}")

  return redirect(url_for('manageAccounts.accounts_listing'))

@manageAccounts.route('/manage-accounts/edit-account/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def edit_account(id):
  selectedUser = User.query.get_or_404(id)
  form = AdminChangeUserInfoForm(
    original_username=selectedUser.username,
    original_email=selectedUser.email
  )


  # admin cannot edit admin and owner accounts, but owner can edit any
  if current_user.role_id == 2: 
    if selectedUser.role_id in [2, 3]:
      abort(404)

  # owner cannot edit owner
  if current_user.role_id == 3:
    if selectedUser.role_id == 3:
      abort(404)

  # admin can only edit customer accounts
  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  if form.validate_on_submit():
    try:
      selectedUser.first_name = form.firstName.data
      selectedUser.last_name = form.lastName.data
      selectedUser.username = form.username.data
      selectedUser.email = form.email.data
      db.session.commit()
      flash("Account has been updated.", 'success')
      return redirect(url_for('manageAccounts.accounts_listing'))
    except Exception as e:
      db.session.rollback()
      flash('An unexpected error occurred. Please try again.', 'error')

  elif request.method == 'GET':
    form.firstName.data = selectedUser.first_name
    form.lastName.data = selectedUser.last_name
    form.username.data = selectedUser.username
    form.email.data = selectedUser.email


  return render_template("dashboard/manageAccounts/edit_account.html", user=current_user, form=form, selectedUser=selectedUser)

@manageAccounts.route('/manage-accounts/change-account-password/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def change_password(id):
  form = ChangePasswordForm()

  selectedUser = User.query.get_or_404(id)

  # admin cannot change password for admin and owner accounts, but owner can edit any
  if current_user.role_id == 2: 
    if selectedUser.role_id in [2, 3]:
      abort(404)

  # owner cannot edit owner
  if current_user.role_id == 3:
    if selectedUser.role_id == 3:
      abort(404)

  # admin can only edit customer accounts
  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  if form.validate_on_submit():
    try:
      # update
      selectedUser.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
      db.session.commit()
      flash("Password updated successfully.", "success")
      return redirect(url_for('manageAccounts.accounts_listing'))
    except Exception as e:
      db.session.rollback()
      flash("An unexpected error occurred. Please try again.", "error")

  return render_template("dashboard/manageAccounts/changePassword.html", user=current_user, form=form, selectedUser=selectedUser)

@manageAccounts.route('/add-any-account', methods=['GET', 'POST'])
@login_required
@role_required(3)
def add_any_account():
  form = OwnerAddAccountForm()

  if form.validate_on_submit():
    try:
      first_name = form.firstName.data
      last_name = form.lastName.data
      username = form.username.data
      email = form.email.data
      password = form.password.data
      role_id = form.role_id.data
      
      # add user to database
      new_user = User(
        first_name = first_name, 
        last_name = last_name,
        username = username,
        email = email,
        image = None,
        password = generate_password_hash(password, method='pbkdf2:sha256'),
        orderCount = 0,
        role_id = role_id
      )
      db.session.add(new_user)
      db.session.commit()
      flash("Account created successfully.", "success")
      return redirect(url_for('manageAccounts.accounts_listing'))
    except Exception as e:
      db.session.rollback()
      flash('An unexpected error occurred. Please try again.', 'error')

  return render_template("dashboard/manageAccounts/add_any_account.html", user=current_user, form=form)


# Account details charts
@manageAccounts.route('/api/customer/order-trend/<int:user_id>')
@login_required
def get_user_order_trend(user_id):
  orders = db.session.query(
    func.strftime('%Y-%m', Order.approval_date).label('month'),
    func.count(Order.id).label('count')
  ).filter(
    Order.user_id == user_id,
    Order.status == 'Approved'
  ).group_by(
    func.strftime('%Y-%m', Order.approval_date)
  ).order_by(
    func.strftime('%Y-%m', Order.approval_date)
  ).all()
  
  # convert month to a more readable format
  formatted_labels = []
  for order in orders:
    try:
      year_month = order[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(order[0])
    
  return {
    'labels': formatted_labels if orders else [],
    'data': [order[1] for order in orders] if orders else []
  }

@manageAccounts.route('/api/customer/voucher-types/<int:user_id>')
@login_required
def get_user_voucher_types(user_id):
  voucher_types = db.session.query(
    VoucherType.voucher_type,
    func.count(UserVoucher.id).label('count')
  ).join(
    Voucher, Voucher.id == UserVoucher.voucher_id
  ).join(
    VoucherType, VoucherType.id == Voucher.voucherType_id 
  ).filter(
    UserVoucher.user_id == user_id
  ).group_by(
    VoucherType.voucher_type
  ).all()
        
  return {
    'labels': [vt[0] for vt in voucher_types] if voucher_types else [],
    'data': [vt[1] for vt in voucher_types] if voucher_types else []
  }

@manageAccounts.route('/api/customer/review-trend/<int:user_id>')
@login_required
def get_user_review_trend(user_id):
  reviews = db.session.query(
    func.strftime('%Y-%m', Review.created_at).label('month'),
    func.count(Review.id).label('count')
  ).filter(
    Review.user_id == user_id
  ).group_by(
    func.strftime('%Y-%m', Review.created_at)
  ).order_by(
    func.strftime('%Y-%m', Review.created_at)
  ).all()
  
  # convert month to a more readable format
  formatted_labels = []
  for review in reviews:
    try:
      year_month = review[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(review[0])
    
  return {
    'labels': formatted_labels if reviews else [],
    'data': [review[1] for review in reviews] if reviews else []
  }