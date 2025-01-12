from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from .models import Product, tradeDetail
from . import db
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

  # staff_picks = Product.query.filter_by(is_featured_staff=True)

  return render_template("views/home.html", user=current_user, special_products=special_products, max_special = home_special_products, max_new = home_new_products)

@views.route('/trade-in')
def trade_Onboard(): 
    return render_template('views/tradeOnboarding.html')

@views.route('/tradeForm')
@login_required  
def trade_form():
    return render_template('views/tradeForm.html')  

@views.route('/submitRequest', methods=['POST'])
@login_required
def submit_request():
    item_type = request.form.get('item-type')
    item_condition = request.form.get('item-condition')
    title = request.form.get('title')
    author_artist = request.form.get('author')
    genre = request.form.get('genre')
    isbn_or_cat = request.form.get('isbn')

    images = request.files.getlist('images')
    image_paths = []
    for file in images:
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/uploads', filename)
            file.save(file_path)
            image_paths.append(file_path)

    images_json = json.dumps(image_paths)
    new_item = tradeDetail(
        item_type=item_type,
        item_condition=item_condition,
        title=title,
        author_artist=author_artist,
        genre=genre,
        isbn_or_cat=isbn_or_cat,
        images=images_json,
        trade_number=current_user.id 
    )

    db.session.add(new_item)
    db.session.commit()

    flash('Trade item submitted successfully!', 'success')
    return redirect(url_for('views.trade_onboard'))
