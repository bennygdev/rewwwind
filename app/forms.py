from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, FieldList, FormField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, Regexp

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
  username = StringField('Username', validators=[DataRequired()])
  submit = SubmitField('Proceed')