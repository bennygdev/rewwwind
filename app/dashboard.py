from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .roleDecorator import role_required
from . import db

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/overview')
@login_required
@role_required(1, 2, 3)
def overview():
  return render_template("dashboard/overview.html", user=current_user)

@dashboard.route('/profile')
@login_required
@role_required(1, 2, 3)
def user_profile():
  return render_template("dashboard/profile/profile.html", user=current_user)

@dashboard.route('/settings')
@login_required
@role_required(1, 2, 3)
def user_settings():
  return render_template("dashboard/settings/settings.html", user=current_user)