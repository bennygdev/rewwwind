from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import User
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

# @manageAccounts.route('/account-details')
# @login_required
# @role_required(2, 3)
# def account_details():

@manageAccounts.route('/add-admin-account')
@login_required
@role_required(3)
def add_admin_account():
  return render_template("dashboard/manageAccounts/add_admin_account.html", user=current_user)