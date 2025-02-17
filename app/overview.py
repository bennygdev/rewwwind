from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .models import User, Order, tradeDetail, Category, Product, OrderItem
from sqlalchemy import func
from .roleDecorator import role_required
from . import db

overview = Blueprint('overview', __name__)
# Profile page, settings page

@overview.route('/overview')
@login_required
@role_required(1, 2, 3)
def user_overview():
  image_file = url_for('static', filename="profile_pics/" + current_user.image)

  if current_user.image:
    if current_user.image.startswith('http'):
      image_file = current_user.image
    else:
      image_file = url_for('static', filename="profile_pics/" + current_user.image)
  else:
    image_file = url_for('static', filename='profile_pics/profile_image_default.jpg')

  # Header statistics
  customer_label1 = "Total Products Bought"
  customer_label2 = "Total Money Spent"
  customer_label3 = "Total Vouchers Available"
  
  admin_label1 = "Total Customers"
  admin_label2 = "Total Revenue"
  admin_label3 = "Total Orders"

  # do an if statement to check role, to return the variable of the value of either admin or customer
  if current_user.role_id == 1:
    headerLabel1 = customer_label1 
    headerLabel2 = customer_label2
    headerLabel3 = customer_label3
    headerValue1 = Order.query.filter_by(user_id=current_user.id).count() # Total orders by customer
    headerValue2 = db.session.query(func.sum(Order.total_amount)).filter(Order.user_id == current_user.id).scalar() # Total money spent by customer
    headerValue3 = 0 # Total vouchers of customer
    # total_vouchers = current_user.vouchers.count() No vouchers yet

    pending_orders = Order.query.filter_by(user_id=current_user.id, status='Pending').order_by(Order.order_date.desc()).all()
        
    pending_trades = tradeDetail.query.filter_by(trade_number=current_user.id).order_by(tradeDetail.created_at.desc()).all()

  elif current_user.role_id == 2 or current_user.role_id == 3:
    headerLabel1 = admin_label1
    headerLabel2 = admin_label2
    headerLabel3 = admin_label3
    headerValue1 = User.query.count() # Total users
    headerValue2 = db.session.query(func.sum(Order.total_amount)).scalar() # Total revenue
    headerValue3 = Order.query.count() # Total Orders

    # revenue - just sum the cost of all orders total paid
    # but even that we're paying the trade-ins, but that wouldn't be practical since trade-ins are rewarded with store credits instead

    pending_orders = Order.query.filter_by(status='Pending').order_by(Order.order_date.desc()).all()
    pending_trades = tradeDetail.query.order_by(tradeDetail.created_at.desc()).all()

  return render_template(
    "dashboard/overview.html", 
    user=current_user, 
    image_file=image_file, 
    headerLabel1=headerLabel1, 
    headerLabel2=headerLabel2, 
    headerLabel3=headerLabel3,
    headerValue1 = headerValue1,
    headerValue2 = headerValue2,
    headerValue3 = headerValue3,
    pending_orders=pending_orders,
    pending_trades=pending_trades
  )

# Charts
@overview.route('/api/customer/trade-frequency')
@login_required
@role_required(1)
def get_trade_frequency():
  # Get trade-ins grouped by month for the current user
  trades = db.session.query(
    func.strftime('%Y-%m', tradeDetail.created_at).label('month'),
    func.count(tradeDetail.id).label('count')
  ).filter(
    tradeDetail.trade_number == current_user.id
  ).group_by(
    func.strftime('%Y-%m', tradeDetail.created_at)
  ).order_by(
    func.strftime('%Y-%m', tradeDetail.created_at)
  ).all()
  
  # convert month to a more readable format
  formatted_labels = []
  for trade in trades:
    try:
      year_month = trade[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(trade[0])
    
  return {
    'labels': formatted_labels if trades else [],
    'data': [trade[1] for trade in trades] if trades else []
  }

@overview.route('/api/customer/buying-trend')
@login_required
@role_required(1)
def get_buying_trend():
  # Get orders grouped by month for the current user
  orders = db.session.query(
    func.strftime('%Y-%m', Order.order_date).label('month'),
    func.count(Order.id).label('count')
  ).filter(
    Order.user_id == current_user.id
  ).group_by(
    func.strftime('%Y-%m', Order.order_date)
  ).order_by(
    func.strftime('%Y-%m', Order.order_date)
  ).all()
  
  # convert month to a more readable format
  formatted_labels = []
  for order in orders:
    try:
      year_month = order[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(order[0])
    
  return {
    'labels': formatted_labels if orders else [],
    'data': [order[1] for order in orders] if orders else []
  }

@overview.route('/api/admin/category-sales')
@login_required
@role_required(2, 3)
def get_category_sales():
  # Get total sales by category
  sales = db.session.query(
    Category.category_name,
    func.count(OrderItem.id).label('count')
  ).join(
    Product, Product.id == OrderItem.product_id
  ).join(
    Category, Category.id == Product.category_id
  ).group_by(
    Category.category_name
  ).all()
    
  return {
    'labels': [sale[0] for sale in sales] if sales else [],
    'data': [sale[1] for sale in sales] if sales else []
  }

@overview.route('/api/admin/product-sales')
@login_required
@role_required(2, 3)
def get_product_sales():
  # Get approved orders grouped by month
  sales = db.session.query(
    func.strftime('%Y-%m', Order.approval_date).label('month'),
    func.count(Order.id).label('count')
  ).filter(
    Order.status == 'Approved'
  ).group_by(
    func.strftime('%Y-%m', Order.approval_date)
  ).order_by(
    func.strftime('%Y-%m', Order.approval_date)
  ).all()
    
  # convert month to a more readable format
  formatted_labels = []
  for sale in sales:
    try:
      year_month = sale[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(sale[0])
    
  return {
    'labels': formatted_labels if sales else [],
    'data': [sale[1] for sale in sales] if sales else []
  }

# @overview.route('/api/admin/weekly-signups')
# @login_required
# @role_required(2, 3)
# def get_weekly_signups():
#   # Get user registrations grouped by week
#   signup_data = db.session.query(
#     func.strftime('%Y-%W', User.created_at).label('week'),
#     func.count(User.id).label('count')
#   ).group_by(
#     func.strftime('%Y-%W', User.created_at)
#   ).order_by(
#     func.strftime('%Y-%W', User.created_at)
#   ).all()
    
#   return {
#     'labels': [signup[0] for signup in signup_data] if signup_data else [],
#     'data': [signup[1] for signup in signup_data] if signup_data else []
#   }

@overview.route('/api/admin/monthly-signups')
@login_required
@role_required(2, 3)
def get_monthly_signups():
  signup_data = db.session.query(
    func.strftime('%Y-%m', User.created_at).label('month'),
    func.count(User.id).label('count')
  ).group_by(
    func.strftime('%Y-%m', User.created_at)
  ).order_by(
    func.strftime('%Y-%m', User.created_at)
  ).all()
    
  # convert month to a more readable format
  formatted_labels = []
  for signup in signup_data:
    try:
      year_month = signup[0].split('-')
      month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      month_idx = int(year_month[1]) - 1 
      formatted_month = f"{month_names[month_idx]} {year_month[0]}"
      formatted_labels.append(formatted_month)
    except (IndexError, ValueError):
      formatted_labels.append(signup[0])
    
  return {
    'labels': formatted_labels if signup_data else [],
    'data': [signup[1] for signup in signup_data] if signup_data else []
  }

@overview.route('/api/customer/top-categories')
@login_required
@role_required(1)
def get_customer_top_categories():
  # Get customer's purchases by category
  categories = db.session.query(
    Category.category_name,
    func.count(OrderItem.id).label('count')
  ).join(
    OrderItem, OrderItem.product_id == Product.id
  ).join(
    Product, Product.category_id == Category.id
  ).join(
    Order, Order.id == OrderItem.order_id
  ).filter(
    Order.user_id == current_user.id
  ).group_by(
    Category.category_name
  ).order_by(
    func.count(OrderItem.id).desc()
  ).all()
    
  return {
    'labels': [cat[0] for cat in categories] if categories else [],
    'data': [cat[1] for cat in categories] if categories else []
  }