from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask import request, flash
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, IntegerField, FloatField, FieldList, FormField, SelectField, BooleanField, FileField, MultipleFileField, EmailField, PasswordField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, Regexp, ValidationError
from PIL import Image # file object validator
from mimetypes import guess_type # file extension validator
from .models import User, Category, Product

# Account-related forms
class LoginForm(FlaskForm):
  emailUsername = StringField('Email/Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
  submit = SubmitField('Login')

class RegisterForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired()])
  lastName = StringField('Last Name', validators=[DataRequired()])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Create Account')

class UsernameForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  submit = SubmitField('Proceed')

class RequestResetForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Reset Password')

class UpdatePersonalInformation(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired()])
  lastName = StringField('Last Name') # most wesbites do not need last name
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
  submit = SubmitField('Update')

class ChangePasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Save')

class AdminChangeUserInfoForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired()])
  lastName = StringField('Last Name')
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Update')

class OwnerAddAccountForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired()])
  lastName = StringField('Last Name', validators=[DataRequired()])
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  role_id = IntegerField('Role ID', validators=[DataRequired()])
  submit = SubmitField('Create Account')

class BillingAddressForm(FlaskForm):
  address_one = StringField('Address One', validators=[DataRequired()])
  address_two = StringField('Address Two')
  unit_number = StringField('Unit Number', validators=[DataRequired(), Length(max=15)])
  postal_code = IntegerField('Postal Code', validators=[DataRequired(), NumberRange(min=1, max=999999)])
  phone_number = IntegerField('Phone Number', validators=[DataRequired(), NumberRange(min=60000000, max=99999999)])
  submit = SubmitField('Save')

# New product forms
class ConditionForm(FlaskForm): # specific conditions to be listed in the AddProductForm
  condition = SelectField('Condition', validators=[DataRequired()])
  stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
  price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])

class AddProductForm(FlaskForm):
  productName = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
  productCreator = StringField('Product Creator', validators=[DataRequired(), Length(max=200)])
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
    self.productType.choices = [(category.id, category.category_name) for category in categories]
    self.productGenre.choices = [(category.id, category.category_name) for category in categories]

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