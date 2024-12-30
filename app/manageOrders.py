from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

manageOrders = Blueprint('manageOrders', __name__)
# Orders page

@manageOrders.route('/manage-orders')
@login_required
@role_required(1, 2, 3)
def manage_orders():
  return render_template("dashboard/manageOrders/orders.html", user=current_user)