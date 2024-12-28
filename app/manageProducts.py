from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .forms import AddProductForm
from .models import Product
from . import db
import os

manageProducts = Blueprint('manageProducts', __name__)

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def product_listings():
    products = Product.query.all()
    for product in products:
      print(url_for('static', filename=product.image_thumbnail))
    return render_template("dashboard/manageProducts/products.html", user=current_user, products=products)