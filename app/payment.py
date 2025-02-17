from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import flag_modified
from .roleDecorator import role_required
from .models import Product, Order, OrderItem, Cart, PaymentInformation, BillingAddress, Pickup, Voucher, UserVoucher
from .forms import BillingAddressForm, SelectDeliveryTypeForm, PickupForm, VoucherSelectForm
from . import db
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime

import stripe

payment = Blueprint('payment', __name__)

@payment.route('/temp/<int:product_id>', methods=['POST'])
@login_required
def create_temp_cart(product_id): # to prevent errors.
    # Prevent admins and owners from purchasing
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to purchase in order to avoid conflicts.\n\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('productPagination.product_detail', product_id=1, not_customer=True))
    
    if request.method == 'POST':
        # Retrieve the product
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404)

        # Validate the product condition
        getcondition = request.form.get('condition')
        if getcondition not in ['Brand New', 'Like New', 'Lightly Used', 'Well Used']:
            abort(404)

        # Find the selected condition
        condition = [con for con in product.conditions if con.get('condition') == getcondition]
        if not condition:
            abort(404)
        
        c_challenge = current_user.cart_items
        if not c_challenge:
            temp_cart = Cart(
                user_id=current_user.id,
                product_id=product_id,
                product_condition=condition[0],
                quantity=1
            )
            db.session.add(temp_cart)
            db.session.commit()
        else:
            existing_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id, product_condition=product.conditions[0]).first()
            if existing_item:
                existing_item.quantity += 1
                flag_modified(existing_item, 'quantity')
            else:
                new_item = Cart(user_id=current_user.id, product_id=product_id, product_condition=product.conditions[0], quantity=1)
                db.session.add(new_item)
            db.session.commit()

    return redirect(url_for('payment.select_ship'))

@payment.route('/checkout/select_shipping', methods=['GET', 'POST']) # step 1 form
@login_required
def select_ship():
    # Prevent admins and owners from purchasing
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to purchase in order to avoid conflicts.\n\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('productPagination.product_detail', product_id=1, not_customer=True))
    
    form = SelectDeliveryTypeForm()
    show = None
    if 'delivery_type' in session:
        show = session['delivery_type']['type']

    if request.method == 'GET':
        if show:
            form.del_type.data = show
            show = form.del_type.data

    else:
        if form.validate_on_submit():
            session['delivery_type'] = {
                'type': form.del_type.data
            }
            return redirect(url_for('payment.billing_info'))
        else:
            for err in form.errors:
                print(err)

    return render_template('views/payment/select_ship.html', form=form, show=show)

@payment.route('/checkout/billing_info', methods=['GET', 'POST']) # step 2 form
@login_required
def billing_info():
    form = BillingAddressForm()
    if session['delivery_type']['type']:
        show = session['delivery_type']['type']
    if show == '1':
        form = PickupForm()

    if request.method == 'GET':
        if 'billing_info' in session and show != '1':
            if show == '4':
                form.countryInt.data = session['billing_info']['country']
            else:
                form.country.data = session['billing_info']['country']
            form.address_one.data = session['billing_info']['line1']
            form.address_two.data = session['billing_info']['line2']
            form.unit_number.data = session['billing_info']['unit_number']
            form.postal_code.data = session['billing_info']['postal_code']
            form.phone_number.data = session['billing_info']['phone_number']
        if show == '1' and session.get('pickup_date', {}).get('date'):
            form.pickup_date.data = datetime.strptime(session['pickup_date']['date'], '%a, %d %b %Y %H:%M:%S %Z')

    else:
        if form.validate_on_submit():
            if show != '1':
                if show == '4':
                    co = form.countryInt.data
                else:
                    co = form.country.data
                session['billing_info'] = {
                    'country': co,
                    'line1': form.address_one.data,
                    'line2': form.address_two.data,
                    'unit_number': form.unit_number.data,
                    'postal_code': form.postal_code.data,
                    'phone_number': form.phone_number.data,
                }
            elif show == '1':
                session['pickup_date'] = {
                    'date': form.pickup_date.data
                }
            return redirect(url_for('payment.select_voucher'))
        else:
            for err in form.errors:
                print(err)

    return render_template('/views/payment/billing_info.html', form=form, show=show)

@payment.route('/checkout/select_voucher', methods=['GET', 'POST']) # step 3 form
@login_required
def select_voucher():
    form = VoucherSelectForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            session['voucher'] = {
                'id': form.voucher.data
            }
            return redirect(url_for('payment.checkout_cart'))
        else:
            for err in form.errors:
                print(err)
    return render_template('/views/payment/select_vouch.html', form=form)

@payment.route('/checkout/cart', methods=['GET'])
@login_required
def checkout_cart():
    # Check if the cart is empty
    cart = current_user.cart_items
    if not cart:
        abort(404)

    # Prepare line items for the checkout session
    items = []
    for item in cart:
        product = Product.query.filter_by(id=item.product_id).first()
        additem = {
            'price_data': {
                'unit_amount': item.product_condition['price'] * 100,
                'currency': 'sgd',
                'product_data': {
                    'name': product.name
                }
            },
            'quantity': item.quantity,
        }
        items.append(additem)

    try:
        # Create or retrieve the Stripe Customer
        if current_user.stripe_id is None:
            customer = stripe.Customer.create(
                name=f"{current_user.first_name} {current_user.last_name}",
                email=current_user.email,
            )
            current_user.stripe_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(current_user.stripe_id)
        
        # total
        total_amount = sum(item['price_data']['unit_amount'] * item['quantity'] for item in items)

        d_type = session.get('delivery_type', {}).get('type')
        shipping_cost = 0
        if d_type == '2' and total_amount / 100 > 30:
            shipping_cost = 4 * 100
            ship_name = 'Standard Local Delivery'
        elif d_type == '3':
            shipping_cost = 10 * 100
            ship_name = 'Expedited Local Delivery'
        elif d_type == '4':
            shipping_cost = 30 * 100
            ship_name = 'International Delivery'
        
        final_total = total_amount + shipping_cost
        
        # voucher
        v_id = session.get('voucher', {}).get('id')
        voucher = Voucher.query.get(v_id) if v_id else None

        if voucher:
            if voucher.voucherType_id == 1:
                items = [] # reset because no way to apply vouchers without manually adding them in stripe
                discount = int(final_total * (voucher.discount_value / 100))
                final_total -= discount
                items.append({
                    'price_data': {
                        'unit_amount': final_total,
                        'currency': 'sgd',
                        'product_data': {
                            'name': 'Discounted Products with code ' + voucher.voucher_code
                        }
                    },
                    'quantity': 1,
                })
            elif voucher.voucherType_id == 2:
                items = [] # reset because no way to apply vouchers without manually adding them in stripe
                discount = int(voucher.discount_value * 100)
                final_total -= discount
                items.append({
                    'price_data': {
                        'unit_amount': final_total,
                        'currency': 'sgd',
                        'product_data': {
                            'name': 'Discounted Products with code ' + voucher.voucher_code
                        }
                    },
                    'quantity': 1,
                })
            elif voucher.voucherType_id == 3:
                # Free shipping
                final_total -= shipping_cost
                shipping_cost = 0

        # Create the Checkout Session
        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('payment.checkout_cancel', _external=True),
            customer=current_user.stripe_id,
            payment_intent_data={
                'setup_future_usage': 'on_session',
                'metadata': {
                    'voucher_id': voucher.id if voucher else None,
                    'voucher_code': voucher.voucher_code if voucher else None,
                },
            },
            payment_method_data={
                'allow_redisplay': 'always',
            },
            shipping_options=[{
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': shipping_cost,
                        'currency': 'sgd',
                    },
                    'display_name': ship_name,
                },
            }] if shipping_cost > 0 else None,
        )

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@payment.route('/success')
@login_required
@role_required(1)
def success():
    try:
        # print(session.get('billing_info', None), session.get('delivery_type', None), session.get('pickup_date', None))
        # retrieve previous checkout session
        checkout_sessions = stripe.checkout.Session.list(customer=current_user.stripe_id, limit=1)
        if not checkout_sessions.data:
            print("No checkout session found.")
            return redirect(url_for('productPagination.product_pagination'))

        checkout_session = checkout_sessions.data[0]

        # Retrieve the latest charge associated with the PaymentIntent
        # charge = stripe.Charge.retrieve(payment_intent.latest_charge)
        
        # Make sure not creating a new entry
        dt_challenge = session.get('delivery_type', None)
        filled_bd = session.get('billing_info', None)
        bd_challenge = BillingAddress.query.filter_by(user_id= current_user.id).first()
        # print(dt_challenge)
        if dt_challenge['type'] in ['2', '3', '4']:
            if not bd_challenge or bd_challenge.address_one != filled_bd['line1']:
                # Save the billing address to the BillingAddress table
                billing_address = BillingAddress(
                    user_id=current_user.id,
                    address_one=filled_bd['line1'],
                    address_two=filled_bd['line2'] or '',  # Optional
                    unit_number=filled_bd['unit_number'],
                    postal_code=filled_bd['postal_code'],
                    phone_number=filled_bd['phone_number'] or 'Not Provided',
                )
                db.session.add(billing_address)
                db.session.commit()
            else:
                billing_address = bd_challenge
        else:
            filled_pd = session.get('pickup_date', None)
            pickup = Pickup(
                user_id=current_user.id,
                pickup_date=datetime.strptime(filled_pd['date'], '%a, %d %b %Y %H:%M:%S %Z')
            )
            db.session.add(pickup)
            db.session.commit()

        # won't save payment info in site since currently being saved in stripe. 
        # i can't find a way to retrieve saved payment info from rewwwind to autofill stripe checkout, so there's that.
        # Retrieve the payment method details
        # payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
        # p_challenge = PaymentInformation.query.filter_by(user_id= current_user.id).first()
        # if not p_challenge or p_challenge.card_number != payment_method.card.last4:
        #     # Save the payment information
        #     print(payment_method.type)
        #     if payment_method.type == 'Visa':
        #         paymentType_id = 1
        #     elif payment_method.type == 'Mastercard':
        #         paymentType_id = 2
        #     payment_information = PaymentInformation(
        #         user_id=current_user.id,
        #         paymentType_id=paymentType_id,
        #         card_number=payment_method.card.last4,  # Not important since details are retrieved from stripe anyways
        #         card_name=payment_method.billing_details.name,
        #         expiry_date=f"{payment_method.card.exp_month:02d}/{payment_method.card.exp_year % 100:02d}", 
        #     )
        #     db.session.add(payment_information)
        #     db.session.commit()
        # else:
        #     payment_information = p_challenge

        # Retrieve the PaymentIntent
        payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)

        # query voucher id
        v_id = session.get('voucher', {}).get('id')

        # Create the Order
        payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
        if payment_method.card.brand == 'visa':
            methodId = 1
        elif payment_method.card.brand == 'mastercard':
            methodId = 2
        else:
            methodId = 3
        if dt_challenge['type'] != '1':
            d_type = ['standard', 'expedited', 'international'][int(dt_challenge['type'])-2]
            order = Order(
                user_id=current_user.id,
                delivery=d_type, 
                payment_type_id=methodId,
                billing_id=billing_address.id,
                voucher_id=v_id if v_id != 0 else None
            )
        else:
            order = Order(
                user_id=current_user.id,
                delivery='self-pickup',
                payment_type_id=methodId,
                pickup_id=pickup.id,
                voucher_id=v_id if v_id != 0 else None
            )
        db.session.add(order)
        db.session.commit()

        # Add items from the cart to the OrderItem table
        if current_user.cart_items:
            for item in current_user.cart_items:
                orderitem = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    product_condition=item.product_condition,
                    quantity=item.quantity,
                    unit_price=item.product_condition['price']
                )
                db.session.add(orderitem)
                db.session.commit()

                # Update the order total
                order.update_total()
                db.session.commit()

                # Remove the item from the cart
                db.session.delete(item)
                db.session.commit()
        
        # set vouchers to used, if any.
        voucher = UserVoucher.query.filter(
            UserVoucher.user_id == current_user.id,
            UserVoucher.voucher_id == v_id
        ).first()
        if voucher:
            voucher.is_used = True
            db.session.commit()

        session.pop('delivery_type', None)
        session.pop('billing_info', None)
        session.pop('pickup_date', None)
        session.pop('voucher', None)

        print("Order placed successfully!")
        flash("Order placed successfully!\nThank you for shopping with us!", "success")
        return redirect(url_for('manageOrders.order_detail', order_id=order.id))

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return redirect(url_for('productPagination.product_pagination'))

@payment.route('/checkout/cancel', methods=['GET'])
@login_required
def checkout_cancel():
    # Retrieve the temp_cart for the current user
    temp_cart = Cart.query.filter_by(user_id=current_user.id).first()
    if temp_cart:
        db.session.delete(temp_cart)
        db.session.commit()
        flash("Your cart has been cleared.", "info")

    session.pop('delivery_type', None)
    session.pop('billing_info', None)
    session.pop('pickup_date', None)

    return redirect(url_for('productPagination.product_pagination'))