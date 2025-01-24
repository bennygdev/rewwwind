from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db
from .models import Voucher, VoucherType
from .forms import VoucherForm
from math import ceil
import json

manageVouchers = Blueprint('manageVouchers', __name__)

@manageVouchers.route('/manage-vouchers')
@login_required
@role_required(2, 3)
def vouchers_listing():
  vouchers = Voucher.query.order_by(Voucher.created_at.desc()).all()

  # pagination
  page = request.args.get('page', 1, type=int)
  per_page = 10

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
    vouchers_query = Voucher.query.filter(Voucher.voucher_code.ilike(f"%{search_query}%"))
  else:
    vouchers_query = Voucher.query

  # pagination logic
  total_vouchers = vouchers_query.count()
  vouchers = vouchers_query.order_by(Voucher.id).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_vouchers / per_page)

  return render_template("dashboard/manageVouchers/vouchers.html", user=current_user, vouchers=vouchers, total_pages=total_pages, current_page=page, search_query=search_query)

@manageVouchers.route('/manage-vouchers/add', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_voucher():
  form = VoucherForm()
    
  if form.validate_on_submit():
    print(form.criteria_json.data)
    criteria = json.loads(form.criteria_json.data) if form.criteria_json.data else []
    print(criteria)
        
    voucher = Voucher(
      voucher_code=form.code.data,
      voucher_description=form.description.data,
      voucherType_id=VoucherType.query.filter_by(voucher_type=form.voucher_type.data).first().id,
      discount_value=form.discount_value.data,
      criteria=criteria,
      eligible_categories=form.eligible_categories.data,
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