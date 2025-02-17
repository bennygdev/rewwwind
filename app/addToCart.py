from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from .roleDecorator import role_required
from sqlalchemy.orm.attributes import flag_modified
from .models import Cart, Product,Voucher,UserVoucher, VoucherType
from datetime import datetime, timedelta
from .forms import AddToCartForm, ApplyVoucherForm
from . import db


addToCart = Blueprint('addToCart', __name__, template_folder='templates')

@addToCart.route('/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    form = AddToCartForm()
    voucher_form = ApplyVoucherForm()
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    # Fetch suggested products if the cart is empty
    suggested_products = []
    if not cart_items: suggested_products = Product.query.limit(4).all()  # Get suggested products
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart_items)
    # Fetch active vouchers for the user
    vouchers = Voucher.query.filter_by(is_active=True).all()

    return render_template('addToCart/cart.html', cart_items=cart_items, cart_total=cart_total,suggested_products=suggested_products, vouchers=vouchers, form=form, voucher_form=voucher_form)


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


@addToCart.route('/apply-voucher', methods=['GET', 'POST'])
@login_required
def apply_voucher():
  voucher_form=ApplyVoucherForm()

  if request.is_json:
    data = request.get_json()
    voucher_code = data.get('voucher', '').strip().upper()
  # For form submissions
  elif voucher_form.validate_on_submit():
    voucher_code = voucher_form.voucher_code.data.strip().upper()
  else:
    if voucher_form.errors:
      error_message = next(iter(voucher_form.errors.values()))[0]
      return jsonify({"status": "error", "message": error_message}), 400
    return jsonify({"status": "error", "message": "Invalid form submission."}), 400

  try:
    print("Request method:", request.method)
    print("Content type:", request.content_type)
    print("Is JSON?", request.is_json)
    print("Form data:", request.form)
    print("JSON data:", request.get_json(silent=True))

    data = request.get_json()
    print(data)
    voucher_code = data.get('voucher', '').strip().upper()  # Convert to uppercase for case-insensitive match

    print(voucher_code)
    if not voucher_code:
      return jsonify({"status": "error", "message": "Please enter a voucher code."}), 400

    # Find the voucher by code
    voucher = Voucher.query.filter_by(voucher_code=voucher_code).first()
        
    if not voucher:
      return jsonify({"status": "error", "message": "Invalid voucher code."}), 400
        
    if not voucher.is_active:
      return jsonify({"status": "error", "message": "This voucher is no longer active."}), 400

    # Check if user has this voucher
    user_voucher = UserVoucher.query.filter_by(user_id=current_user.id, voucher_id=voucher.id, is_used=False).first()
    if not user_voucher:
      return jsonify({"status": "error", "message": "You don't have this voucher."}), 400

        # Check if voucher is expired
    if datetime.now() > user_voucher.expires_at:
      return jsonify({"status": "error", "message": "This voucher has expired."}), 400

    # Get cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    if not cart_items:
      return jsonify({"status": "error", "message": "Your cart is empty."}), 400
        
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart_items)
        
    # Check for first purchase requirement
    if voucher.criteria:
      for criterion in voucher.criteria:
        if criterion.get('type') == 'first_purchase_only' and criterion.get('value') == 'true':
          if current_user.orderCount > 0:
            return jsonify({"status": "error", "message": "This voucher is only valid for your first purchase."}), 400
                
        if criterion.get('type') == 'min_cart_amount':
          min_amount = float(criterion.get('value', 0))
          if cart_total < min_amount:
            return jsonify({"status": "error", "message": f"Minimum purchase of ${min_amount:.2f} required."}), 400
                    
        if criterion.get('type') == 'min_cart_items':
          min_items = int(criterion.get('value', 0))
          total_items = sum(item.quantity for item in cart_items)
          if total_items < min_items:
            return jsonify({"status": "error", "message": f"Minimum of {min_items} items required."}), 400
        
    # Check category eligibility
    if voucher.eligible_categories and len(voucher.eligible_categories) > 0:
      cart_categories = set()
      for item in cart_items:
        product = Product.query.get(item.product_id)
        category = product.category.category_name if product.category else None
        if category:
          cart_categories.add(category)
            
      eligible_categories = set(voucher.eligible_categories)
            
      # If the voucher is restricted to specific categories
      if not cart_categories.issubset(eligible_categories):
        return jsonify({"status": "error", "message": f"This voucher is only valid for {', '.join(voucher.eligible_categories)} items."}), 400
            
      # If the voucher requires all items to be from a specific category
      if len(eligible_categories) == 1 and len(cart_categories) > 1:
        return jsonify({"status": "error", "message": f"This voucher is only valid when your cart contains only {voucher.eligible_categories[0]} items."}), 400

    # Apply the voucher discount
    discount_amount = 0
        
    # Get voucher type
    voucher_type = VoucherType.query.get(voucher.voucherType_id)
        
    if voucher_type.voucher_type == 'percentage':
      discount_amount = cart_total * (voucher.discount_value / 100)
    elif voucher_type.voucher_type == 'fixed_amount':
      discount_amount = voucher.discount_value
    elif voucher_type.voucher_type == 'free_shipping':
      discount_amount = 5  # Assuming $5 shipping fee
        
    new_total = max(0, cart_total - discount_amount)
        
    # Mark voucher as used (we'll commit this when the order is actually placed)
    # user_voucher.is_used = True
    # db.session.commit()

    return jsonify({
      "status": "success", 
      "new_total": new_total,
      "discount_amount": discount_amount,
      "voucher_applied": voucher.voucher_code
    })
  except Exception as e:
    print(f"Error in apply_voucher: {str(e)}")  # Log the error
    return jsonify({"status": "error", "message": "An error occurred. Please try again."}), 500
        
@addToCart.route('/remove-voucher', methods=['POST'])
@login_required
def remove_voucher():
  try:
    if 'applied_voucher' in session:
      del session['applied_voucher']
    if 'voucher_discount' in session:
      del session['voucher_discount']
            
    return jsonify({
      "status": "success",
      "message": "Voucher removed successfully"
    })
  except Exception as e:
    return jsonify({
      "status": "error",
      "message": "Error removing voucher"
    }), 500