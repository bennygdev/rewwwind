from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from main import app
from .models import Cart, Product  # Ensure Cart and Product models exist
from . import db  # Ensure db is properly set up in your app
from flask_wtf.csrf import CSRFProtect


@app.route('/cart', methods=['GET'])
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    cart_total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)


@app.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity = max(1, quantity)  # Ensure quantity is at least 1
        db.session.commit()
    flash("Cart updated successfully!")
    return redirect(url_for('view_cart'))



@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    flash("Item removed from cart!")
    return redirect(url_for('view_cart'))

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    flash("Item added to cart!")
    return redirect(url_for('view_cart'))

