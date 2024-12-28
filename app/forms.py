from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask import request, flash
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, IntegerField, FieldList, FormField, SelectField, FileField, MultipleFileField, EmailField, PasswordField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, Regexp, ValidationError
from PIL import Image # file object validator
from mimetypes import guess_type # file extension validator
from .models import User, Category, Product

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
  lastName = StringField('Last Name', validators=[DataRequired()])
  username = StringField('Username', validators=[DataRequired(), Length(max=15)])
  email = EmailField('Email', validators=[DataRequired(), Email()])
  picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
  submit = SubmitField('Update')

class ChangePasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", message="Password must be at least 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character.")])
  confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
  submit = SubmitField('Save')

class AddProductForm(FlaskForm):
  productName = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
  productImages = MultipleFileField('', render_kw={'accept':'image/*'})
  productThumbnail = HiddenField()
  productDescription = TextAreaField('Product Description')
  productType = SelectField('Type', validators=[DataRequired()])
  productGenre = SelectField('Genre', validators=[DataRequired()])
  
  # populating select choices from sql.
  def process(self, formdata=None, obj=None, data=None, **kwargs):
    categories = Category.query.all()
    self.productType.choices = [(category.id, category.category_name) for category in categories]
    self.productGenre.choices = [(category.id, category.category_name) for category in categories]
    super(AddProductForm, self).process(formdata, obj, data, **kwargs)
  
  # validating images
  def validate_productImages(self, field):
    print('Working.')
    for file in field.data:
      mime_type, _ = guess_type(file.filename)

      if not mime_type or not mime_type.startswith('image/'):
          raise ValidationError('this is not a valid image file.', mime_type)

      image = Image.open(file.stream) 
      if image.verify():
        raise ValidationError('This is not a valid image file.', image)
  
  submit = SubmitField('Add')