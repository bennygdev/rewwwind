from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from .forms import TradeItemForm, MailingListForm, AddToCartForm
from .models import Product, tradeDetail, MailingList
from . import db
from datetime import timedelta
from sqlalchemy import func
from secrets import token_urlsafe
import uuid
from sqlalchemy.orm.attributes import flag_modified

views = Blueprint('views', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)  

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unsubscribe_token():
  return token_urlsafe(16)

@views.route('/', methods=['GET', 'POST'])
def home():
  cart_form=AddToCartForm()
  mailing_list_form = MailingListForm()


  special_products = Product.query.filter_by(is_featured_special=True).all() # special (featured) products
  home_special_products = special_products[:8] # max special to display in home
  
  max_days = func.now() - timedelta(days=7)
  new_products = Product.query.filter(Product.created_at >= max_days).all() # product should be less than 7 days old to be new
  home_new_products = new_products[:18]

  staff_products = Product.query.filter_by(is_featured_staff=True).all() # staff (featured) products
  home_staff_products = staff_products[:3]

  # staff_picks = Product.query.filter_by(is_featured_staff=True)

  if request.method == 'POST':
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      if mailing_list_form.validate():
        try:
          new_subscriber = MailingList(
            email=mailing_list_form.email.data,
            unsubscribe_token=generate_unsubscribe_token()
          )
          db.session.add(new_subscriber)
          db.session.commit()
          return jsonify({'success': True})
        except Exception as e:
          db.session.rollback()
          return jsonify({'success': False, 'error': 'Subscription failed'})
      else:
        # Return validation errors
        return jsonify({
          'success': False, 
          'error': mailing_list_form.email.errors[0] if mailing_list_form.email.errors else 'Validation failed'
        })
      
    # fallback for non ajax
    if mailing_list_form.validate_on_submit():
      new_subscriber = MailingList(
        email=mailing_list_form.email.data,
        unsubscribe_token=generate_unsubscribe_token()
      )
      db.session.add(new_subscriber)
      db.session.commit()

  return render_template(
    "views/home.html", 
    user=current_user, 
    special_products=special_products, 
    max_special = home_special_products, 
    max_new = home_new_products, 
    max_staff = home_staff_products,
    mailing_list_form=mailing_list_form,
    cart_form=cart_form
  )

@views.route('/terms-of-service')
def terms_of_service():
  return render_template('views/termsofservice.html')

@views.route('/privacy-policy')
def privacy_policy():
  return render_template('views/privacypolicy.html')

@views.route('/license')
def license():
  return render_template('views/license.html')

@views.route('/exchanges-and-returns')
def exchanges_and_returns():
  return render_template('views/exchanges.html')

@views.route('/faq')
def faq():
  return render_template('views/faq.html')

@views.route('/trade-in')
def trade_Onboard(): 
  return render_template('views/tradeOnboarding.html')

@views.route('/condition-guidelines')
def condition_guidelines():
  return render_template('views/condition_guidelines.html')

@views.route('/about-us')
def about_us():
  return render_template('views/aboutus.html')

@views.route('/contact-us')
def contact_us():
  return render_template('views/contactus.html')

@views.route('/our-impact')
def our_impact():
  return render_template('views/ourimpact.html')

@views.route('/rewards')
def rewards_page():
  return render_template('views/rewards.html')

@views.route('/tradeForm', methods=['GET', 'POST'])
@login_required  
def trade_form():
    form = TradeItemForm()

    if current_user.role_id in [2, 3]:
        flash("Admins and owners are not allowed to trade in items to avoid conflicts.\nPlease use a dummy customer account instead.", "info")
        return redirect(url_for('auth.login'))

    if form.validate_on_submit():  
        try:
            # Create trade item
            trade = tradeDetail(
                item_type=form.item_type.data,
                item_condition=form.item_condition.data,
                title=form.title.data,
                author_artist=form.author.data,
                genre=form.genre.data,
                isbn_or_cat=form.isbn.data,
                user=current_user
            )

            # Handle image uploads
            files = request.files.getlist('images')
            uploaded_file_paths = []
            upload_folder = current_app.config['UPLOAD_FOLDER']

            # Ensure upload folder exists
            os.makedirs(upload_folder, exist_ok=True)

            print(f"Uploading {len(files)} images...")  # Debugging output

            for file in files:
                if file and allowed_file(file.filename):  
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    uploaded_file_paths.append(filename)  # Save filename for DB

            # Store images as JSON list (ensure correct format)
            if uploaded_file_paths:
                trade.images = json.dumps(uploaded_file_paths)  # Convert to JSON string
            else:
                trade.images = "[]"  # Ensure an empty list if no images

            flag_modified(trade, "images")  

            # Debugging: Print stored data
            print("Images stored in DB:", trade.images)

            # Commit changes
            db.session.add(trade)
            db.session.commit()

            flash('Trade item submitted successfully!', 'success')
            return redirect(url_for('manageTradeins.manage_tradeins'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('views.trade_form'))

    return render_template('views/tradeForm.html', form=form)