from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import tradeDetail  # Import your model
from . import db

manageTradeins = Blueprint('manageTradeins', __name__)


@manageTradeins.route('/manage-tradeins', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def manage_tradeins():
    
    user_trade_items = tradeDetail.query.filter_by(trade_number=current_user.id).all()

    print(f"Trade items for user {current_user.id}: {user_trade_items}")

    return render_template(
        "dashboard/manageTradeins/tradeins.html",
        user=current_user,
        trade_items=user_trade_items
    )
