from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db
from .models import Voucher, VoucherType
from .forms import VoucherForm, EditVoucherForm
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
  per_page = 12

  # filters
  expiry_filter = request.args.get('expiry', '')
  type_filter = request.args.get('type', '')
  status_filter = request.args.get('status', '')

  # Start with base query
  vouchers_query = Voucher.query

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
    vouchers_query = Voucher.query.filter(Voucher.voucher_code.ilike(f"%{search_query}%"))
  else:
    vouchers_query = Voucher.query

  if expiry_filter:
    vouchers_query = vouchers_query.filter(Voucher.expiry_days == int(expiry_filter))

  if type_filter:
    type_id_map = {
      'percentage': 1,
      'fixed_amount': 2,
      'free_shipping': 3
    }
    if type_filter.lower() in type_id_map:
      vouchers_query = vouchers_query.filter(Voucher.voucherType_id == type_id_map[type_filter.lower()])

  if status_filter:
    is_active = status_filter.lower() == 'active'
    vouchers_query = vouchers_query.filter(Voucher.is_active == is_active)

  # pagination logic
  total_vouchers = vouchers_query.count()
  vouchers = vouchers_query.order_by(Voucher.created_at.desc()).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_vouchers / per_page)

  # Filter choices
  expiry_choices = [
    ('7', '7 Days'),
    ('14', '14 Days'),
    ('30', '30 Days'),
    ('60', '60 Days'),
    ('90', '90 Days')
  ]

  type_choices = [
    ('percentage', 'Percentage'),
    ('fixed_amount', 'Fixed Amount'),
    ('free_shipping', 'Free Shipping')
  ]

  status_choices = [
    ('active', 'Active'),
    ('inactive', 'Inactive')
  ]

  return render_template(
    "dashboard/manageVouchers/vouchers.html", 
    user=current_user, 
    vouchers=vouchers, 
    total_pages=total_pages, 
    current_page=page, 
    search_query=search_query,
    expiry_filter=expiry_filter,
    type_filter=type_filter,
    status_filter=status_filter,
    expiry_choices=expiry_choices,
    type_choices=type_choices,
    status_choices=status_choices
  )

@manageVouchers.route('/manage-vouchers/add', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_voucher():
  form = VoucherForm()
    
  if form.validate_on_submit():
    try:
      print(form.criteria_json.data)
      criteria = json.loads(form.criteria_json.data) if form.criteria_json.data else []
      print(criteria)
          
      voucher = Voucher(
        voucher_code=form.code.data,
        voucher_description=form.description.data,
        voucherType_id=VoucherType.query.filter_by(voucher_type=form.voucher_type.data).first().id,
        discount_value=form.discount_value.data,
        criteria=criteria,
        eligible_categories=list(form.eligible_categories.data),
        expiry_days=form.expiry_days.data,
        is_active=form.is_active.data == 'True'
      )
          
      db.session.add(voucher)
      db.session.commit()
      flash('Voucher created successfully!', 'success')
      return redirect(url_for('manageVouchers.vouchers_listing'))
    except Exception as e: # debug
      print(e)
      db.session.rollback()
      flash('An error occurred while creating the voucher.', 'error')
            
  return render_template("dashboard/manageVouchers/add_voucher.html", user=current_user, form=form)

@manageVouchers.route('/manage-vouchers/view/<int:id>')
@login_required
@role_required(2, 3)
def view_voucher(id):
  voucher = Voucher.query.get_or_404(id)

  type_mapping = {
    'fixed_amount': 'Fixed Amount',
    'free_shipping': 'Free Shipping',
    'percentage': 'Percentage'
  }

  voucher_type = voucher.voucher_types.voucher_type
  formatted_type = type_mapping.get(voucher_type, voucher_type)

  return jsonify({
    'id': voucher.id,
    'code': voucher.voucher_code,
    'description': voucher.voucher_description,
    'type': formatted_type,
    'discount_value': str(voucher.discount_value),
    'criteria': voucher.criteria,
    'eligible_categories': voucher.eligible_categories,
    'expiry_days': voucher.expiry_days,
    'is_active': voucher.is_active,
    'created_at': voucher.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    'updated_at': voucher.updated_at.strftime('%Y-%m-%d %H:%M:%S')
  })

@manageVouchers.route('/manage-vouchers/edit-voucher/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def edit_voucher(id):
  voucher = Voucher.query.get_or_404(id)
  form = EditVoucherForm(voucher_id=id, obj=voucher)
    
  if form.validate_on_submit():
    try:
      # Update voucher details
      voucher.voucher_code = form.code.data
      voucher.voucher_description = form.description.data
      voucher.voucherType_id = VoucherType.query.filter_by(voucher_type=form.voucher_type.data).first().id
      voucher.discount_value = form.discount_value.data
      voucher.is_active = form.is_active.data == 'True'
          
      # Parse and save criteria
      criteria = json.loads(form.criteria_json.data) if form.criteria_json.data else []
      voucher.criteria = criteria
          
      voucher.eligible_categories = list(form.eligible_categories.data)
      voucher.expiry_days = form.expiry_days.data
        
      db.session.commit()
      flash('Voucher updated successfully!', 'success')
      return redirect(url_for('manageVouchers.vouchers_listing'))
    except Exception as e:
      db.session.rollback()
      print(e)
      flash('An error occurred while updating the voucher.', 'error')
  elif request.method == 'GET':
    form.code.data = voucher.voucher_code
    form.description.data = voucher.voucher_description
    form.voucher_type.data = voucher.voucher_types.voucher_type
    form.is_active.data = str(voucher.is_active)
    if voucher.eligible_categories:
      print("yes")
      form.eligible_categories.data = voucher.eligible_categories

    
  return render_template("dashboard/manageVouchers/edit_voucher.html", user=current_user, form=form, voucher=voucher)

@manageVouchers.route('/manage-vouchers/delete-voucher/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def delete_voucher(id):
  selectedVoucher = Voucher.query.get_or_404(id)

  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  if selectedVoucher:
    db.session.delete(selectedVoucher)
    db.session.commit()
    flash("Voucher deleted.", "success")
    return redirect(url_for('manageVouchers.vouchers_listing'))
  else:
    flash("Invalid voucher or unauthorized access.", "error")
    return redirect(url_for('manageVouchers.vouchers_listing'))