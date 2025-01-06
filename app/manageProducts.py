from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSON
from .roleDecorator import role_required
from .forms import AddProductForm, DeleteProductForm #, EditProductForm
from .models import Product
from . import db
import os

from math import ceil
# from datetime import datetime

manageProducts = Blueprint('manageProducts', __name__)

# Products page
def pagination(products):
    # count products
    total_products = len(products)

    # count warnings (low stock)
    total_warnings = sum(
        1 for product in products
        if any(variant.get('stock') <= 10 for variant in product.variants)
    )

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10

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

    return products, total_products, total_warnings, total_pages, page, search_query

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def products_listing():
    products = Product.query.all()
    deleteForm = DeleteProductForm()

    products, total_products, total_warnings, total_pages, page, search_query = pagination(products)

    return render_template("dashboard/manageProducts/products.html", user=current_user, products=products, total_products=total_products, total_warnings=total_warnings, deleteForm=deleteForm, total_pages=total_pages, current_page=page, search_query=search_query) #, datetime=datetime
    

from flask import jsonify, flash
import os
from werkzeug.utils import secure_filename

@manageProducts.route('/manage-products/add-product', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_product():
    form = AddProductForm()

    # Handle form submission
    if form.validate_on_submit():
        try:
            # Extract form data
            print(form.data)
            productName = form.productName.data
            productCreator = form.productCreator.data
            productDescription = form.productDescription.data
            productType = form.productType.data
            productGenre = form.productGenre.data
            productThumbnail = int(form.productThumbnail.data)
            productConditions = form.productConditions.data
            is_featured_special = form.productIsFeaturedSpecial.data
            is_featured_staff = form.productIsFeaturedStaff.data

            # Handle file upload
            files = request.files.getlist('productImages')
            upload_folder = current_app.config['UPLOAD_FOLDER']
            uploaded_file_paths = []

            for file in files:
                if file:
                    file.seek(0)  # Ensure we're at the start of the file
                    file_path = os.path.join(upload_folder, secure_filename(file.filename))
                    file.save(file_path)
                    uploaded_file_paths.append(f"media/uploads/{secure_filename(file.filename)}")

            # Create the new product object
            new_product = Product(
                name=productName,
                creator=productCreator,
                image_thumbnail=f"media/uploads/{secure_filename(files[productThumbnail].filename)}",
                images=uploaded_file_paths,
                description=productDescription,
                variants=productConditions,
                is_featured_special = is_featured_special,
                is_featured_staff = is_featured_staff,
                category_id=1
            )

            # Add the product to the database and commit
            db.session.add(new_product)
            db.session.commit()

            # Return a success response
            flash("The product has been added successfully.", "success")
            return jsonify({'success': True, 'message': 'Product added successfully!'})

        except Exception as e:
            # Return error response if anything goes wrong
            return jsonify({'error': False, 'message': f"An error occurred: {str(e)}"})

    # Handle form validation errors
    if form.errors:
        error_messages = [f"{', '.join(errors)}" for field, errors in form.errors.items()]
        return jsonify({'error': False, 'message': f"{', '.join(error_messages)}"})

    # Default return in case of GET request or no validation errors
    return render_template("dashboard/manageProducts/addProduct.html", user=current_user, form=form)

@manageProducts.route('/manage-products/update-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddProductForm()

    if request.method == 'GET':  # Populate the form with product data for GET
        form.productName.data = product.name
        form.productCreator.data = product.creator
        form.productDescription.data = product.description
        form.productType.data = product.category_id
        form.productGenre.data = product.category_id
        form.productThumbnail.data = product.image_thumbnail
        form.productIsFeaturedSpecial.data = product.is_featured_special
        form.productIsFeaturedStaff.data = product.is_featured_staff

        if product.variants:
            variant = product.variants[0]  # Take the first variant condition
            form.productConditions[0].condition.data = variant['condition']
            form.productConditions[0].stock.data = variant['stock']
            form.productConditions[0].price.data = variant['price']

        for variant in product.variants[1:]:  # Skip the first variant since it's already set
            form.productConditions.append_entry({
                'condition': variant['condition'],
                'stock': variant['stock'],
                'price': variant['price']
            })
        
        if product.images:
            print(product.images)
        else:
            flash('No images were uploaded.', "update_images_false")

    if form.validate_on_submit():  # Handle POST request
        try:
            # Update product details
            product.name = form.productName.data
            product.creator = form.productCreator.data
            product.description = form.productDescription.data
            product.variants = form.productConditions.data
            product.category_id = form.productType.data
            product.image_thumbnail = form.productThumbnail.data
            product.is_featured_special = form.productIsFeaturedSpecial.data
            product.is_featured_staff = form.productIsFeaturedStaff.data

            # Handle file uploads
            files = request.files.getlist('productImages')
            uploaded_file_paths = []
            upload_folder = current_app.config['UPLOAD_FOLDER']
            for file in files:
                if file:
                    file_path = os.path.join(upload_folder, secure_filename(file.filename))
                    file.save(file_path)
                    uploaded_file_paths.append(f"media/uploads/{secure_filename(file.filename)}")
            
            if uploaded_file_paths:
                product.images.extend(uploaded_file_paths)  # Assuming product has an `images` attribute
            print(vars(product))
            
            # Commit changes
            db.session.commit()
            flash("The product has been updated successfully.", "success")
            return redirect(url_for('manageProducts.products_listing'))

        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash(f"An error occurred: {str(e)}", "danger")

    if request.method == 'POST' and form.errors:  # Handle validation errors
        flash("Please fix the errors in the form.", "danger")
        print(form.errors)

    return render_template("dashboard/manageProducts/updateProduct.html", user=current_user, form=form, product=product)

@manageProducts.route('/manage-products/delete-product', methods=['POST'])
@login_required
@role_required(2, 3)
def delete_product():
    products = Product.query.all()
    deleteForm = DeleteProductForm()
    products, total_products, total_warnings, total_pages, page, search_query = pagination(products)

    if deleteForm.validate_on_submit():
        id = deleteForm.productID.data
        product_to_delete = Product.query.get(id)
        if product_to_delete:
            db.session.delete(product_to_delete)
            db.session.commit()
            flash("The product has been removed successfully.", "success")

        # Refresh the products list
        products = Product.query.all()
        products, total_products, total_warnings, total_pages, page, search_query = pagination(products)

        return redirect(url_for('manageProducts.products_listing'))
        

    return render_template("dashboard/manageProducts/products.html", user=current_user, products=products, total_products=total_products, total_warnings=total_warnings, deleteForm=deleteForm, total_pages=total_pages, current_page=page, search_query=search_query) #, datetime=datetime
