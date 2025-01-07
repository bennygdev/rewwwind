from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .models import Product, Review
from .forms import AddReviewForm
from . import db
from math import ceil

productPagination = Blueprint('productPagination', __name__)

@productPagination.route('/')
def product_pagination():
  products = Product.query.all()

  # count products
  total_products = len(products)

  # pagination
  page = request.args.get('page', 1, type=int)
  per_page = 16

  # search logic
  search_query = request.args.get('q', '', type=str)

  if search_query:
      products_query = Product.query.filter(Product.name.ilike(f"%{search_query}%"))
  else:
      products_query = Product.query

  # pagination logic
  total_products = products_query.count()
  products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)

  total_pages = ceil(total_products / per_page)
  
  return render_template("/views/products.html", user=current_user, products=products, total_products=total_products, total_pages=total_pages, current_page=page, search_query=search_query)

@productPagination.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    # Query the database for the product
    product = Product.query.get_or_404(product_id) 
    reviews = product.reviews
    if product is None:
       abort(404)
    
    reviewForm = AddReviewForm()

    return render_template("/views/productPage.html", user=current_user, product=product, form=reviewForm, reviews=reviews)

@productPagination.route('/product/<int:product_id>/add-review', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    reviewForm = AddReviewForm()

    if reviewForm.validate_on_submit():
        # Create a new review object and save it to the database
        new_review = Review(
            rating=reviewForm.rating.data,
            show_username = reviewForm.show_username.data,
            description=reviewForm.description.data,
            product_id=product.id,
            user_id=current_user.id,
        )
        db.session.add(new_review)
        db.session.commit()
        
        print(new_review.rating, new_review.show_username, new_review.description, new_review.product_id, new_review.user_id)

        flash("Your review was added successfully!", "success")
        
    
    # Return an error response if validation fails
    if reviewForm.errors:
        for error in reviewForm.errors:
            print(error)
        flash("There were errors.", "error")

    return render_template("/views/productPage.html", user=current_user, product=product, form=reviewForm)

@productPagination.route('/featured/specials')
def product_specials():
    page = request.args.get('page', 1, type=int)
    per_page = 16

    search_query = request.args.get('q', '', type=str)

    products_query = Product.query.filter_by(is_featured_special=True)

    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

    total_products = products_query.count()

    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)

    total_pages = ceil(total_products / per_page)


    return render_template("/views/productSpecials.html", user=current_user, products=products, total_products=total_products, total_pages=total_pages, current_page=page)

@productPagination.route('/featured/staff_picks')
def product_staff():
    page = request.args.get('page', 1, type=int)
    per_page = 16

    search_query = request.args.get('q', '', type=str)

    products_query = Product.query.filter_by(is_featured_staff=True)

    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

    total_products = products_query.count()

    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)

    total_pages = ceil(total_products / per_page)


    return render_template("/views/productStaff.html", user=current_user, products=products, total_products=total_products, total_pages=total_pages, current_page=page)