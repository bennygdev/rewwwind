from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

manageAccounts = Blueprint('manageAccounts', __name__)
# Admin account (account listing) and adding accounts (Owner)

@manageAccounts.route('/manage-accounts')
@login_required
@role_required(2, 3)
def accounts_listing():
  totalUsers = 0
  newUsers = 0
  onlineCount = 0


  return render_template("dashboard/manageAccounts/accounts.html", user=current_user, totalUsers=totalUsers, newUsers=newUsers, onlineCount=onlineCount)

# @manageAccounts.route('/account-details')
# @login_required
# @role_required(2, 3)
# def account_details():

@manageAccounts.route('/add-admin-account')
@login_required
@role_required(3)
def add_admin_account():
  return render_template("dashboard/manageAccounts/add_admin_account.html", user=current_user)