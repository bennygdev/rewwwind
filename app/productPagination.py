from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import cast, Float, Integer
from .roleDecorator import role_required
from .models import Product, Review, Category, SubCategory
from .forms import AddReviewForm
from . import db
from math import ceil

productPagination = Blueprint('productPagination', __name__)

@productPagination.route('/')
def product_pagination():
    # Base query
    products_query = Product.query

    # Search logic
    search_query = request.args.get('q', '', type=str)
    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

    # Filter logic
    category_filter = request.args.get('type', '', type=str).title()
    subcategory_filter = request.args.get('genre', '', type=str).title()
    price_filter = request.args.get('price', '', type=str)
    rating_filter = request.args.get('rating', '', type=str)

    if category_filter and category_filter != 'All':
        products_query = products_query.join(Product.category).filter(Category.category_name == category_filter)
    if subcategory_filter and subcategory_filter != 'All':
        products_query = products_query.join(Product.subcategories).filter(SubCategory.subcategory_name == subcategory_filter)
    if price_filter and price_filter != 'all':
        if 'highest' in price_filter:
            products_query = products_query.order_by(cast(Product.conditions[0]['price'], Float).desc())
        else:
            products_query = products_query.order_by(cast(Product.conditions[0]['price'], Float).asc())
    if rating_filter and rating_filter != 'all':
        if 'star' in rating_filter:
            products_query = products_query.filter(cast(Product.rating, Integer) == int(rating_filter[0]))
        else:
            if 'highest' in rating_filter:
                products_query = products_query.order_by(Product.rating.desc())
            else:
                products_query = products_query.order_by(Product.rating.asc())
        

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 16

    filters_changed = request.args.get('filters_changed', 'false').lower() == 'true'
    if filters_changed:
        page = 1
        return redirect(url_for(
            'productPagination.product_pagination', 
            page=1, 
            q=search_query if search_query else None, 
            type=category_filter if category_filter else None, 
            genre=subcategory_filter if subcategory_filter else None, 
            price=price_filter if price_filter else None, 
            rating=rating_filter if rating_filter else None, 
            filters_changed='false'
            ))

    total_products = products_query.count()
    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)


    total_pages = ceil(total_products / per_page)

    categories = Category.query.all()[:8]
    subcategories = SubCategory.query.join(Category).filter(Category.category_name == category_filter)[:8]

    if not category_filter:
        subcategory_filter = ""

    # Render the template
    return render_template(
        "/views/products.html",
        user=current_user,
        products=products,
        total_products=total_products,
        total_pages=total_pages,
        current_page=page,
        search_query=search_query,
        categories=categories,
        subcategories=subcategories,
        category_filter=category_filter,
        subcategory_filter=subcategory_filter,
        price_filter=price_filter,
        rating_filter=rating_filter
    )

@productPagination.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    # Query the database for the product
    product = Product.query.get_or_404(product_id)
    
    # Query for reviews related to the product
    reviews_query = Review.query.filter_by(product_id=product_id)
    
    # Filter logic
    rating_filter = request.args.get('rating', '', type=str)
    if rating_filter and rating_filter != 'all':
        if 'star' in rating_filter:
            # Filter reviews by exact rating (e.g., 4-star reviews)
            reviews_query = reviews_query.filter(cast(Review.rating, Integer) == int(rating_filter[0]))
        elif 'highest' in rating_filter:
            # Sort reviews by highest rating
            reviews_query = reviews_query.order_by(Review.rating.desc())
        elif 'lowest' in rating_filter:
            # Sort reviews by lowest rating
            reviews_query = reviews_query.order_by(Review.rating.asc())
    
    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_reviews = reviews_query.count()

    if rating_filter:
        page = 1  # Reset to page 1 when a filter is applied

    reviews = reviews_query.order_by(Review.id).paginate(page=page, per_page=per_page)
    total_pages = ceil(total_reviews / per_page)
    
    # Ensure product exists
    if product is None:
        abort(404)
    
    # Review form instance
    reviewForm = AddReviewForm()

    # Render template
    return render_template(
        "/views/productPage.html",
        user=current_user,
        product=product,
        form=reviewForm,
        reviews=reviews,
        total_pages=total_pages,
        current_page=page,
        rating_filter=rating_filter
    )
@productPagination.route('/product/<int:product_id>/add-review', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    reviewForm = AddReviewForm()
    reviews = product.reviews

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

        product.update_rating()
        db.session.commit()
        
        print(new_review.rating, new_review.show_username, new_review.description, new_review.product_id, new_review.user_id)

        flash("Your review was added successfully!", "success")
        
    
    # Return an error response if validation fails
    if reviewForm.errors:
        for field, errors in reviewForm.errors.items():
            for error in errors:
                flash(f"<strong>Error:</strong> {error}", "error")

    return render_template("/views/productPage.html", user=current_user, product=product, form=reviewForm, reviews=reviews)

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