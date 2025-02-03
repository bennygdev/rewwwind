from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, make_response
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Order
from .forms import UpdateOrderForm
from . import db
from sqlalchemy import desc, asc, cast, Float
from datetime import datetime, timedelta
from fpdf import FPDF
from math import ceil

manageOrders = Blueprint('manageOrders', __name__)
# Orders page

@manageOrders.route('/manage-orders')
@login_required
@role_required(1, 2, 3)
def orders_listing():
  if current_user.role_id == 1:
    orders_query = Order.query.filter_by(user_id=current_user.id)
  else:
    orders_query = Order.query

  # search logic
  search_query = request.args.get('q', '', type=str)
  if search_query:
    orders_query = orders_query.filter(Order.id.ilike(f"%{search_query}%"))
  
  # filter logic
  recency_filter = request.args.get('recency', '', type=str)
  if recency_filter and recency_filter != 'all':
    if '30' in recency_filter:
      orders_query = Order.query.filter(Order.order_date >= datetime.now() - timedelta(days=30))
    elif 'first' in recency_filter:
      orders_query = orders_query.order_by(desc(Order.order_date))
    else:
      orders_query = orders_query.order_by(asc(Order.order_date))
  
  cost_filter = request.args.get('cost', '', type=str)
  if cost_filter and cost_filter != 'none':
    if 'highest' in cost_filter:
      orders_query = Order.query.order_by(cast(Order.total_amount, Float).desc())
    else:
      orders_query = Order.query.order_by(cast(Order.total_amount, Float).asc())

  # pagination logic
  page = request.args.get('page', 1, type=int)
  per_page = 10

  orders = orders_query.order_by(Order.id).paginate(page=page, per_page=per_page)
  total_orders = orders_query.count()

  total_pages = ceil(total_orders / per_page)
    
  return render_template(
    'dashboard/manageOrders/orders.html', 
    current_user=current_user, 
    orders=orders, 
    total_orders=total_orders,
    current_page=page,
    total_pages=total_pages,
    search_query=search_query,
    recency_filter=recency_filter,
    cost_filter=cost_filter
    )

@manageOrders.route('/manage-order/order-detail=<int:order_id>')
@login_required
@role_required(1,2,3)
def order_detail(order_id):
  order = Order.query.get_or_404(order_id)
  order_items = order.order_items
  
  form = UpdateOrderForm()
  if order.status != 'Pending':
    form.approved.data = order.status
  else:
    form.approved.data = 'Not Approved'

  if not order:
    abort(404)
  return render_template('dashboard/manageOrders/orderDetail.html', user=current_user, order=order, order_items=order_items, form=form, timedelta=timedelta)

@manageOrders.route('/manage-order/order-detail=<int:order_id>/update-order', methods=["POST"])
@login_required
@role_required(1,2,3)
def update_order(order_id):
  order = Order.query.get_or_404(order_id)
  form = UpdateOrderForm()

  if form.validate_on_submit():
    if form.approved.data.title() in ['Approved', 'Not Approved']:
      if form.approved.data.title() == 'Not Approved':
        order.status = 'Pending'
      else:
        order.status = form.approved.data.title()
    
    db.session.commit()

    order.update_approval()
    print(order.approval_date)
    db.session.commit()
    
    flash("Order was updated successfully!", "success")

  return redirect(url_for('manageOrders.orders_listing'))

@manageOrders.route('/manage-order/order-detail=<int:order_id>/invoice')
@login_required
@role_required(1,2,3)
def generate_invoice(order_id):
  order = Order.query.get_or_404(order_id)

  if not order.approval_date:
    abort(404)
  
  # timestamp
  timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

  # Initialise PDF
  pdf = FPDF()
  pdf.set_title(f"rewwwind___invoice_{order_id}_{timestamp}")
  pdf.add_page()
  pdf.set_font('Arial', 'B', 16)

  # Header
  pdf.cell(200, 10, txt="Invoice", ln=True, align='C')
  pdf.set_font('Arial', '', 12)
  pdf.cell(200, 10, txt=f"Order ID: {order.id}", ln=True, align='C')
  pdf.cell(200, 10, txt=f"Order Date: {order.approval_date.strftime('%d %B %Y')}", ln=True, align='C')
  pdf.ln(10)

  # Billing Information
  pdf.set_font('Arial', 'B', 14)
  pdf.cell(0, 10, "Billing Information:", ln=True)
  pdf.set_font('Arial', '', 12)
  pdf.cell(0, 10, f"Name: {order.user.first_name} {order.user.last_name}", ln=True)
  pdf.cell(0, 10, f"Address: {order.billing.address_one}", ln=True)
  pdf.cell(0, 10, f"Phone: {order.billing.phone_number}", ln=True)
  pdf.ln(10)

  # Order Summary
  pdf.set_font('Arial', 'B', 14)
  pdf.cell(0, 10, "Order Summary:", ln=True)
  pdf.set_font('Arial', 'B', 12)
  pdf.cell(80, 10, "Item", 1)
  pdf.cell(40, 10, "Quantity", 1)
  pdf.cell(40, 10, "Price ($)", 1)
  pdf.ln()

  pdf.set_font('Arial', '', 12)
  for item in order.order_items:
    product_name = item.product.name
    quantity = item.quantity
    price = item.product_condition['price'] * item.quantity
    pdf.cell(80, 10, product_name, 1)
    pdf.cell(40, 10, str(quantity), 1)
    pdf.cell(40, 10, f"{price:.2f}", 1)
    pdf.ln()
  
  pdf.ln(10)

  # Subtotal
  pdf.set_font('Arial', 'B', 12)  # bold
  pdf.cell(30, 10, "Subtotal:", 0, 0)  # label
  pdf.set_font('Arial', '', 12)  # remove bold
  pdf.cell(0, 10, f"$ {order.total_amount:.2f}", ln=True)  # value

  # shipping price
  pdf.set_font('Arial', 'B', 12) 
  pdf.cell(30, 10, "Shipping:", 0, 0) 
  pdf.set_font('Arial', '', 12) 
  pdf.cell(0, 10, "$ 30.00", ln=True) 

  # total
  pdf.set_font('Arial', 'B', 12) 
  pdf.cell(30, 10, "Total:", 0, 0)
  pdf.set_font('Arial', '', 12)
  pdf.cell(0, 10, f"$ {order.total_amount + 30:.2f}", ln=True)

  # Output
  response = make_response(pdf.output(dest='S').encode('latin1'))
  response.headers['Content-Type'] = 'application/pdf'
  response.headers['Content-Disposition'] = f'inline; filename=rewwwind___invoice_{order_id}_{timestamp}.pdf'
  return response