from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Product
from . import db

productPagination = Blueprint('productPagination', __name__)

@productPagination.route('/')
def product_pagination():
  products = Product.query.all()
  return render_template("/productPagination/products.html", user=current_user, products=products)

@productPagination.route('/product/<int:product_id>')
def product_detail(product_id):
    # Query the database for the product
    product = Product.query.get(product_id) 
    return render_template("/productPagination/productPage.html", user=current_user, product=product)