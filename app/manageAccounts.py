from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .roleDecorator import role_required
from .models import User
from .forms import AdminChangeUserInfoForm, ChangePasswordForm
from . import db
from datetime import datetime, timedelta
from math import ceil
from flask import request

manageAccounts = Blueprint('manageAccounts', __name__)
# Admin account (account listing) and adding accounts (Owner)

# Online will be done later
@manageAccounts.route('/manage-accounts')
@login_required
@role_required(2, 3)
def accounts_listing():
  accounts = User.query.all()

  totalUsers = User.query.count()

  # get new users in the last 7 days
  seven_days_ago = datetime.utcnow() - timedelta(days=7)
  newUsers = User.query.filter(User.created_at >= seven_days_ago).count()

  # newUsers = 0
  onlineCount = 0

  # pagination
  page = request.args.get('page', 1, type=int)
  per_page = 10

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
    accounts_query = User.query.filter(User.username.ilike(f"%{search_query}%"))
  else:
    accounts_query = User.query

  # pagination logic
  total_accounts = accounts_query.count()
  accounts = accounts_query.order_by(User.id).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_accounts / per_page)

  return render_template("dashboard/manageAccounts/accounts.html", user=current_user, totalUsers=totalUsers, newUsers=newUsers, onlineCount=onlineCount, accounts=accounts, total_pages=total_pages, current_page=page, search_query=search_query)

@manageAccounts.route('/account-details/<int:id>')
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

  formatted_created_at = selectedUser.created_at.strftime("%d %B %Y")

  image_file = url_for('static', filename="profile_pics/" + selectedUser.image)

  if selectedUser.image:
    if selectedUser.image.startswith('http'):
      image_file = selectedUser.image
    else:
      image_file = url_for('static', filename="profile_pics/" + selectedUser.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  return render_template("dashboard/manageAccounts/account_details.html", user=current_user, selectedUser=selectedUser, formatted_created_at=formatted_created_at, image_file=image_file)

@manageAccounts.route('/delete-account/<int:id>', methods=['GET', 'POST'])
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

  db.session.delete(selectedUser)
  db.session.commit()

  flash("Account successfully deleted.", "info")
  return redirect(url_for('manageAccounts.accounts_listing'))

@manageAccounts.route('/edit-account/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def edit_account(id):
  form = AdminChangeUserInfoForm()

  selectedUser = User.query.get_or_404(id)

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
    
    if form.username.data != selectedUser.username:
      user = User.query.filter_by(username=form.username.data).first()
      if user:
        flash("That username is taken. Please choose another one.", "error")
        return render_template("dashboard/manageAccounts/edit_account.html", user=current_user, form=form, selectedUser=selectedUser)
      
    if form.email.data != selectedUser.email:
      user = User.query.filter_by(email=form.email.data).first()
      if user:
        flash("That email is taken. Please choose another one.", "error")
        return render_template("dashboard/manageAccounts/edit_account.html", user=current_user, form=form, selectedUser=selectedUser)
      
    selectedUser.first_name = form.firstName.data
    selectedUser.last_name = form.lastName.data
    selectedUser.username = form.username.data
    selectedUser.email = form.email.data
    db.session.commit()
    flash("Account has been updated.", 'success')
    return redirect(url_for('manageAccounts.accounts_listing'))

  elif request.method == 'GET':
    form.firstName.data = selectedUser.first_name
    form.lastName.data = selectedUser.last_name
    form.username.data = selectedUser.username
    form.email.data = selectedUser.email


  return render_template("dashboard/manageAccounts/edit_account.html", user=current_user, form=form, selectedUser=selectedUser)

@manageAccounts.route('/change-account-password/<int:id>', methods=['GET', 'POST'])
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
    if check_password_hash(selectedUser.password, form.password.data):
      flash("New password cannot be the same as the previous password", "error")
      return render_template("dashboard/manageAccounts/changePassword.html", user=current_user, form=form, selectedUser=selectedUser)
    
    # update
    selectedUser.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
    db.session.commit()
    flash("Password updated successfully.", "success")
    return redirect(url_for('manageAccounts.accounts_listing'))
  
  if form.confirmPassword.data != form.password.data:
    flash("Both passwords must match.", "error")
    return render_template("dashboard/manageAccounts/changePassword.html", user=current_user, form=form, selectedUser=selectedUser)
  
  if form.password.errors:
    flash("Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.", "error")
    return render_template("dashboard/manageAccounts/changePassword.html", user=current_user, form=form, selectedUser=selectedUser)

  return render_template("dashboard/manageAccounts/changePassword.html", user=current_user, form=form, selectedUser=selectedUser)

@manageAccounts.route('/add-admin-account')
@login_required
@role_required(3)
def add_admin_account():
  return render_template("dashboard/manageAccounts/add_admin_account.html", user=current_user)