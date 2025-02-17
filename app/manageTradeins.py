from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import tradeDetail  
from datetime import timedelta
from . import db
from .forms import ShippingPaymentForm

manageTradeins = Blueprint('manageTradeins', __name__)


@manageTradeins.route('/manage-tradeins', methods=['GET'])
@login_required
@role_required(1, 2, 3)  # Allows Customers (1), Admins (2), and Owners (3)
def manage_tradeins():
    # Check if user is an admin or owner
    if current_user.role_id in [2, 3]: 
        trade_items = tradeDetail.query.all()  # Gets all trade requests
        print(f"Admin View - All Trade Requests: {trade_items}")
    else:
        trade_items = tradeDetail.query.filter_by(trade_number=current_user.id).all()  # Gets only the user's requests
        print(f"User View - Trade items for {current_user.id}: {trade_items}")

    return render_template(
        "dashboard/manageTradeins/tradeins.html",
        user=current_user,
        trade_items=trade_items
    )

@manageTradeins.route('/delete-trade/<int:trade_id>', methods=['GET'])
@login_required
@role_required(1, 2, 3)  
def delete_trade(trade_id):
    trade_item = tradeDetail.query.get_or_404(trade_id)

    # Only owner (user of whoever made it) can delete sent requests
    if current_user.role_id == 1 and trade_item.trade_number != current_user.id:
        flash("You do not have permission to delete this trade-in.", "danger")
        return redirect(url_for('manageTradeins.manage_tradeins'))

    db.session.delete(trade_item)
    db.session.commit()
    
    flash("Trade-in deleted successfully!", "delete")

    return redirect(url_for('manageTradeins.manage_tradeins'))

from datetime import timedelta

@manageTradeins.route('/view-trade/<int:trade_id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def view_trade_details(trade_id):
    trade_item = tradeDetail.query.get_or_404(trade_id)
    form = ShippingPaymentForm()

    return render_template(
        "dashboard/manageTradeins/customer_tradeDetails.html",
        trade_item=trade_item,
        form=form,
        timedelta=timedelta
    )

@manageTradeins.route('/edit-trade/<int:trade_id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)  
def edit_trade(trade_id):
    trade_item = tradeDetail.query.get_or_404(trade_id)

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

@manageTradeins.route('/admin/manage-tradeins', methods=['GET'])
@login_required
@role_required(2, 3)  # Admin/Owner roles
def view_all_requests():
    trade_requests = tradeDetail.query.all()  # Get all trade requests

    print(f"Admin View - All Trade Requests: {trade_requests}")

    return render_template(
        "dashboard/manageTradeins/admin_tradeins.html",
        trade_requests=trade_requests
    )

@manageTradeins.route('/trade/<int:trade_id>/update-status', methods=['GET'])
@login_required
@role_required(2, 3)
def update_trade_status(trade_id):
    trade = tradeDetail.query.get_or_404(trade_id)
    
    new_status = request.args.get("status")
    
    if new_status in ["Approved", "Rejected"]:
        trade.status = new_status
        db.session.commit()
        flash(f"Trade-in Request #{trade.id} has been {new_status.lower()}.", "success")
    
    return redirect(url_for('manageTradeins.manage_tradeins'))

@manageTradeins.route('/trade/<int:trade_id>/save-shipping-payment', methods=['POST'])
@login_required
def save_shipping_payment(trade_id):
    trade = tradeDetail.query.get_or_404(trade_id)

    if trade.status != "Approved":
        flash("Only approved trade-ins can proceed with shipping and payment.", "warning")
        return redirect(url_for('manageTradeins.view_trade_details', trade_id=trade.id))

    form = ShippingPaymentForm(request.form)

    if form.validate_on_submit():
        # Store shipping option
        trade.shipping_option = form.shipping_option.data

        # Store only relevant details
        if trade.shipping_option == "Mail-in":
            trade.tracking_number = form.tracking_number.data
            trade.street_address = trade.house_block = trade.zip_code = trade.contact_number = None  # Reset fields

        elif trade.shipping_option == "Pick-Up Service":
            trade.street_address = form.street_address.data
            trade.house_block = form.house_block.data
            trade.zip_code = form.zip_code.data
            trade.contact_number = form.contact_number.data
            trade.tracking_number = None  # Reset tracking number

        else:  # In-Store Drop-off (No extra fields needed)
            trade.tracking_number = None
            trade.street_address = trade.house_block = trade.zip_code = trade.contact_number = None

        # Store payment details
        trade.card_number = form.card_number.data[-4:]  # Store only last 4 digits for security
        trade.card_expiry = form.card_expiry.data
        trade.card_name = form.card_name.data

        db.session.commit()

        flash("Shipping and payment details saved successfully!", "success")
        return redirect(url_for('manageTradeins.view_trade_details', trade_id=trade.id))

    flash("There were errors in your submission. Please check and try again.", "danger")
    return redirect(url_for('manageTradeins.view_trade_details', trade_id=trade.id))
