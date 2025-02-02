from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import cast, Float, Integer, func
from .roleDecorator import role_required
from .models import Product, Review, Category, SubCategory
from .forms import AddReviewForm, AddToCartForm, DeleteReviewForm
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
    category_filter = request.args.get('type', '', type=str)
    subcategory_filter = request.args.get('genre', '', type=str)
    if ',' in subcategory_filter:
        subcategory_filter = subcategory_filter.split(',')
    else:
        subcategory_filter = [subcategory_filter]
    match_req = request.args.get('match', '', type=str)
    if not match_req:
        match_req = 'or'
    price_filter = request.args.get('price', '', type=str)
    rating_filter = request.args.get('rating', '', type=str)

    if category_filter:
        products_query = products_query.join(Product.category).filter(Category.category_name == category_filter.title())
    if subcategory_filter and len(subcategory_filter) != 1:
        if 'or' in match_req:
            products_query = products_query.join(Product.subcategories).filter(
                SubCategory.subcategory_name.in_([entry.title() for entry in subcategory_filter])
            )
        elif 'and' in match_req:
            products_query = products_query.join(Product.subcategories).filter( 
                SubCategory.subcategory_name.in_([entry.title() for entry in subcategory_filter])
            ).group_by(Product.id).having(
                func.count(Product.id) == len(subcategory_filter)
            )
    if price_filter:
        if 'highest' in price_filter:
            products_query = products_query.order_by(cast(Product.conditions[0]['price'], Float).desc())
        else:
            products_query = products_query.order_by(cast(Product.conditions[0]['price'], Float).asc())
    if rating_filter:
        if type(rating_filter) is Integer:
            products_query = products_query.filter(cast(Product.rating, Integer) == int(rating_filter[0]))
        else:
            if 'highest' in rating_filter:
                products_query = products_query.order_by(Product.rating.desc())
            else:
                products_query = products_query.order_by(Product.rating.asc())
        

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 16

    total_products = products_query.count()
    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)


    total_pages = ceil(total_products / per_page)

    categories = Category.query.all()[:8]
    subcategories = SubCategory.query.all()
    if category_filter:
        subcategories = SubCategory.query.join(Category).filter(Category.category_name == category_filter.title())

    # filter choices
    category_choices = [(category.category_name.lower(), category.category_name) for category in categories]

    subcategory_choices = [(subcategory.subcategory_name.lower(), subcategory.subcategory_name) for subcategory in subcategories]
        

    price_choices = [
        ('highest', 'Highest first'),
        ('lowest', 'Lowest first')
    ]

    rating_choices = [
        ('highest', 'Highest first'),
        ('lowest', 'Lowest first'),
        ('1', '1 star'),
        ('2', '2 star'),
        ('3', '3 star'),
        ('4', '4 star'),
        ('5', '5 star')
    ]
    
    form = AddToCartForm()

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
        category_choices=category_choices,
        subcategory_filter=subcategory_filter,
        match_req=match_req,
        subcategory_choices=subcategory_choices,
        price_filter=price_filter,
        price_choices=price_choices,
        rating_filter=rating_filter,
        rating_choices=rating_choices,
        form=form
    )

@productPagination.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews_query = Review.query.filter_by(product_id=product_id)

    # Condition logic
    selected_condition_name = request.args.get('condition')
    if not selected_condition_name:
        selected_condition = product.conditions[0]
    else:
        selected_condition = next((condition for condition in product.conditions if condition['condition'] == selected_condition_name), None)
    print(selected_condition)
    
    # Filter logic
    rating_filter = request.args.get('rating', '', type=str)
    if rating_filter and rating_filter != 'all':
        if 'star' in rating_filter:
            reviews_query = reviews_query.filter(cast(Review.rating, Integer) == int(rating_filter[0]))
        elif 'highest' in rating_filter:
            reviews_query = reviews_query.order_by(Review.rating.desc())
        elif 'lowest' in rating_filter:
            reviews_query = reviews_query.order_by(Review.rating.asc())
    
    # Pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_reviews = reviews_query.count()

    reviews = reviews_query.order_by(Review.id).paginate(page=page, per_page=per_page)
    total_pages = ceil(total_reviews / per_page)
    
    if product is None:
        abort(404)

    reviewForm = AddReviewForm()
    cartForm = AddToCartForm()

    not_customer = request.args.get('not_customer', type=bool)

    # Render template
    return render_template(
        "/views/productPage.html",
        user=current_user,
        product=product,
        selected_condition=selected_condition,
        reviewform=reviewForm,
        cartform=cartForm,
        reviews=reviews,
        total_pages=total_pages,
        current_page=page,
        rating_filter=rating_filter,
        not_customer=not_customer
    )

@productPagination.route('/product/<int:product_id>/add-review', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    reviewForm = AddReviewForm()
    cartForm = AddToCartForm()
    
    # To avoid no reviews being shown
    page = request.args.get('page', 1, type=int)
    per_page = 5
    reviews_query = Review.query.filter_by(product_id=product_id)
    reviews = reviews_query.order_by(Review.id).paginate(page=page, per_page=per_page)

    # Condition logic
    selected_condition_name = request.args.get('condition')
    if not selected_condition_name:
        selected_condition = product.conditions[0]
    else:
        selected_condition = next((condition for condition in product.conditions if condition['condition'] == selected_condition_name), None)

    if reviewForm.validate_on_submit():
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

    if reviewForm.errors:
        for field, errors in reviewForm.errors.items():
            for error in errors:
                flash(f"<strong>Error:</strong> {error}", "error")

    return render_template("/views/productPage.html", user=current_user, product=product, reviewform=reviewForm, cartform=cartForm, reviews=reviews, selected_condition=selected_condition)

@productPagination.route('/product/<int:product_id>/update-review=<int:review_id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def update_review(product_id, review_id):
    product = Product.query.get_or_404(product_id)
    reviewForm = AddReviewForm()
    cartForm = AddToCartForm()
    review = Review.query.get_or_404(review_id)

    # To avoid no reviews being shown
    page = request.args.get('page', 1, type=int)
    per_page = 5
    reviews_query = Review.query.filter_by(product_id=product_id)
    reviews = reviews_query.order_by(Review.id).paginate(page=page, per_page=per_page)

    # Condition logic
    selected_condition_name = request.args.get('condition')
    if not selected_condition_name:
        selected_condition = product.conditions[0]
    else:
        selected_condition = next((condition for condition in product.conditions if condition['condition'] == selected_condition_name), None)
    print(selected_condition)    

    if current_user.id != review.user_id and current_user.role_id == 1:
        abort(401)
    if request.method == 'GET':
        if review:
            reviewForm.rating.data = review.rating
            reviewForm.show_username.data = review.show_username
            reviewForm.description.data = review.description
    else:
        if reviewForm.validate_on_submit():
            review.rating = int(reviewForm.rating.data)
            review.show_username = reviewForm.show_username.data
            review.description = reviewForm.description.data

            product.update_rating()

            print(review.rating, review.show_username, review.description)
            db.session.commit()

            flash("Your review was updated successfully!", "success")
            
        
        # Return an error response if validation fails
        if reviewForm.errors:
            for field, errors in reviewForm.errors.items():
                for error in errors:
                    flash(f"<strong>Error:</strong> {error}", "error")

    return render_template("/views/updateReview.html", user=current_user, product=product, reviewform=reviewForm, cartform=cartForm, reviews=reviews, review=review, selected_condition=selected_condition)

@productPagination.route('/product/<int:product_id>/delete-review=<int:review_id>', methods=['GET', 'POST'])
@login_required
@role_required(1, 2, 3)
def delete_review(product_id, review_id):
    product = Product.query.get_or_404(product_id)
    reviewForm = AddReviewForm()
    deleteForm = DeleteReviewForm()
    cartForm = AddToCartForm()
    review = Review.query.get_or_404(review_id)

    # To avoid no reviews being shown
    page = request.args.get('page', 1, type=int)
    per_page = 5
    reviews_query = Review.query.filter_by(product_id=product_id)
    reviews = reviews_query.order_by(Review.id).paginate(page=page, per_page=per_page)

    # Condition logic
    selected_condition_name = request.args.get('condition')
    if not selected_condition_name:
        selected_condition = product.conditions[0]
    else:
        selected_condition = next((condition for condition in product.conditions if condition['condition'] == selected_condition_name), None)
    print(selected_condition)

    if request.method == 'GET':
        if current_user.id != review.user_id and current_user.role_id == 1:
            abort(401)
    else:
        if deleteForm.validate_on_submit():
            db.session.delete(review)
            db.session.commit()

            product.update_rating()
            db.session.commit()

            flash("The review was successfully deleted.", "success")
        
        # Return an error response if validation fails
        if deleteForm.errors:
            for field, errors in deleteForm.errors.items():
                for error in errors:
                    print(error)
                    flash(f"<strong>Error:</strong> {error}", "error")

    return render_template("/views/productPage.html", user=current_user, product=product, reviewform=reviewForm, cartform=cartForm, reviews=reviews, review=review, delete=True, deleteform=deleteForm, selected_condition=selected_condition)

@productPagination.route('/featured/specials')
def product_specials():
    # Base query
    products_query = Product.query.filter_by(is_featured_special = True)

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

    total_products = products_query.count()
    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)


    total_pages = ceil(total_products / per_page)

    categories = Category.query.all()[:8]
    subcategories = SubCategory.query.join(Category).filter(Category.category_name == category_filter)[:8]

    if not category_filter:
        subcategory_filter = ""
    
    form = AddToCartForm()

    return render_template(
        "/views/productSpecials.html",
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
        rating_filter=rating_filter,
        form=form
    )

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
    
    form = AddToCartForm()

    return render_template("/views/productStaff.html", user=current_user, products=products, total_products=total_products, total_pages=total_pages, current_page=page, form=form)