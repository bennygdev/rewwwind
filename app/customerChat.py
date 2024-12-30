from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

customerChat = Blueprint('customerChat', __name__)
# Customer chat page

@customerChat.route('/customer-chat')
@login_required
@role_required(2, 3)
def customer_chat():
  return render_template("dashboard/customerChat/customerChat.html", user=current_user)