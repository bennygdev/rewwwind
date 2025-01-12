from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Product
from datetime import timedelta
from sqlalchemy import func

views = Blueprint('views', __name__)

@views.route('/')
def home():

  special_products = Product.query.filter_by(is_featured_special=True).all() # special (featured) products
  home_special_products = special_products[:6] # max special to display in home
  
  max_days = func.now() - timedelta(days=7)
  new_products = Product.query.filter(Product.created_at >= max_days).all() # product should be less than 7 days old to be new
  home_new_products = new_products[:18]

  staff_products = Product.query.filter_by(is_featured_staff=True).all() # staff (featured) products
  home_staff_products = staff_products[:3]

  # staff_picks = Product.query.filter_by(is_featured_staff=True)

  return render_template("views/home.html", user=current_user, special_products=special_products, max_special = home_special_products, max_new = home_new_products, max_staff = home_staff_products)