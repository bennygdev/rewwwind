from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, current_app, session
import requests
from flask_login import login_required, current_user
from .__init__ import csrf
from sqlalchemy import cast, Float, Integer
from sqlalchemy.orm.attributes import flag_modified
from .roleDecorator import role_required
from .models import Product, Order, OrderItem, Cart, PaymentInformation, BillingAddress
from .forms import AddReviewForm, AddToCartForm, DeleteReviewForm
from . import db
from math import ceil

import stripe

payment = Blueprint('payment', __name__)

@payment.route('/checkout/product/<int:product_id>', methods=['POST'])
@login_required
def checkout_product(product_id):
    # Prevent admins and owners from purchasing
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to purchase in order to avoid conflicts.\n\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('productPagination.product_detail', product_id=product_id, not_customer=True))

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

        # Update with billing address and phone number if available
        if hasattr(current_user, 'billing_address') and hasattr(current_user, 'phone'):
            stripe.Customer.modify(
                current_user.stripe_id,
                address={
                    'line1': current_user.billing_address.get('line1', ''),
                    'city': current_user.billing_address.get('city', ''),
                    'state': current_user.billing_address.get('state', ''),
                    'postal_code': current_user.billing_address.get('postal_code', ''),
                    'country': current_user.billing_address.get('country', ''),
                },
                phone=current_user.phone
            )

        # Create the Checkout Session
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'unit_amount': condition[0]['price'] * 100,
                        'currency': 'sgd',
                        'product_data': {
                            'name': product.name
                        }
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('productPagination.product_pagination', _external=True),
            adaptive_pricing={'enabled': True},
            customer=current_user.stripe_id,
            payment_intent_data={
                'setup_future_usage': 'on_session'
            },
            payment_method_data={
                'allow_redisplay': 'always'
            },
            billing_address_collection='required',
            phone_number_collection={'enabled': True}
        )

        # Add the product to the cart temporarily (if needed)
        temp_cart = Cart(
            user_id=current_user.id,
            product_id=product_id,
            product_condition=condition[0],
            quantity=1
        )
        db.session.add(temp_cart)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(str(e))
        return str(e)

    return redirect(checkout_session.url, code=303)

@payment.route('/checkout/cart', methods=['POST'])
@login_required
def checkout_cart():
    # Prevent admins and owners from purchasing
    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to purchase in order to avoid conflicts.\n\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('productPagination.product_detail', product_id=1, not_customer=True))

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

        # Update with billing address and phone number if available
        if hasattr(current_user, 'billing_address') and hasattr(current_user, 'phone'):
            stripe.Customer.modify(
                current_user.stripe_id,
                address={
                    'line1': current_user.billing_address.get('line1', ''),
                    'city': current_user.billing_address.get('city', ''),
                    'state': current_user.billing_address.get('state', ''),
                    'postal_code': current_user.billing_address.get('postal_code', ''),
                    'country': current_user.billing_address.get('country', ''),
                },
                phone=current_user.phone
            )

        # Create the Checkout Session
        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('productPagination.product_pagination', _external=True),
            adaptive_pricing={'enabled': True},
            customer=current_user.stripe_id,
            payment_intent_data={
                'setup_future_usage': 'on_session'
            },
            payment_method_data={
                'allow_redisplay': 'always'
            },
            billing_address_collection='required',
            phone_number_collection={'enabled': True}
        )

        # Function to handle successful payment
        def handle_successful_payment(session_id):
            # Retrieve the Checkout Session
            checkout_session = stripe.checkout.Session.retrieve(session_id)

            # Retrieve the PaymentIntent
            payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)

            # Attach the payment method to the customer
            if payment_intent.payment_method:
                stripe.PaymentMethod.attach(
                    payment_intent.payment_method,
                    customer=current_user.stripe_id
                )
                print("Payment method attached to customer.")

            # Update the customer with billing address and phone number
            billing_details = payment_intent.charges.data[0].billing_details
            if billing_details:
                stripe.Customer.modify(
                    current_user.stripe_id,
                    address={
                        'line1': billing_details.address.line1,
                        'city': billing_details.address.city,
                        'state': billing_details.address.state,
                        'postal_code': billing_details.address.postal_code,
                        'country': billing_details.address.country,
                    },
                    phone=billing_details.phone
                )
                print("Billing address and phone number updated for customer.")

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@payment.route('/success')
@login_required
@role_required(1)
def success():
    try:
        # retrieve previous checkout session
        checkout_sessions = stripe.checkout.Session.list(customer=current_user.stripe_id, limit=1)
        if not checkout_sessions.data:
            flash("No checkout session found.", "error")
            return redirect(url_for('productPagination.product_pagination'))

        checkout_session = checkout_sessions.data[0]

        # Retrieve the PaymentIntent
        payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)

        # Retrieve the latest charge associated with the PaymentIntent
        charge = stripe.Charge.retrieve(payment_intent.latest_charge)

        # Retrieve billing details from the Charge
        billing_details = charge.billing_details
        
        # Make sure not creating a new entry
        bd_challenge = BillingAddress.query.filter_by(user_id= current_user.id).first()
        if not bd_challenge or bd_challenge.address_one != billing_details.address.line1:
            # Save the billing address to the BillingAddress table
            billing_address = BillingAddress(
                user_id=current_user.id,
                address_one=billing_details.address.line1,
                address_two=billing_details.address.line2 or '',  # Optional
                unit_number='',
                postal_code=billing_details.address.postal_code,
                phone_number=billing_details.phone or 'Not Provided',
            )
            db.session.add(billing_address)
            db.session.commit()
        else:
            billing_address = bd_challenge

        # Retrieve the payment method details
        payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
        p_challenge = PaymentInformation.query.filter_by(user_id= current_user.id).first()
        if not p_challenge or p_challenge.card_number != payment_method.card.last4:
            # Save the payment information
            payment_information = PaymentInformation(
                user_id=current_user.id,
                paymentType_id=1, # Will just hard code for now.
                card_number=payment_method.card.last4,  # Not important since details are retrieved from stripe anyways
                card_name=payment_method.billing_details.name,
                expiry_date=f"{payment_method.card.exp_month:02d}/{payment_method.card.exp_year % 100:02d}", 
                card_cvv='***',  # Can't store.
            )
            db.session.add(payment_information)
            db.session.commit()
        else:
            payment_information = p_challenge

        # Create the Order
        order = Order(
            user_id=current_user.id,
            delivery='Standard',
            payment_type_id=1,  # Will just hard code for now
            payment_information_id=payment_information.id,
            billing_id=billing_address.id
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

        flash("Order placed successfully!", "success")
        return redirect(url_for('manageOrders.order_detail', order_id=order.id))

    except Exception as e:
        db.session.rollback()
        print(str(e))
        flash("An error occurred while processing your order. Please try again.", "error")
        return redirect(url_for('productPagination.product_pagination'))