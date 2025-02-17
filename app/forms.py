from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask import request, flash, session
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from wtforms import StringField, TextAreaField, IntegerField, DateField, FloatField, FieldList, FormField, SelectField, BooleanField, FileField, MultipleFileField, EmailField, PasswordField, RadioField, SelectMultipleField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, Regexp, ValidationError
from PIL import Image # file object validator
from mimetypes import guess_type # file extension validator
from wtforms.validators import Regexp
from .models import User, Category, SubCategory, Product, MailingList, Voucher, Cart, Order, UserVoucher
from datetime import datetime
import re
import json

# Account-related forms
class LoginForm(FlaskForm):
  emailUsername = StringField('Email/Username', validators=[DataRequired(message="Email or username is required")])
  password = PasswordField('Password', validators=[DataRequired(message="Password is required"), Length(min=6)])
  submit = SubmitField('Login')

  def validate_emailUsername(self, field):
    user = User.query.filter((User.email == field.data) | (User.username == field.data)).first()
    if not user:
      raise ValidationError('Invalid email or username')
    elif user.google_account:
      raise ValidationError('Please use Google Sign-In for this account')
        
    # Store the user for password validation
    self.user = user

  def validate_password(self, field):
    if hasattr(self, 'user'):  # Only check if user exists (passed email validation)
      if not check_password_hash(self.user.password, field.data):
        raise ValidationError('Invalid password')

class RegisterForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(message="First name is required")])
  lastName = StringField('Last Name', validators=[DataRequired(message="Last name is required")])
  email = EmailField('Email', validators=[DataRequired(message="Email is required"), Email(message="Please enter a valid email address")])
  password = PasswordField('Password', validators=[DataRequired(message="Password is required"), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Create Account')

  def validate_email(self, field):
    user = User.query.filter_by(email=field.data).first()
    if user:
      raise ValidationError('An account with that email already exists.')

class UsernameForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired(message="Username is required"), Length(max=15, message="Username must be less than 15 characters")])
  submit = SubmitField('Proceed')

  def validate_username(self, field):
    user = User.query.filter_by(username=field.data).first()
    if user:
      raise ValidationError('This username is already taken.')

class RequestResetForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(message="Email is required"), Email(message="Please enter a valid email address")])
  submit = SubmitField('Request Password Reset')

  def validate_email(self, field):
    user = User.query.filter_by(email=field.data).first()
    if not user:
      raise ValidationError('There is no account with that email')
    elif user.google_account:
      raise ValidationError('This email is linked to a Google account. Please sign in with Google')
    self.user = user

class ResetPasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(message="Password is required"), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Reset Password')

  def __init__(self, user, *args, **kwargs):
    super(ResetPasswordForm, self).__init__(*args, **kwargs)
    self.user = user

  def validate_password(self, field):
    if check_password_hash(self.user.password, field.data):
      raise ValidationError("New password cannot be the same as the previous password")

class UpdatePersonalInformation(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(), Length(max=150, message="First name cannot exceed 150 characters.")])
  lastName = StringField('Last Name', validators=[Length(max=150, message="Last name cannot exceed 150 characters.")]) # most wesbites do not need last name
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Only JPG and PNG images are allowed.')])
  submit = SubmitField('Update')

  def validate_username(self, username):
    if username.data != current_user.username:
      user = User.query.filter_by(username=username.data).first()
      if user:
        raise ValidationError("That username is taken. Please choose another one.")

  def validate_picture(self, picture):
    if picture.data:
      try:
        # Attempt to open the image to verify it's valid
        Image.open(picture.data)
      except:
        raise ValidationError("The uploaded file is not a valid image.")

class ChangePasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Save')

  def validate_password(self, password):
    if check_password_hash(current_user.password, password.data):
      raise ValidationError("New password cannot be the same as your current password.")

class ChangeEmailForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Save')

  def validate_email(self, email):
    if email.data == current_user.email:
      raise ValidationError("New email cannot be the same as your current email.")
            
    user = User.query.filter_by(email=email.data).first()
    if user:
      raise ValidationError("This email is already taken. Please try again.")

class AdminChangeUserInfoForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(message="First name is required."), Length(max=150, message="First name cannot exceed 150 characters.")])
  lastName = StringField('Last Name', validators=[Length(max=150, message="Last name cannot exceed 150 characters.")])
  username = StringField('Username', validators=[DataRequired(message="Username is required."), Length(max=15, message="Username cannot exceed 15 characters.")])
  email = EmailField('Email', validators=[DataRequired(message="Email is required."), Email(message="Please enter a valid email address.")])
  submit = SubmitField('Update')

  def __init__(self, original_username, original_email, *args, **kwargs):
    super(AdminChangeUserInfoForm, self).__init__(*args, **kwargs)
    self.original_username = original_username
    self.original_email = original_email

  def validate_username(self, username):
    if username.data != self.original_username:
      user = User.query.filter_by(username=username.data).first()
      if user:
        raise ValidationError("This username is already taken.")

  def validate_email(self, email):
    if email.data != self.original_email:
      user = User.query.filter_by(email=email.data).first()
      if user:
        raise ValidationError("This email address is already registered.")

class OwnerAddAccountForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(message="First name is required."), Length(max=150, message="First name cannot exceed 150 characters.")])
  lastName = StringField('Last Name', validators=[DataRequired(message="Last name is required."), Length(max=150, message="Last name cannot exceed 150 characters.")])
  username = StringField('Username', validators=[DataRequired(message="Username is required."), Length(max=15, message="Username cannot exceed 15 characters.")])
  email = EmailField('Email', validators=[DataRequired(message="Email is required."), Email(message="Please enter a valid email address.")])
  password = PasswordField('Password', validators=[DataRequired(message="Password is required."), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  role_id = IntegerField('Role ID', validators=[DataRequired(message="Please select a role.")])
  submit = SubmitField('Create Account')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError("This username is already taken.")

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
      raise ValidationError("This email address is already registered.")

class SelectDeliveryTypeForm(FlaskForm):
  del_type = RadioField(validators=[DataRequired(message="Please select a delivery method")],
      choices=[
      ('1', 'Self Pick-Up'),
      ('2', 'Standard Local Delivery'),
      ('3', 'Expedited Local Delivery'),
      ('4', 'International Shipping')
      ])


class BillingAddressForm(FlaskForm):
  country = SelectField('Country', choices=[('SG', 'Singapore')], coerce=str, default='SG')
  countryInt = SelectField('Country', 
                        choices = [
    ("AU", "Australia"),
    ("HK", "Hong Kong"),
    ("ID", "Indonesia"),
    ("MY", "Malaysia"),
    ("PH", "Philippines"),
    ("KR", "South Korea"),
    ("TW", "Taiwan"),
    ("TH", "Thailand"),
    ("GB", "United Kingdom"),
    ("US", "United States"),
    ("VN", "Vietnam")
  ],
  default='AU', # def an unavoidable error but i'm gonna waste too much time doing it so i'll leave it for now
  coerce=str
                        )
  address_one = StringField('Address One', validators=[DataRequired(message="Address is required"), Length(min=5, max=255, message="Address must be between 5 and 255 characters")])
  address_two = StringField('Address Two', validators=[Length(max=255, message="Address cannot exceed 255 characters")])
  unit_number = StringField('Unit Number', validators=[DataRequired(), Length(max=15, message="Unit number cannot exceed 15 characters"), Regexp(r'^[A-Za-z0-9-]+$', message="Unit number can only contain letters, numbers, and hyphens")])
  postal_code = StringField('Postal Code', validators=[DataRequired(message="Postal code is required"), Length(min=5, max=6, message="Postal code must be between 5 to 6 digits"), Regexp(r"^[0-9]*$", message="Postal code must contain only numbers.")])
  phone_number = StringField('Phone Number', validators=[DataRequired(message="Phone number is required")])
  submit = SubmitField('Save')
        
  def validate_phone_number(self, field):
    if field.data:
      cleaned_number = ''.join(filter(str.isdigit, field.data))
            
      if not cleaned_number.startswith(('6', '8', '9')):
        raise ValidationError("Phone number must start with 6, 8, or 9")
            
      if len(cleaned_number[2:]) != 8:
        raise ValidationError("Phone number must be 8 digits long")
            
      field.data = cleaned_number

class PickupForm(FlaskForm): # for in-store pickups
  pickup_date = DateField('Pickup Date', validators=[DataRequired(message="Please select a date.")])

  def validate_pickup_date(self, field):
    import datetime
    if field.data:
      if field.data < datetime.date.today():
        raise ValidationError('The date selected is in the past, please try again')

class VoucherSelectForm(FlaskForm): # purely for pre-payment process
  voucher = SelectField('Voucher')

  def process(self, formdata=None, obj=None, data=None, **kwargs):
    super(VoucherSelectForm, self).process(formdata, obj, data, **kwargs)
    
    cart = Cart.query.filter(Cart.user_id==current_user.id).all()
    cart_total = sum(item.quantity * item.product_condition['price'] for item in cart)
    cart_count = sum(item.quantity for item in cart)

    vouchers = Voucher.query.join(UserVoucher).filter(
        UserVoucher.user_id == current_user.id,
        Voucher.is_active == True
    ).all()
        
    eligible_vouchers = []

    for voucher in vouchers:
      is_eligible = True
      show = session['delivery_type']['type']

      # Check if the voucher has been used
      user_voucher = UserVoucher.query.filter(
          UserVoucher.user_id == current_user.id,
          UserVoucher.voucher_id == voucher.id
      ).first()
      
      if user_voucher and user_voucher.is_used:
        # Mark used vouchers as ineligible
        is_eligible = False

      # Check if the voucher has any criteria
      if voucher.criteria:
        for criterion in voucher.criteria:
          if criterion['type'] == 'first_purchase':
            # Check if the user has made any previous purchases
            previous_purchases = Order.query.filter(Order.user_id == current_user.id).count()
            if previous_purchases > 0:
              is_eligible = False
              break
              
          elif criterion['type'] == 'min_cart_amount':
            if cart_total < criterion['value']:
              is_eligible = False
              break
              
          elif criterion['type'] == 'min_cart_items':
            if cart_count < criterion['value']:
              is_eligible = False
              break
          
      if 'SHIP' in voucher.voucher_code.upper() and show == '1':
        is_eligible = False
      # Check eligible categories
      if is_eligible and voucher.eligible_categories:
        # Check if any item in the cart belongs to the eligible categories
        cart_categories = set(item.product.category.category_name for item in cart)
        if not any(category in cart_categories for category in voucher.eligible_categories):
          is_eligible = False
      
      if is_eligible:
        eligible_vouchers.append(voucher)
        
    # Update the voucher field choices with eligible vouchers
    self.voucher.choices = [(0, 'No Voucher')] + [(voucher.id, voucher.voucher_code) for voucher in eligible_vouchers]


class PaymentMethodForm(FlaskForm):
  paymentType_id = RadioField(
    'Select Card Type',
    choices=[
      ('1', 'Visa'),
      ('2', 'Mastercard'),
      ('3', 'American Express')
    ],
    validators=[DataRequired()]
  )
  card_name = StringField('Card Name', validators=[DataRequired(message="Cardholder name is required"), Length(min=2, max=255, message="Name must be between 2 and 255 characters"), Regexp(r'^[A-Za-z\s-]+$', message="Name can only contain letters, spaces, and hyphens")])
  card_number = StringField('Card Number', validators=[DataRequired(message="Card number is required"), Length(min=15, max=16), Regexp(r'^\d+$', message="Card number must contain only numbers")])
  expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired(message="Expiry date is required"), Length(max=5)])
  card_cvv = PasswordField('CVV', validators=[DataRequired(message="CVV is required"), Regexp(r'^\d+$', message="CVV must contain only numbers")])
  submit = SubmitField('Save')

  def get_card_type_from_number(self, card_number):
    # Helper method to detect card type from number
    if card_number.startswith('4'):
      return '1'  # Visa
    elif card_number.startswith(('51', '52', '53', '54', '55')):
      return '2'  # Mastercard
    elif card_number.startswith(('34', '37')):
      return '3'  # Amex
    return None

  def validate_card_number(self, field):
    if not field.data:
        return
            
    card_number = field.data.strip()
    selected_type = self.paymentType_id.data
    detected_type = self.get_card_type_from_number(card_number)
        
    # Validate card number format based on type
    if selected_type == '1':  # Visa
      if not (card_number.startswith('4') and len(card_number) in [13, 16]):
        raise ValidationError('Invalid Visa card number. Must start with 4 and be 13 or 16 digits')
    elif selected_type == '2':  # Mastercard
      if not (card_number.startswith(('51', '52', '53', '54', '55')) and len(card_number) == 16): 
        raise ValidationError('Invalid Mastercard number. Must start with 51-55 and be 16 digits')
    elif selected_type == '3':  # Amex
      if not (card_number.startswith(('34', '37')) and len(card_number) == 15):
        raise ValidationError('Invalid American Express card number. Must start with 34 or 37 and be 15 digits')

    # Check if card type matches selected type
    if detected_type and detected_type != selected_type:
      card_types = {
        '1': 'Visa',
        '2': 'Mastercard',
        '3': 'American Express'
      }
      detected_name = card_types.get(detected_type, 'Unknown')
      raise ValidationError(f'This appears to be a {detected_name} card number. Please select the correct card type')
    
  def validate_expiry_date(self, field):
    if not field.data:
      return
            
    if not re.match(r'^\d{2}/\d{2}$', field.data):
      raise ValidationError('Expiry date must be in MM/YY format')
            
    month, year = field.data.split('/')
    try:
      month = int(month)
      year = int('20' + year)  # Convert to full year
    except ValueError:
      raise ValidationError('Expiry date must contain valid numbers')
        
    # Validate month range
    if not 1 <= month <= 12:
      raise ValidationError('Month must be between 01 and 12')
        
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
        
    # Validate expiration
    if year < current_year or (year == current_year and month < current_month):
      raise ValidationError('Card has expired')
        
    # Validate future date
    if year > current_year + 10:
      raise ValidationError('Expiry date too far in the future')

  def validate_card_cvv(self, field):
    if not field.data:
      return

    payment_type = self.paymentType_id.data
    cvv = field.data.strip()

    if payment_type == '3':  # American Express
      if len(cvv) != 4:
        raise ValidationError('American Express cards require a 4-digit CVV')
    else:  # Visa and Mastercard
      if len(cvv) != 3:
        if len(cvv) == 4:
          raise ValidationError('Please enter a 3-digit CVV for this card type')
        else:
          raise ValidationError('Please enter a valid 3-digit CVV')

# New product forms
class ConditionForm(FlaskForm): # specific conditions to be listed in the AddProductForm
  condition = SelectField('Condition', validators=[DataRequired()])
  stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=1)])
  price = FloatField('Price', validators=[DataRequired(), NumberRange(min=1)])

class AddProductForm(FlaskForm):
  productName = StringField('Product Name', validators=[DataRequired(), Length(max=200, min=2)])
  productCreator = StringField('Product Creator', validators=[DataRequired(), Length(max=200, min=2)])
  productImages = MultipleFileField('', render_kw={'accept':'image/*'})
  productThumbnail = HiddenField()
  productDescription = TextAreaField('Product Description')
  productType = SelectField('Type', validators=[DataRequired()])
  productGenre = SelectField('Genre', validators=[DataRequired()])
  productIsFeaturedSpecial = BooleanField()
  productIsFeaturedStaff = BooleanField()
  productConditions = FieldList(FormField(ConditionForm), min_entries=1)

  images = HiddenField('images') # purely for update product
  
  submit = SubmitField('Add Product')

  def process(self, formdata=None, obj=None, data=None, **kwargs):
    super(AddProductForm, self).process(formdata, obj, data, **kwargs)

  
    # populating product select choices from sql.
    categories = Category.query.all()
    subcategories = SubCategory.query.filter(SubCategory.category_id==1).all()
    self.productType.choices = [(category.id, category.category_name) for category in categories]
    self.productGenre.choices = [(subcategory.id, subcategory.subcategory_name) for subcategory in subcategories]

    # populating condition select choices
    condition_choices = [
        ('Brand New', 'Brand New'),
        ('Like New', 'Like New'),
        ('Lightly Used', 'Lightly Used'),
        ('Well Used', 'Well Used')
    ]
    if self.productConditions.entries:
      for condition_form in self.productConditions.entries:  # Use entries to access each form
          condition_form.form.condition.choices = condition_choices
  
  # validating images
  def validate_productImages(self, field):
    for file in field.data:
        if file and not isinstance(file, str):
          # Check mime type and extension
          mime_type, _ = guess_type(file.filename)
          extension = secure_filename(file.filename).split('.')[-1].lower()
          if not mime_type or not str(mime_type).startswith('image/') and extension not in ['jpg', 'jpeg', 'png']: # prob overkill with extension but might as well i guess?
              raise ValidationError('The submitted image was not valid image file. Please submit an image file with .jpg, .jpeg, or .png extensions.')

          # pillow corruption verification
          try:
              image = Image.open(file.stream)
              image.verify()
          except (IOError, SyntaxError):
              raise ValidationError('The image file could not be submitted. Please check if the image file is corrupted, and submit a different file if so.')
          

# SHELVE FUNCTIONALITY PURELY FOR ADDPRODUCTFORM, other logic found in manageProducts.save_product_form route, and also the most bottom of addProduct.js
class AddProductFormData:
  def __init__(self, name, creator, description, type, genre, conditions, featured_special, featured_staff):
    self.__name = name
    self.__creator = creator
    self.__description = description
    self.__type = type
    self.__genre = genre
    self.__conditions = conditions
    self.__featured_special = featured_special
    self.__featured_staff = featured_staff
  
  def to_dict(self):
    return {
        "name": self.__name,
        "creator": self.__creator,
        "description": self.__description,
        "type": self.__type,
        "genre": self.__genre,
        "featured_special": self.__featured_special,
        "featured_staff": self.__featured_staff
    }
  
  def get_name(self):
    return self.__name
  def set_name(self, name):
    self.__name = name
  
  def get_creator(self):
    return self.__creator
  def set_creator(self, creator):
    self.__creator = creator
  
  def get_description(self):
    return self.__description
  def set_description(self, description):
    self.__description = description
  
  def get_type(self):
    return self.__type
  def set_type(self, type):
    self.__type = type
  
  def get_genre(self):
    return self.__genre
  def set_genre(self, genre):
    self.__genre = genre
  
  def get_conditions(self):
    return self.__conditions
  def set_conditions(self, conditions):
    self.__conditions = conditions
  
  def get_featured_special(self):
    return self.__featured_special
  def set_featured_special(self, featured_special):
    self.__featured_special = featured_special
  
  def get_featured_staff(self):
    return self.__featured_staff
  def set_featured_staff(self, featured_staff):
    self.__featured_staff = featured_staff

class DeleteProductForm(FlaskForm):
  productID = HiddenField()
  deleteConfirm = StringField('Enter the text shown to confirm deletion', validators=[DataRequired()])
  submit = SubmitField('Delete this product')

  def validate_deleteConfirm(self, field):
    if field.data != 'CONFIRMDELETE':
       raise ValidationError('The confirmation input is invalid. Please type CONFIRMDELETE to confirm the deletion.')

class AddReviewForm(FlaskForm):
  rating = HiddenField('Rating:')
  show_username = BooleanField('Show username', default=True)
  description = TextAreaField()
  
  submit = SubmitField('Post Review')

  def validate_rating(self, field):
    if not field.data:
      raise ValidationError('Please select a rating to give this product.')

class DeleteReviewForm(FlaskForm):
  deleteConfirm = StringField('Please enter the text shown below to confirm deletion.', validators=[DataRequired()])
  submit = SubmitField('Delete Review')

  def validate_deleteConfirm(self, field):
    if field.data != 'CONFIRMDELETE':
       raise ValidationError('The confirmation input is invalid. Please type CONFIRMDELETE to confirm the deletion.')

# Order-related Forms
class UpdateOrderForm(FlaskForm):
  approved = RadioField('Approve Order', choices=['Approved', 'Not Approved'], default='Not Approved')
  submit = SubmitField('Update Approval')

# Cart-related Forms
class AddToCartForm(FlaskForm):
  condition = HiddenField(default=0)
  quantity = IntegerField('Quantity')
  submit = SubmitField('Add to Cart')

#Trade-in form stuff
class TradeItemForm(FlaskForm):
    item_type = SelectField('Item Type', choices=[
      ('book', 'Book'), ('vinyl', 'Vinyl')
      ], validators=[DataRequired()])
    
    item_condition = SelectField('Item Condition', choices=[
        ('brandNew', 'Brand New'),
        ('likeNew', 'Like New'),
        ('lightlyUsed', 'Lightly Used'),
        ('used', 'Used')
    ], validators=[DataRequired()])

    images = FileField('Images', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files are allowed.')])
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=255, message="Title must be at least 3 characters.")])
    author = StringField('Author / Artist', validators=[DataRequired(), Length(min=3, max=255, message="Author must be at least 3 characters.")])
    genre = StringField('Genre', validators=[DataRequired(), Length(min=3, max=255, message="Genre must be at least 3 characters.")])

    isbn = StringField('ISBN / Cat#', validators=[
        DataRequired(),
        Regexp(r"^\d{13}$", message="ISBN must be exactly 13 digits (numbers only).")  
    ])
    
    submit = SubmitField('Submit')
    
class VoucherForm(FlaskForm):
  code = StringField('Voucher Code', validators=[DataRequired(), Length(min=3, max=50), Regexp(r'^[A-Za-z0-9_-]*$', message="Voucher code can only contain letters, numbers, underscores and dashes")])
  description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
  voucher_type = SelectField('Voucher Type', choices=[
    ('percentage', 'Percentage Discount'),
    ('fixed_amount', 'Fixed Amount Off'),
    ('free_shipping', 'Free Shipping')
  ], validators=[DataRequired()])
  discount_value = FloatField('Discount Value', validators=[Optional(), NumberRange(min=0)])
    
  # Criteria fields
  criteria_json = StringField('Voucher Criteria')
  # min_cart_amount = FloatField('Minimum Cart Amount', validators=[Optional(), NumberRange(min=0)])
  # min_cart_items = IntegerField('Minimum Cart Items', validators=[Optional(), NumberRange(min=1)])
  # first_purchase_only = BooleanField('First Purchase Only')
  eligible_categories = SelectMultipleField('Eligible Categories', 
    choices=[
      ('Vinyl', 'Vinyl'),
      ('Book', 'Book')
    ],
    validators=[DataRequired(message="Please select at least one category")]
  )
    
  expiry_days = SelectField('Expiry Period', choices=[
    (7, '7 Days'),
    (14, '14 Days'),
    (30, '30 Days'),
    (60, '60 Days'),
    (90, '90 Days')
  ], coerce=int, validators=[DataRequired(message="Expiry day is required")])

  is_active = RadioField('Voucher Status', choices=[
    ('True', 'Active'),
    ('False', 'Not Active')
  ], default='True', validators=[DataRequired(message="Please select one voucher status")])

  submit = SubmitField('Create Voucher')
    
  def __init__(self, *args, **kwargs):
    super(VoucherForm, self).__init__(*args, **kwargs)
    # Populate categories dynamically
    self.eligible_categories.choices = [
      ('Vinyl', 'Vinyl'),
      ('Book', 'Book')
    ]
    
  def validate_code(self, field):
    if Voucher.query.filter_by(voucher_code=field.data).first():
      raise ValidationError('This voucher code is already in use.')
    
    if not re.match(r'^[A-Za-z0-9_-]*$', field.data):
      raise ValidationError('Voucher code can only contain letters, numbers, underscores and dashes')

  def validate_description(self, field):
    if len(field.data) > 1000:
        raise ValidationError('Description cannot exceed 1000 characters.')

  def validate_discount_value(self, field):
    try:
      value = float(field.data)
    except (TypeError, ValueError):
      raise ValidationError('Discount value must be a number')

    if self.voucher_type.data == 'percentage':
      if not 0 <= field.data <= 100:
        raise ValidationError('Percentage discount must be between 0 and 100')
    elif self.voucher_type.data == 'fixed_amount':
      if field.data <= 0:
        raise ValidationError('Fixed amount discount must be greater than 0')
    elif self.voucher_type.data == 'free_shipping':
      field.data = 0  # No discount value needed for free shipping

  def validate_eligible_categories(self, field):
    if not field.data:
      raise ValidationError('Please select at least one eligible category.')

  def validate_criteria_json(self, field):
    if not field.data or field.data == '[]':
      raise ValidationError('Please add at least one voucher criteria.')

class EditVoucherForm(FlaskForm):
  code = StringField('Voucher Code', validators=[DataRequired(), Length(min=3, max=50), Regexp(r'^[A-Za-z0-9_-]*$', message="Voucher code can only contain letters, numbers, underscores and dashes")])
  description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
  voucher_type = SelectField('Voucher Type', choices=[
    ('percentage', 'Percentage Discount'),
    ('fixed_amount', 'Fixed Amount Off'),
    ('free_shipping', 'Free Shipping')
  ], validators=[DataRequired()])
  discount_value = FloatField('Discount Value', validators=[Optional(), NumberRange(min=0)])
    
  # Criteria fields
  criteria_json = StringField('Voucher Criteria')
  # min_cart_amount = FloatField('Minimum Cart Amount', validators=[Optional(), NumberRange(min=0)])
  # min_cart_items = IntegerField('Minimum Cart Items', validators=[Optional(), NumberRange(min=1)])
  # first_purchase_only = BooleanField('First Purchase Only')
  eligible_categories = SelectMultipleField('Eligible Categories', 
    choices=[
      ('Vinyl', 'Vinyl'),
      ('Book', 'Book')
    ],
    validators=[DataRequired(message="Please select at least one category")]
  )
    
  expiry_days = SelectField('Expiry Period', choices=[
    (7, '7 Days'),
    (14, '14 Days'),
    (30, '30 Days'),
    (60, '60 Days'),
    (90, '90 Days')
  ], coerce=int, validators=[DataRequired(message="Expiry day is required")])

  is_active = RadioField('Voucher Status', choices=[
    ('True', 'Active'),
    ('False', 'Not Active')
  ], default='True', validators=[DataRequired(message="Please select one voucher status")])

  submit = SubmitField('Create Voucher')
    
  def __init__(self, voucher_id, *args, **kwargs):
    super(EditVoucherForm, self).__init__(*args, **kwargs)
    # Populate categories dynamically
    self.eligible_categories.choices = [
      ('Vinyl', 'Vinyl'),
      ('Book', 'Book')
    ]
    self.voucher_id = voucher_id
    
  def validate_code(self, field):
    existing_voucher = Voucher.query.filter_by(voucher_code=field.data).first()
    if existing_voucher and existing_voucher.id != self.voucher_id:
      raise ValidationError('This voucher code is already in use.')
        
    if not re.match(r'^[A-Za-z0-9_-]*$', field.data):
      raise ValidationError('Voucher code can only contain letters, numbers, underscores and dashes')

  def validate_description(self, field):
    if len(field.data) > 1000:
        raise ValidationError('Description cannot exceed 1000 characters.')

  def validate_discount_value(self, field):
    try:
      value = float(field.data)
    except (TypeError, ValueError):
      raise ValidationError('Discount value must be a number')

    if self.voucher_type.data == 'percentage':
      if not 0 <= field.data <= 100:
        raise ValidationError('Percentage discount must be between 0 and 100')
    elif self.voucher_type.data == 'fixed_amount':
      if field.data <= 0:
        raise ValidationError('Fixed amount discount must be greater than 0')
    elif self.voucher_type.data == 'free_shipping':
      field.data = 0  # No discount value needed for free shipping

  def validate_eligible_categories(self, field):
    if not field.data:
      raise ValidationError('Please select at least one eligible category.')

  def validate_criteria_json(self, field):
    if not field.data or field.data == '[]':
      raise ValidationError('Please add at least one voucher criteria.')

class VoucherGiftForm(FlaskForm):
  user_id = HiddenField('User ID', 
    validators=[DataRequired(message="Please select a user")]
    )
    
  voucher_id = HiddenField('Voucher ID',
    validators=[DataRequired(message="Please select a voucher")]
  )
    
  submit = SubmitField('Gift Voucher')
    
  def validate_user_id(self, field):
    user = User.query.get(field.data)
    if not user or user.role_id != 1:  # Ensure user exists and is a customer
      raise ValidationError('Invalid user selected.')
            
  def validate_voucher_id(self, field):
    voucher = Voucher.query.get(field.data)
    if not voucher or not voucher.is_active:
      raise ValidationError('Selected voucher is not active or does not exist.')
    
class MailingListForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Email(message="Please enter a valid email address.")])
  submit = SubmitField('Subscribe')

  def validate_email(self, field):
    existing_email = MailingList.query.filter_by(email=field.data).first()
    if existing_email:
      raise ValidationError('This email is already subscribed to our newsletter.')
    
class NewsletterForm(FlaskForm):
  title = StringField('Newsletter Title', validators=[DataRequired(message='Title is required'), Length(min=5, max=100, message='Title must be between 5 and 100 characters')])
  description = TextAreaField('Newsletter Content', validators=[DataRequired(message='Newsletter content is required'), Length(min=20, max=2000, message='Content must be between 20 and 2000 characters')])
  submit = SubmitField('Send Newsletter')

class ShippingPaymentForm(FlaskForm):
    shipping_option = RadioField(
        'Shipping Option',
        choices=[
            ('Mail-in', 'Mail-in'),
            ('In-Store Drop-off', 'In-Store Drop-off'),
            ('Pick-Up Service', 'Pick-Up Service (Shipping: $5.00)')
        ],
        validators=[DataRequired(message="Please select a shipping option.")]
    )

    tracking_number = StringField(
        'Tracking Number',
        validators=[Length(min=3, max=50, message="Tracking number must be between 3 and 50 characters.")]
    )

    street_address = StringField(
        'Street Address',
        validators=[Length(min=5, max=255, message="Address must be between 5 and 255 characters.")]
    )

    house_block = StringField(
        'House / Block No.',
        validators=[Length(min=1, max=50, message="House/Block number cannot exceed 50 characters.")]
    )

    zip_code = StringField(
        'Zip or Postal Code',
        validators=[Regexp(r"^\d{5,6}$", message="Postal code must be 5 or 6 digits.")]
    )

    contact_number = StringField(
        'Contact Number',
        validators=[Regexp(r"^\d{8,15}$", message="Contact number must be between 8 and 15 digits.")]
    )

    card_number = StringField(
        'Card Number',
        validators=[DataRequired(message="Card number is required"), Regexp(r"^\d{15,16}$", message="Card number must be 15 or 16 digits.")]
    )

    card_expiry = StringField(
        'Expiration Date (MM/YY)',
        validators=[DataRequired(message="Expiration date is required"), Regexp(r"^(0[1-9]|1[0-2])\/\d{2}$", message="Expiration date must be in MM/YY format.")]
    )

    card_name = StringField(
        'Name on Card',
        validators=[DataRequired(message="Cardholder name is required"), Length(min=2, max=255, message="Name must be between 2 and 255 characters.")]
    )

    submit = SubmitField('Submit')

    def validate(self, extra_validators=None):
        """ Custom validation method to dynamically enforce required fields """
        rv = FlaskForm.validate(self, extra_validators)  # Run base validation first
        if not rv:
            return False  # Stop if base validation fails

        # Only validate tracking number if 'Mail-in' is selected
        if self.shipping_option.data == "Mail-in" and not self.tracking_number.data:
            self.tracking_number.errors.append("Tracking number is required for Mail-in shipping.")
            return False

        # Only validate address fields if 'Pick-Up Service' is selected
        if self.shipping_option.data == "Pick-Up Service":
            required_fields = [
                (self.street_address, "Street address is required for Pick-Up Service."),
                (self.house_block, "House / Block number is required for Pick-Up Service."),
                (self.zip_code, "Zip code is required for Pick-Up Service."),
                (self.contact_number, "Contact number is required for Pick-Up Service.")
            ]
            for field, error_msg in required_fields:
                if not field.data:
                    field.errors.append(error_msg)
                    return False

        return True  # If no validation errors, return True