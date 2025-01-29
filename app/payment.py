from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify, current_app
from flask_login import login_required, current_user
from .__init__ import csrf
from sqlalchemy import cast, Float, Integer
from .roleDecorator import role_required
from .models import Product, Review, Category, SubCategory
from .forms import AddReviewForm, AddToCartForm, DeleteReviewForm
from . import db
from math import ceil

import stripe

payment = Blueprint('payment', __name__)

@payment.route('/create-checkout-session', methods=['POST'])
@login_required
@role_required(1)
@csrf.exempt
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1QmYFF2ek3YdFHUUw0BGUHAW',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('productPagination.product_pagination', _external=True),
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@payment.route('/success')
@login_required
@role_required(1)
def success():
    return render_template('views/payment_success.html')