from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
DB_NAME = "database.db"
csrf = CSRFProtect()
mail = Mail()
oauth = OAuth()

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = '123456789'
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
  app.config['MAIL_PORT'] = 465
  app.config['MAIL_USE_SSL'] = True
  app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
  app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS') 

  app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'media', 'uploads') # temporary image upload folder
  if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

  app.config['OAUTH2_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
  app.config['OAUTH2_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
  app.config['OAUTH2_META_URL'] = 'https://accounts.google.com/.well-known/openid-configuration'

  mail = Mail(app)

  db.init_app(app)
  csrf.init_app(app)
  mail.init_app(app)

  # Google oAuth setup
  # oauth = OAuth(app)
  oauth.init_app(app)

  google = oauth.register(
    name='google',
    client_id = app.config['OAUTH2_CLIENT_ID'],
    client_secret = app.config['OAUTH2_CLIENT_SECRET'],
    server_metadata_url = app.config['OAUTH2_META_URL'],
    client_kwargs = {
      "scope": "openid profile email"
    }
  )

  # REMINDER: Only use camel casing, no hyphens etc. flask will flag an error if thats the case.
  # Initialise Routes

  # Main pages
  from .views import views

  app.register_blueprint(views, url_prefix="/")
  
  # Authentication pages
  from .auth import auth
  app.register_blueprint(auth, url_prefix="/")

  # Dashboard pages
  from .dashboard import dashboard
  from .manageOrders import manageOrders
  from .manageTradeins import manageTradeins
  from .customerChat import customerChat
  from .manageProducts import manageProducts
  from .manageVouchers import manageVouchers
  from .manageAccounts import manageAccounts
  
  app.register_blueprint(dashboard, url_prefix="/dashboard")
  app.register_blueprint(manageOrders, url_prefix="/dashboard")
  app.register_blueprint(manageTradeins, url_prefix="/dashboard")
  app.register_blueprint(customerChat, url_prefix="/dashboard")
  app.register_blueprint(manageProducts, url_prefix="/dashboard")
  app.register_blueprint(manageVouchers, url_prefix="/dashboard")
  app.register_blueprint(manageAccounts, url_prefix="/dashboard")

  # Product Pages
  from .productPagination import productPagination

  app.register_blueprint(productPagination, url_prefix="/products")

  # Cart Pages
  from .addToCart import addToCart


  app.register_blueprint(addToCart, url_prefix="/")


  # Initialise Database
  from .models import User, Product, Role, Order, OrderItem, Category, ProductCategory

  create_database(app)

  # User load
  login_manager = LoginManager()
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(id):
    return User.query.get(int(id))

  @app.context_processor
  def inject_user():
    return dict(user=current_user)
  
  # 404, 403, 401 handler
  @app.errorhandler(404)
  def page_not_found(e):
    return render_template('404.html', user=current_user), 404
  
  @app.errorhandler(403)
  def forbidden(e):
    return render_template('403.html', user=current_user), 403

  @app.errorhandler(401)
  def unauthorized(e):
    return render_template('401.html', user=current_user), 401
  
  return app
  
def create_database(app):
  with app.app_context():
    if not path.exists('instance/' + DB_NAME):
      db.create_all()
      print('Created Database!')
      # insert_categories()

      from .seed import insert_categories, add_products, insert_users, insert_default_roles # will remove as time goes, added seed.py to avoid confusion here - nelson
      # Seed is actually what i wanted to add, so this is a nice touch you added - Ben
      insert_default_roles()
      insert_users()
      insert_categories()
      add_products()