from . import db
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import URLSafeTimedSerializer as Serializer


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image = db.Column(db.String(150), nullable=True, default='profile_image_default.jpg')
    google_account = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(150), nullable=True)
    orderCount = db.Column(db.Integer, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)  # role table
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationship to Cart
    cart_items = db.relationship('Cart', back_populates='user', lazy=True)


    # Reset password methods
    def get_reset_token(self):
      s = Serializer(current_app.config['SECRET_KEY'])
      return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
      s = Serializer(current_app.config['SECRET_KEY'])
      try:
        user_id = s.loads(token, max_age=expires_sec)['user_id']
      except:
        return None

      return User.query.get(user_id)

class BillingAddress(db.Model):
  __tablename__ = 'billing_addresses'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  address_one = db.Column(db.String(255), nullable=False)
  address_two = db.Column(db.String(255), nullable=True)  # Optional
  unit_number = db.Column(db.String(15), nullable=False)
  postal_code = db.Column(db.String(20), nullable=False)
  phone_number = db.Column(db.String(20), nullable=False)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class PaymentInformation(db.Model):
  __tablename__ = 'payment_information'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  payment_type = db.Column(db.String(20), nullable=False)
  card_number = db.Column(db.String(16), nullable=False) # store as string since leading zeros
  card_name = db.Column(db.String(255), nullable=False)
  expiry_date = db.Column(db.Date, nullable=False)
  card_cvv = db.Column(db.String(3), nullable=False) # store as string since leading zeros
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class Role(db.Model):
  __tablename__ = 'roles'
  id = db.Column(db.Integer, primary_key=True)
  role_name = db.Column(db.String(50), unique=True, nullable=False)
  users = db.relationship('User', backref='role', lazy=True)  # otm

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=True)
    creator = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_thumbnail = db.Column(db.String(300), nullable=True)
    images = db.Column(db.JSON, nullable=True)  # list of uploaded images
    variants = db.Column(db.JSON, nullable=True)  # store variants (name, stock, price)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False) 
    category = db.relationship('Category', backref='products', lazy=True)  # backref categories
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)  # otm orderItem

class Review(db.Model):
  __tablename__ = 'reviews'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  show_username = db.Column(db.Boolean, default=False)
  rating = db.Column(db.Integer, nullable=False)
  description = db.Column(db.String(1000), nullable=True)
  created_at = db.Column(db.DateTime(timezone=True), default=func.now())
  updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
  product = db.relationship('Product', backref='reviews', lazy=True)

  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  user = db.relationship('User', backref='reviews', lazy=True)

  cart_entries = db.relationship('Cart', back_populates='product', lazy=True)




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
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  category_name = db.Column(db.String(100), unique=True, nullable=False)

class ProductCategory(db.Model):
  __tablename__ = 'product_categories'
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    user = db.relationship('User', back_populates='cart_items')  # Changed backref name to 'cart_entries'
    product = db.relationship('Product', back_populates='cart_entries')  # Product can appear in multiple carts





