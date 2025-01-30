from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, current_app, session
from flask_login import login_required, current_user
from sqlalchemy import cast, Integer
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import JSON
from .roleDecorator import role_required
from .forms import AddProductForm, DeleteProductForm, AddProductFormData #, EditProductForm
from .models import Product, Category, SubCategory, ProductSubCategory, OrderItem
from . import db
import os

wishlist = Blueprint('wishlist', __name__)

@wishlist.route('/wishlist')
@login_required
def favourites():
    if not current_user.wishlisted_items:
        products = None
    else:
        products = Product.query.filter(Product.id.in_(current_user.wishlisted_items)).all()

    return render_template('dashboard/manageProducts/wishlist.html', user=current_user, products=products)

@wishlist.route('/wishlist/add-item/<int:product_id>', methods=['POST'])
@login_required
def add_favourite(product_id):

    if request.method == 'POST':
        if current_user.wishlisted_items is None:
            current_user.wishlisted_items = []
        if product_id not in current_user.wishlisted_items:
            current_user.wishlisted_items.append(product_id)
            flag_modified(current_user, "wishlisted_items")
            db.session.commit()
        
        return redirect(url_for('wishlist.favourites'))

@wishlist.route('/wishlist/remove-item/<int:product_id>')
@login_required
def remove_favourite(product_id):
    if current_user.wishlisted_items is None:
        current_user.wishlisted_items = []
    current_user.wishlisted_items.remove(product_id)
    flag_modified(current_user, "wishlisted_items")
    db.session.commit()
        
    return redirect(url_for('wishlist.favourites'))