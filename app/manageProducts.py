from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

manageProducts = Blueprint('manageProducts', __name__)
# Products page

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def product_listings():
  return render_template("dashboard/manageProducts/products.html", user=current_user)