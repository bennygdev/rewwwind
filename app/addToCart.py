from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Cart, Product
from .forms import AddToCartForm
from . import db


addToCart = Blueprint('addToCart', __name__, template_folder='templates')

@addToCart.route('/cart', methods=['GET'])
@login_required
def view_cart():
    form = AddToCartForm()
    #print(f"Current user: {current_user}")  # Debugging: Should print user object
    #print(f"Authenticated: {current_user.is_authenticated}")  # Debugging: Should be True
    cart_items = Cart.query.filter_by(user_id=current_user.id).join(Product).all()
    # Fetch suggested products if the cart is empty
    suggested_products = []
    if not cart_items:suggested_products = Product.query.limit(5).all()  # Get 5 suggested products
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart_items)
    return render_template('addToCart/cart.html', cart_items=cart_items, cart_total=cart_total, suggested_products=suggested_products, form=form)


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
    if current_user.role_id in [2,3]:
        flash("Admins and owners are not allowed to add products to their cart to avoid conflicts.\n\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('productPagination.product_detail', product_id=product_id, not_customer=True))
    #cartForm = AddToCartForm()
    product = Product.query.filter_by(id=product_id).first() # query the related product
    condition_index = request.form.get("condition")
    if condition_index is None:
        flash("Please select a condition.", "error")
        return redirect(url_for('addToCart.view_cart'))

    try:
        selected_condition = product.conditions[int(condition_index)]
    except (IndexError, ValueError):
        flash("Invalid condition selected.", "error")
        return redirect(url_for("some_page"))
    # Get the selected condition
    selected_condition = product.conditions[int(request.form.get("condition"))]  # Fetch condition from form
    # Check if the item with the same condition is already in the cart
    existing_item = Cart.query.filter_by(user_id=current_user.id,product_id=product_id,product_condition=selected_condition).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        new_item = Cart(user_id=current_user.id, product_id=product_id, product_condition=selected_condition, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    #flash("Item added to cart!")
    return redirect(url_for('addToCart.view_cart'))