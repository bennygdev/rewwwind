from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from .forms import TradeItemForm
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

  staff_products = Product.query.filter_by(is_featured_staff=True).all() # staff (featured) products
  home_staff_products = staff_products[:3]

  # staff_picks = Product.query.filter_by(is_featured_staff=True)

  return render_template("views/home.html", user=current_user, special_products=special_products, max_special = home_special_products, max_new = home_new_products, max_staff = home_staff_products)

@views.route('/trade-in')
def trade_Onboard(): 
    return render_template('views/tradeOnboarding.html')

@views.route('/tradeForm', methods=['GET', 'POST'])
@login_required  
def trade_form():
    form = TradeItemForm()

    if form.validate_on_submit():

        item_type = form.item_type.data
        item_condition = form.item_condition.data
        title = form.title.data
        author = form.author.data
        genre = form.genre.data
        isbn = form.isbn.data
        images = request.files.getlist('images')


        image_paths = []
        for file in images:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_paths.append(file_path)

        images_json = json.dumps(image_paths)

        new_item = tradeDetail(
            item_type=item_type,
            item_condition=item_condition,
            title=title,
            author_artist=author,
            genre=genre,
            isbn_or_cat=isbn,
            images=images_json,
            trade_number=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()

        flash('Trade item submitted successfully!', 'success')
        return redirect(url_for('views.home'))

    return render_template('views/tradeForm.html', form=form)
