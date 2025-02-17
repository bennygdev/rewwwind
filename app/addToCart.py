from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .roleDecorator import role_required
from sqlalchemy.orm.attributes import flag_modified
from .models import Cart, Product,Voucher,UserVoucher
from datetime import datetime, timedelta
from .forms import AddToCartForm
from . import db


addToCart = Blueprint('addToCart', __name__, template_folder='templates')

@addToCart.route('/cart', methods=['GET'])
@login_required
def view_cart():
    form = AddToCartForm()
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    # Fetch suggested products if the cart is empty
    suggested_products = []
    if not cart_items: suggested_products = Product.query.limit(4).all()  # Get suggested products
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart_items)
    # Fetch active vouchers for the user
    vouchers = Voucher.query.filter_by(is_active=True).all()

    return render_template('addToCart/cart.html', cart_items=cart_items, cart_total=cart_total,suggested_products=suggested_products, vouchers=vouchers, form=form)


@addToCart.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()

    for item in cart_items:
        quantity = request.form.get(f'quantities[{item.product_id}]')
        if quantity:
            item.quantity = max(1, int(quantity))

    db.session.commit()

    return redirect(url_for('addToCart.view_cart'))


@addToCart.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    #flash("Item removed from cart!")
    return redirect(url_for('addToCart.view_cart'))

@addToCart.route('/add-to-cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # cartForm = AddToCartForm()
    product = Product.query.filter_by(id=product_id).first()
    condition_index = request.form.get("condition")

    if condition_index is None:
        flash("Please select a condition.", "error")
        return redirect(url_for('addToCart.view_cart'))

    try:
        selected_condition = product.conditions[int(condition_index)]  # Get the selected condition
    except (IndexError, ValueError):
        flash("Invalid condition selected.", "error")
        return redirect(url_for("addToCart.view_cart"))

    # Check if the same item with the same condition exists in the cart
    existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id,
                                         product_condition=selected_condition).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, product_condition=selected_condition,
                        quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash("Item added to cart!", "success")
    return redirect(url_for('addToCart.view_cart'))



#favourites

@addToCart.route('/toggle-favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not cart_item:
        return jsonify({"status": "error", "message": "Cart item not found"}), 400

    cart_item.favorite = not cart_item.favorite  # Toggle favorite status

    # Sync with Wishlist
    if current_user.wishlisted_items is None:
        current_user.wishlisted_items = []

    if cart_item.favorite:
        if product_id not in current_user.wishlisted_items:
            current_user.wishlisted_items.append(product_id)
    else:
        if product_id in current_user.wishlisted_items:
            current_user.wishlisted_items.remove(product_id)

    flag_modified(current_user, "wishlisted_items")
    db.session.commit()

    return jsonify({"status": "success", "favorited": cart_item.favorite})


@addToCart.route('/apply-voucher', methods=['POST'])
@login_required
def apply_voucher():
    print("Voucher request received!")  # Debugging line
    data = request.get_json()
    print("Received data:", data)  # Debugging line

    voucher_id = data.get('voucher', '').strip()

    if not voucher_id:
        return jsonify({"status": "error", "message": "Please select a voucher."}), 400

    voucher = Voucher.query.get(voucher_id)
    if not voucher or not voucher.is_active:
        return jsonify({"status": "error", "message": "Invalid or expired voucher."}), 400

    # Get cart total
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart_items)

    # Check if user meets the voucher conditions
    min_purchase = voucher.criteria.get('min_cart_amount', 0) if voucher.criteria else 0
    if cart_total < min_purchase:
        return jsonify({"status": "error", "message": f"Minimum purchase of ${min_purchase} required."}), 400

    # Apply the voucher discount
    discount_amount = 0
    if voucher.voucherType_id == 1:  # Percentage Discount
        discount_amount = cart_total * (voucher.discount_value / 100)
    elif voucher.voucherType_id == 2:  # Fixed Amount Discount
        discount_amount = voucher.discount_value
    elif voucher.voucherType_id == 3:  # Free Shipping
        discount_amount = 5  # Assuming $5 shipping discount

    new_total = max(0, cart_total - discount_amount)

    print(f"Original Total: {cart_total}, Discount: {discount_amount}, New Total: {new_total}")

    return jsonify({"status": "success", "new_total": new_total})
