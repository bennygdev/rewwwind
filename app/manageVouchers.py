from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

manageVouchers = Blueprint('manageVouchers', __name__)
# Vouchers page

@manageVouchers.route('/manage-vouchers')
@login_required
@role_required(2, 3)
def vouchers_listing():
  return render_template("dashboard/manageVouchers/vouchers.html", user=current_user)