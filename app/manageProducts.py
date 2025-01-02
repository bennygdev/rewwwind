from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .forms import AddProductForm, DeleteProductForm #, EditProductForm
from .models import Product
from . import db
import os

from datetime import datetime

manageProducts = Blueprint('manageProducts', __name__)
# Products page

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def product_listings():
    products = Product.query.all()
    productDeleteForm = DeleteProductForm()

    return render_template("dashboard/manageProducts/products.html", user=current_user, products=products, deleteForm=productDeleteForm, datetime=datetime)

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
            productName = form.productName.data
            productCreator = form.productCreator.data
            productDescription = form.productDescription.data
            productType = form.productType.data
            productGenre = form.productGenre.data
            productThumbnail = int(form.productThumbnail.data)
            productConditions = form.productConditions.data

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
                description=productDescription,
                variants=productConditions,
                category_id=1
            )

            # Add the product to the database and commit
            db.session.add(new_product)
            db.session.commit()

            # Return a success response
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

@manageProducts.route('/manage-products/delete-product', methods=['POST'])
@login_required
@role_required(2, 3)
def delete_product():
    deleteForm = DeleteProductForm()

    if deleteForm.validate_on_submit():
        id = deleteForm.productID.data

        product_to_delete = Product.query.get(id)
        if product_to_delete:
            # print(f"Deleting product: {product_to_delete.name}")
            db.session.delete(product_to_delete)
            db.session.commit()
            

        deleteForm.deleteConfirm.data = 'success'
        return render_template("dashboard/manageProducts/products.html", user=current_user, products=Product.query.all(), deleteForm=deleteForm) #datetime=datetime)

    # refresh with errors
    return render_template("dashboard/manageProducts/products.html", user=current_user, products=Product.query.all(), deleteForm=deleteForm) #datetime=datetime)