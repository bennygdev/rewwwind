from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)  # role table
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    orders = db.relationship('Order', backref='user', lazy=True) # otm order

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)  # otm

# class Product(db.Model):
#     __tablename__ = 'products'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     price = db.Column(db.Numeric(10, 2), nullable=False)
#     stock_quantity = db.Column(db.Integer, default=0)
#     image_path = db.Column(db.String(300), nullable=True) 
#     created_at = db.Column(db.DateTime(timezone=True), default=func.now())
#     updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
#     categories = db.relationship('Category', secondary='product_categories', lazy='subquery', backref=db.backref('products', lazy=True)) # mtm category
#     order_items = db.relationship('OrderItem', backref='product', lazy=True) # otm orderitems
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_thumbnail = db.Column(db.String(300), nullable=True)
    images = db.Column(db.JSON, nullable=True)  # list of uploaded images
    variants = db.Column(db.JSON, nullable=True)  # store variants (name, price, stock)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False) 
    category = db.relationship('Category', backref='products', lazy=True)  # backref categories
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)  # otm orderItem


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime(timezone=True), default=func.now())
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    
    order_items = db.relationship('OrderItem', backref='order', lazy=True) # otm orderitems

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False) 
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)

class ProductCategory(db.Model):
  __tablename__ = 'product_categories'
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
