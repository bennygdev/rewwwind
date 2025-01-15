from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import tradeDetail  # Import your model
from datetime import timedelta
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

@manageTradeins.route('/delete-trade/<int:trade_id>', methods=['GET'])
@login_required
@role_required(1, 2, 3)  
def delete_trade(trade_id):
    trade_item = tradeDetail.query.get_or_404(trade_id)

    # Only owner (user) can delete sent requests
    if current_user.role_id == 1 and trade_item.trade_number != current_user.id:
        flash("You do not have permission to delete this trade-in.", "danger")

        return redirect(url_for('manageTradeins.manage_tradeins'))

    db.session.delete(trade_item)
    db.session.commit()
    flash("Trade-in deleted successfully!", "success")

    return redirect(url_for('manageTradeins.manage_tradeins'))

from datetime import timedelta

@manageTradeins.route('/view-trade/<int:trade_id>', methods=['GET'])
@login_required
@role_required(1, 2, 3)
def view_trade_details(trade_id):

    trade_item = tradeDetail.query.get_or_404(trade_id)
    
    return render_template(
        "dashboard/manageTradeins/customer_tradeDetails.html",
        trade_item=trade_item,
        timedelta=timedelta  
    )

@manageTradeins.route('/edit-trade/<int:trade_id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)  # Adjust roles as needed
def edit_trade(trade_id):
    trade_item = tradeDetail.query.get_or_404(trade_id)

    # Ensure only the owner can edit their item (if necessary)
    if current_user.role_id == 1 and trade_item.trade_number != current_user.id:
        flash("You do not have permission to edit this trade-in.", "danger")
        return redirect(url_for('manageTradeins.manage_tradeins'))

    if request.method == 'POST':
        # Update the trade item based on form data
        trade_item.title = request.form.get('title')
        trade_item.item_type = request.form.get('item_type')
        trade_item.genre = request.form.get('genre')
        trade_item.author_artist = request.form.get('author_artist')
        trade_item.isbn_or_cat = request.form.get('isbn_or_cat')
        trade_item.item_condition = request.form.get('item_condition')

        db.session.commit()
        flash("Trade-in updated successfully!", "success")
        return redirect(url_for('manageTradeins.view_trade_details', trade_id=trade_id))

    return render_template(
        "dashboard/manageTradeins/customer_tradeDetailsEdit.html",
        trade_item=trade_item
    )
