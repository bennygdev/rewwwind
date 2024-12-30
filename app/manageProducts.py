from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .roleDecorator import role_required
from .forms import AddProductForm
from .models import Product
from . import db
import os

manageProducts = Blueprint('manageProducts', __name__)
# Products page

@manageProducts.route('/manage-products')
@login_required
@role_required(2, 3)
def product_listings():
    products = Product.query.all()
    return render_template("dashboard/manageProducts/products.html", user=current_user, products=products)

@manageProducts.route('/manage-products/add-product', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def add_product():
    form = AddProductForm()
    
    if form.validate_on_submit():
        productName = form.productName.data
        productCreator = form.productCreator.data
        productDescription = form.productDescription.data
        productType = form.productType.data
        productGenre = form.productGenre.data
        productThumbnail = int(form.productThumbnail.data)
        productConditions = form.productConditions.data
        print(productConditions[0]['stock'])
        
        files = request.files.getlist('productImages')
        upload_folder = current_app.config['UPLOAD_FOLDER']
        for file in files:
            file.seek(0)
            file.save(os.path.join(upload_folder, secure_filename(file.filename))) 

        new_product = Product (
            name = productName,
            creator = productCreator,
            image_thumbnail = f'media/uploads/{secure_filename(files[productThumbnail].filename)}',
            description = productDescription,
            variants = productConditions,
            category_id = 1
          )
        
        db.session.add(new_product)
        db.session.commit()
        print("item added successfully", form.data)

    # debugger
    if form.errors:
        print("Form validation errors:")
        for field, error_messages in form.errors.items():
            print(f"{field}: {error_messages}")

    return render_template("dashboard/manageProducts/addProduct.html", user=current_user, form=form)