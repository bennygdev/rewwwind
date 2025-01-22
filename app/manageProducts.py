from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, current_app, session
from flask_login import login_required, current_user
from sqlalchemy import cast, Integer
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import JSON
from .roleDecorator import role_required
from .forms import AddProductForm, DeleteProductForm, AddProductFormData #, EditProductForm
from .models import Product, Category, SubCategory, ProductSubCategory, OrderItem
from . import db
import os

from math import ceil
# from datetime import datetime
import shelve

manageProducts = Blueprint('manageProducts', __name__)

# Products page
def pagination(products):
    # count products
    total_products = len(products)

    # count warnings (low stock)
    total_warnings = sum(
        1 for product in products
        if any(condition.get('stock') <= 10 for condition in product.conditions)
    )

    products_query = Product.query

    # search logic
    search_query = request.args.get('q', '', type=str)
    if search_query:
        products_query = Product.query.filter(Product.name.ilike(f"%{search_query}%"))
    
    # filter logic
    category_filter = request.args.get('type', '', type=str).title()
    subcategory_filter = request.args.get('genre', '', type=str).title()
    featured_filter = request.args.get('featured', '', type=str)
    stock_filter = request.args.get('stock', '', type=str)
    
    if category_filter and category_filter != 'All':
        products_query = products_query.join(Product.category).filter(Category.category_name == category_filter)
    if subcategory_filter and subcategory_filter != 'All':
        products_query = products_query.join(Product.subcategories).filter(SubCategory.subcategory_name == subcategory_filter)
    if featured_filter and featured_filter != 'none':
        if 'special' in featured_filter:
            products_query = products_query.filter(Product.is_featured_special)
        else:
            products_query = products_query.filter(Product.is_featured_staff)

    if stock_filter and stock_filter != 'all':
        if 'limited' in stock_filter:
            products_query = products_query.filter(cast(Product.conditions[0]['stock'], Integer) <= 10)
        elif 'plenty' in stock_filter:
            products_query = products_query.filter(cast(Product.conditions[0]['stock'], Integer) > 10)
        elif 'no' in stock_filter:
            products_query = products_query.filter(cast(Product.conditions[0]['stock'], Integer) == 0)
        elif 'lowest' in stock_filter:
            products_query = products_query.order_by(cast(Product.conditions[0]['stock'], Integer).asc())
        else:
            products_query = products_query.order_by(cast(Product.conditions[0]['stock'], Integer).desc())
    
    if not category_filter:
        subcategory_filter = ""

    # pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 10

    total_products = products_query.count()
    products = products_query.order_by(Product.id).paginate(page=page, per_page=per_page)

    total_pages = ceil(total_products / per_page)

    return products, total_products, total_warnings, total_pages, page, search_query, category_filter, subcategory_filter, featured_filter, stock_filter

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def products_listing():
    products = Product.query.all()
    deleteForm = DeleteProductForm()

    products, total_products, total_warnings, total_pages, page, search_query, category_filter, subcategory_filter, featured_filter, stock_filter = pagination(products)

    categories = Category.query.all()[:8]
    subcategories = SubCategory.query.join(Category).filter(Category.category_name == category_filter)[:8]

    return render_template(
        "dashboard/manageProducts/products.html", 
        user=current_user, 
        products=products, 
        total_products=total_products, 
        total_warnings=total_warnings, 
        deleteForm=deleteForm, 
        total_pages=total_pages, 
        current_page=page, 
        search_query=search_query,
        categories=categories,
        subcategories=subcategories,
        category_filter=category_filter,
        subcategory_filter=subcategory_filter,
        featured_filter=featured_filter,
        stock_filter=stock_filter
        ) #, datetime=datetime

# uploads folder cleaning logic
def clean_uploads_folder():
    used_images = set()
    products = Product.query.all()
    for product in products:
        if product.images:
            used_images.update(product.images)

    uploads_folder = os.path.join(current_app.static_folder, 'media', 'uploads')
    all_files = set(os.listdir(uploads_folder))

    unused_files = all_files - used_images

    for filename in unused_files:
        file_path = os.path.join(uploads_folder, filename)
        try:
            os.remove(file_path)
            print(f"Deleted unused file: {filename}")
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")

@manageProducts.route('/manage-products/add-product', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_product():
    form = AddProductForm()
    clean_uploads_folder()
    if request.method == 'GET':
        try:
            shelve_path = os.path.join(current_app.instance_path, 'shelve.db')
            with shelve.open(shelve_path) as shelve_db:
                user_id = str(current_user.id)
                if user_id in shelve_db:
                    saved_data = shelve_db[user_id]

                    # print(saved_data.get_conditions())

                    form.productName.data = saved_data.get_name()
                    form.productCreator.data = saved_data.get_creator()
                    form.productDescription.data = saved_data.get_description()
                    form.productType.data = saved_data.get_type()
                    form.productGenre.data = saved_data.get_genre()
                    form.productIsFeaturedSpecial.data = saved_data.get_featured_special()
                    form.productIsFeaturedStaff.data = saved_data.get_featured_staff()

                    condition_choices = [
                    ('Brand New', 'Brand New'),
                    ('Like New', 'Like New'),
                    ('Lightly Used', 'Lightly Used'),
                    ('Well Used', 'Well Used')
                    ]

                    if saved_data.get_conditions():
                        condition = saved_data.get_conditions()[0]  # Take the first variant condition
                        form.productConditions[0].condition.data = condition['condition']
                        form.productConditions[0].stock.data = condition['stock']
                        form.productConditions[0].price.data = condition['price']

                        for condition in saved_data.get_conditions()[1:]:  # Skip the first condition since it's already set
                            entry = form.productConditions.append_entry({
                                'stock': condition['stock'],
                                'price': condition['price']
                            })
                            entry.condition.choices = condition_choices
                            entry.condition.data = condition['condition']
            print("Previously saved form data has been loaded.")
        except Exception as e:
            print(f"Failed to load saved form data: {e}")
    else:
        if form.validate_on_submit():
            try:
                productName = form.productName.data
                productCreator = form.productCreator.data
                productDescription = form.productDescription.data
                productType = form.productType.data
                productGenre = form.productGenre.data
                subcategory = SubCategory.query.filter(SubCategory.id==productGenre).first()
                # print(subcategory)
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
                        file.seek(0)  # PLEASE REMEMBER, i keep on forgetting lol
                        file_path = os.path.join(upload_folder, secure_filename(file.filename))
                        file.save(file_path)
                        uploaded_file_paths.append(secure_filename(file.filename))

                # Create the new product object
                new_product = Product(
                    name=productName,
                    creator=productCreator,
                    image_thumbnail=secure_filename(files[productThumbnail].filename),
                    images=uploaded_file_paths,
                    category_id=productType,
                    subcategories=[subcategory],
                    description=productDescription,
                    conditions=productConditions,
                    is_featured_special = is_featured_special,
                    is_featured_staff = is_featured_staff
                )

                db.session.add(new_product)
                db.session.commit()

                try:
                    shelve_path = os.path.join(current_app.instance_path, 'shelve.db')
                    with shelve.open(shelve_path) as shelve_db:
                        user_id = str(current_user.id)
                        if user_id in shelve_db:
                            del shelve_db[user_id]
                except Exception as e:
                    print(f"Error deleting saved form data: {e}")

                # Set a session flag to prevent immediate re-saving
                session['product_added'] = True

                # Return a success response
                flash("The product has been added successfully.", "success")
                return jsonify({'success': True, 'message': 'Product added successfully!'})
            
            except ValueError:
                return jsonify({'error': False, 'message': "No images were uploaded. Please upload at least one image."})
            except Exception as e:
                # Return error response if anything goes wrong
                return jsonify({'error': False, 'message': f"An error occurred: {str(e)}"})

    # Handle form validation errors
    if form.errors:
        error_messages = [f"{', '.join(errors)}" for field, errors in form.errors.items()]
        return jsonify({'error': False, 'message': f"{', '.join(error_messages)}"})

    # Default return in case of GET request or no validation errors
    return render_template("dashboard/manageProducts/addProduct.html", user=current_user, form=form)

@manageProducts.route('/manage-products/save', methods=['POST'])
@login_required
@role_required(2, 3)
def save_product_form():
    try:
        if session.get('product_added'):
            session.pop('product_added')
            print(True)
            return jsonify({'success': False, 'message': "Skipped after product addition."})
        
        shelve_path = os.path.join(current_app.instance_path, 'shelve.db')
        
        with shelve.open(shelve_path) as db:
            user_id = str(current_user.id)
            data = request.get_json()

            form_data = AddProductFormData(
                name = data.get('productName'),
                creator = data.get('productCreator'),
                description = data.get('productDescription'),
                type = data.get('productType'),
                genre = data.get('productGenre'),
                conditions = data.get('productConditions'),
                featured_special = data.get('isFeaturedSpecial'),
                featured_staff = data.get('isFeaturedStaff')
            )

            db[user_id] = form_data
        print('success')
        flash("The product data (except images) was saved successfully.<br>It can be viewed again when revisiting the 'Add Product' form, as long as you do not log out.", "success")
        return redirect(url_for('manageProducts.products_listing'))
    
    except Exception as e:
        print('failure', e)
        flash("There was an error saving the form.", "error")
        return jsonify({'error': False, 'message': "Error in saving form."})

@manageProducts.route('/manage-products/update-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddProductForm()
    
    clean_uploads_folder()

    if request.method == 'GET':  # Populate the form with product data for GET
        form.productName.data = product.name
        form.productCreator.data = product.creator
        form.productDescription.data = product.description
        form.productType.data = product.category.category_name
        form.productGenre.data = product.subcategories[0].subcategory_name
        form.productThumbnail.data = product.image_thumbnail
        form.productIsFeaturedSpecial.data = product.is_featured_special
        form.productIsFeaturedStaff.data = product.is_featured_staff

        condition_choices = [
        ('Brand New', 'Brand New'),
        ('Like New', 'Like New'),
        ('Lightly Used', 'Lightly Used'),
        ('Well Used', 'Well Used')
        ]

        # there's probably a better way but if it works it works
        if product.conditions:
            condition = product.conditions[0]  # Take the first variant condition
            form.productConditions[0].condition.data = condition['condition']
            form.productConditions[0].stock.data = condition['stock']
            form.productConditions[0].price.data = condition['price']

            for condition in product.conditions[1:]:  # Skip the first condition since it's already set
                entry = form.productConditions.append_entry({
                    'stock': condition['stock'],
                    'price': condition['price']
                })
                entry.condition.choices = condition_choices
                entry.condition.data = condition['condition']
        # if not product.images:
        #     print('No images were uploaded.')

    if form.validate_on_submit():  # Handle POST request
        try:
            # Update product details
            product.name = form.productName.data
            product.creator = form.productCreator.data
            product.description = form.productDescription.data
            product.conditions = form.productConditions.data
            product.category_id = form.productType.data
            product.subcategories = [SubCategory.query.filter(SubCategory.id==form.productGenre.data).first()]
            product.is_featured_special = form.productIsFeaturedSpecial.data
            product.is_featured_staff = form.productIsFeaturedStaff.data

            # Handle file uploads
            files = request.files.getlist('productImages')
            uploaded_file_paths = []
            upload_folder = current_app.config['UPLOAD_FOLDER']
            for file in files:
                if file:
                    file.seek(0)  # Ensure we're at the start of the file
                    file_path = os.path.join(upload_folder, secure_filename(file.filename))
                    file.save(file_path)
                    uploaded_file_paths.append(secure_filename(file.filename))
            
            product.images = [img for img in product.images if img in form.images.data.split(',')]
            # print(form.images.data)

            if uploaded_file_paths:
                product.images.extend(uploaded_file_paths)
                flag_modified(product, 'images')
            # print(product.images)
            
            product.image_thumbnail = product.images[int(form.productThumbnail.data)]

            # print(vars(product))
            
            # Commit changes
            db.session.commit()
            flash("The product has been updated successfully.", "success")
            return jsonify({'success': True, 'message': 'Product updated successfully!'})
        except ValueError:
            return jsonify({'error': False, 'message': "No images were uploaded. Please upload at least one image."})
        except Exception as e:
            # Return error response if anything goes wrong
            return jsonify({'error': False, 'message': f"An error occurred: {str(e)}"})

    if form.errors:
        error_messages = [f"{', '.join(errors)}" for field, errors in form.errors.items()]
        return jsonify({'error': False, 'message': f"{', '.join(error_messages)}"})

    return render_template("dashboard/manageProducts/updateProduct.html", user=current_user, form=form, product=product)

@manageProducts.route('/manage-products/delete-product', methods=['POST'])
@login_required
@role_required(2, 3)
def delete_product():
    products = Product.query.all()
    clean_uploads_folder()

    products, total_products, total_warnings, total_pages, page, search_query, category_filter, subcategory_filter, featured_filter, stock_filter = pagination(products)

    categories = Category.query.all()[:8]
    subcategories = SubCategory.query.join(Category).filter(Category.category_name == category_filter)[:8]
    deleteForm = DeleteProductForm()

    if OrderItem.query.filter(OrderItem.product_id==deleteForm.productID.data).first():
        flash("Sorry, the product you're about to delete is bound to an order.\nPlease make sure that the order is fulfilled before deleting this product.", "error")

    elif deleteForm.validate_on_submit():
        id = deleteForm.productID.data
        product_to_delete = Product.query.get(id)
        if product_to_delete:
            db.session.query(ProductSubCategory).filter_by(product_id=product_to_delete.id).delete()
            db.session.commit()

            db.session.delete(product_to_delete)
            db.session.commit()
            flash("The product has been removed successfully.", "success")

        # Refresh the products list
        products = Product.query.all()
        products, total_products, total_warnings, total_pages, page, search_query, category_filter, subcategory_filter, featured_filter, stock_filter = pagination(products)

        return redirect(url_for('manageProducts.products_listing'))

    return render_template(
        "dashboard/manageProducts/products.html", 
        user=current_user, 
        products=products, 
        total_products=total_products, 
        total_warnings=total_warnings, 
        deleteForm=deleteForm, 
        total_pages=total_pages, 
        current_page=page, 
        search_query=search_query,
        categories=categories,
        subcategories=subcategories,
        category_filter=category_filter,
        subcategory_filter=subcategory_filter,
        featured_filter=featured_filter,
        stock_filter=stock_filter
        ) #, datetime=datetime
