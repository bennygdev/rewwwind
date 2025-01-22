from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .models import MailingList
from .roleDecorator import role_required
from . import db

newsletter = Blueprint('newsletter', __name__)
# Newsletter page