from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, current_app, session
import requests
from flask_login import login_required, current_user
from .__init__ import csrf
from sqlalchemy import cast, Float, Integer
from sqlalchemy.orm.attributes import flag_modified
from .roleDecorator import role_required
from .models import Product, Order, OrderItem, Cart
from .forms import AddReviewForm, AddToCartForm, DeleteReviewForm
from . import db
from math import ceil

import stripe

payment = Blueprint('payment', __name__)

@payment.route('/checkout/product/<int:product_id>', methods=['POST'])
@login_required
@role_required(1)
def checkout_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        abort(404)
    
    getcondition = request.form.get('condition')
    if getcondition not in ['Brand New', 'Like New', 'Lightly Used', 'Well Used']:
        abort(404)
    
    condition = [con for con in product.conditions if con.get('condition') == getcondition]
    

    try:
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
                },
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
        )
        if current_user.stripe_id is None:
            customer = stripe.Customer.create(
                name=f"{current_user.first_name} {current_user.last_name}",
                email=current_user.email,
            )

            current_user.stripe_id = customer.id
            db.session.commit()

        temp_cart = Cart(
            user_id=current_user.id, 
            product_id=product_id, 
            product_condition=condition[0], 
            quantity=1)
        db.session.add(temp_cart)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(str(e))

    return redirect(checkout_session.url, code=303)

@payment.route('/checkout/cart', methods=['POST'])
@login_required
@role_required(1)
def checkout_cart():
    cart = current_user.cart_items
    if not cart:
        abort(404)
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
        )
        if current_user.stripe_id is None:
            customer = stripe.Customer.create(
                name=f"{current_user.first_name} {current_user.last_name}",
                email=current_user.email,
            )

            current_user.stripe_id = customer.id
            db.session.commit()
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@payment.route('/success')
@login_required
@role_required(1)
def success():
    try:
        order = Order(
            user_id=current_user.id,
            delivery='Standard',
            payment_type_id=1,
            payment_information_id=1,
            billing_id=1
        )
        db.session.add(order)
        db.session.commit()

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

                order.update_total()
                db.session.commit()
                
                db.session.delete(item)
                db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(str(e))

    return render_template('views/payment_success.html')