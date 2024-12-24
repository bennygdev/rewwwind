from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

manageTradeins = Blueprint('manageTradeins', __name__)

@manageTradeins.route('/manage-tradeins')
@login_required
@role_required(1, 2, 3)
def manage_tradeins():
  return render_template("dashboard/manageTradeins/tradeins.html", user=current_user)