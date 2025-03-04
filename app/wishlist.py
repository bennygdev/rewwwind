from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, current_app, session
from flask_login import login_required, current_user
from sqlalchemy import cast, Integer
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import JSON
from .roleDecorator import role_required
from .forms import AddProductForm, DeleteProductForm, AddProductFormData, AddToCartForm #, EditProductForm
from .models import Product, Category, SubCategory, ProductSubCategory, OrderItem, Cart
from . import db
import os

wishlist = Blueprint('wishlist', __name__)

@wishlist.route('/wishlist')
@login_required
def favourites():
    form = AddToCartForm()

    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to wishlist items to avoid conflicts.\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('auth.login'))

    products_query = Product.query

    # Search logic
    search_query = request.args.get('q', '', type=str)
    if search_query != '':
        products = products_query.filter(Product.name.ilike(f"%{search_query}%"))
        total_products = products.count()
    else:
        products = []
        if current_user.wishlisted_items:
            products = Product.query.filter(Product.id.in_(current_user.wishlisted_items)).all()
        total_products = products.__len__()

    return render_template('views/wishlist.html', 
                           user=current_user, 
                           products=products, 
                           search_query=search_query, 
                           total_products=total_products,
                           form=form)

@wishlist.route('/wishlist/add-item/<int:product_id>', methods=['POST'])
@login_required
def add_favourite(product_id):
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to trade in items to avoid conflicts.\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if current_user.wishlisted_items is None:
            current_user.wishlisted_items = []
        if product_id not in current_user.wishlisted_items:
            current_user.wishlisted_items.append(product_id)
            flag_modified(current_user, "wishlisted_items")
            db.session.commit()
        
        return redirect(url_for('wishlist.favourites'))

@wishlist.route('/wishlist/remove-item/<int:product_id>', methods=['GET', 'POST'])
@login_required
def remove_favourite(product_id):
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to trade in items to avoid conflicts.\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('auth.login'))

    if current_user.wishlisted_items is None:
        current_user.wishlisted_items = []
    current_user.wishlisted_items.remove(product_id)
    flag_modified(current_user, "wishlisted_items")
    db.session.commit()

    # check if the request came from the products page
    referrer = request.referrer
    if referrer and 'wishlist' not in referrer:
      return redirect(referrer)
    
    return redirect(url_for('wishlist.favourites'))

def sync_cart_with_wishlist(product_id):
    if request.method == 'POST':
        # Ensure wishlisted_items exists
        if current_user.wishlisted_items is None:
            current_user.wishlisted_items = []

        # Add product to wishlist if not already there
        if product_id not in current_user.wishlisted_items:
            current_user.wishlisted_items.append(product_id)
            flag_modified(current_user, "wishlisted_items")

        # Update the cart item to be favorited
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.favorite = True
            db.session.commit()

        db.session.commit()
        return jsonify({"status": "success", "favorited": True})