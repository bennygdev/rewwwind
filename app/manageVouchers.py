from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db
from .models import Voucher, VoucherType
from .forms import VoucherForm

manageVouchers = Blueprint('manageVouchers', __name__)

@manageVouchers.route('/manage-vouchers')
@login_required
@role_required(2, 3)
def vouchers_listing():
  vouchers = Voucher.query.order_by(Voucher.created_at.desc()).all()

  return render_template("dashboard/manageVouchers/vouchers.html", user=current_user, vouchers=vouchers)

@manageVouchers.route('/manage-vouchers/add', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_voucher():
  form = VoucherForm()
    
  if form.validate_on_submit():
    criteria = {
      'min_cart_amount': form.min_cart_amount.data,
      'min_cart_items': form.min_cart_items.data,
      'first_purchase': form.first_purchase_only.data,
      'eligible_categories': form.eligible_categories.data
    }
        
    voucher = Voucher(
      voucher_code=form.code.data,
      voucher_description=form.description.data,
      voucherType_id=VoucherType.query.filter_by(voucher_type=form.voucher_type.data).first().id,
      discount_value=form.discount_value.data,
      criteria=criteria,
      expiry_days=form.expiry_days.data
    )
        
    db.session.add(voucher)
    try:
      db.session.commit()
      flash('Voucher created successfully!', 'success')
      return redirect(url_for('manageVouchers.vouchers_listing'))
    except Exception as e: # debug
      print(e)
      db.session.rollback()
      flash('An error occurred while creating the voucher.', 'error')
            
  return render_template("dashboard/manageVouchers/add_voucher.html", user=current_user, form=form)

@manageVouchers.route('/manage-vouchers/voucher-details/<int:id>')
@login_required
@role_required(2, 3)
def voucher_details(id):
  selectedVoucher = Voucher.query.get_or_404(id)

  return render_template('dashboard/manageVouchers/voucher_details.html', user=current_user, selectedVoucher=selectedVoucher)