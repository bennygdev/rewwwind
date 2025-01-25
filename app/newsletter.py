from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from flask_mail import Message
from .models import MailingList, MailingPost
from .forms import NewsletterForm
from .roleDecorator import role_required
from . import db, mail
from math import ceil
from dotenv import load_dotenv
import os

load_dotenv()

newsletter = Blueprint('newsletter', __name__)
# Newsletter page

def send_newsletter(form):
  mailing_list = MailingList.query.all()
  mailing_count = MailingList.query.count()
    
  recipients = [subscriber.email for subscriber in mailing_list]
    
  if not recipients or mailing_count == 0:
    flash('No subscribers in the mailing list.', 'error')
    return False
    
  try:
    # Create message
    msg = Message(
      subject=form.title.data, 
      sender=('Rewwwind', 'rewwwindmail@gmail.com'),
      bcc=recipients,
      body=form.description.data
    )

    # Send message
    mail.send(msg)
    flash('Newsletter sent successfully!', 'success')
    return True
  except Exception as e:
    current_app.logger.error(f"Newsletter sending failed: {str(e)}")
    flash('Failed to send newsletter. Please try again.', 'error')
    return False

@newsletter.route('/newsletter', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def newsletter_page():
  form = NewsletterForm()
  subscribers_count = MailingList.query.count()
  
  # Pagination and search
  page = request.args.get('page', 1, type=int)
  per_page = 10
    
  # Search logic
  search_query = request.args.get('q', '', type=str)
  if search_query:
    subscribers_query = MailingList.query.filter(MailingList.email.ilike(f"%{search_query}%"))
  else:
    subscribers_query = MailingList.query
    
  # Pagination
  total_subscribers = subscribers_query.count()
  subscribers = subscribers_query.order_by(MailingList.id).paginate(page=page, per_page=per_page)
  total_pages = ceil(total_subscribers / per_page)

  posts_count = MailingPost.query.count()
  recent_posts = MailingPost.query.order_by(MailingPost.created_at.desc()).limit(5).all()
    
  if form.validate_on_submit():
    if send_newsletter(form):

      mailingPost = MailingPost(
        title=form.title.data,
        description=form.description.data
      )

      db.session.add(mailingPost)
      try:
        db.session.commit()
        return redirect(url_for('newsletter.newsletter_page'))
      except Exception as e: # debug
        print(e)
        db.session.rollback()
        flash('An error occurred while creating the post.', 'error')

      return redirect(url_for('newsletter.newsletter_page'))

  return render_template(
    "dashboard/newsletter/newsletter.html", 
    user=current_user, 
    form=form, 
    subscribers=subscribers, 
    posts_count=posts_count, 
    recent_posts=recent_posts, 
    total_pages=total_pages, 
    current_page=page, 
    search_query=search_query,
    subscribers_count=subscribers_count
  )

@newsletter.route('/newsletter/delete-subscriber/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def delete_subscriber(id):
  selected_subscriber = MailingList.query.get_or_404(id)

  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  if selected_subscriber:
    db.session.delete(selected_subscriber)
    db.session.commit()
    flash("Subscriber deleted.", "success")
    return redirect(url_for('newsletter.newsletter_page'))
  else:
    flash("Invalid subscriber or unauthorized access.", "error")
    return redirect(url_for('newsletter.newsletter_page'))
  
  
@newsletter.route('/newsletter/post/<int:id>', methods=['GET'])
@login_required
@role_required(2, 3)
def newsletter_post_content(id):
  post = MailingPost.query.get_or_404(id)

  return render_template("dashboard/newsletter/newsletter_postContent.html", user=current_user, post=post)

@newsletter.route('/newsletter/all-posts', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def newsletter_all_posts():
    posts = MailingPost.query.order_by(MailingPost.created_at.desc()).all()

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # search logic
    search_query = request.args.get('q', '', type=str)

    if search_query:
      posts_query = MailingPost.query.filter(MailingPost.title.ilike(f"%{search_query}%"))
    else:
      posts_query = MailingPost.query

    # pagination logic
    total_posts = posts_query.count()
    posts = posts_query.order_by(MailingPost.created_at.desc()).paginate(page=page, per_page=per_page)

    total_pages = ceil(total_posts / per_page)

    return render_template("dashboard/newsletter/newsletter_posts.html", posts=posts, total_pages=total_pages, current_page=page, search_query=search_query)

@newsletter.route('/newsletter/delete-post/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(2, 3)
def delete_post(id):
  selected_post = MailingPost.query.get_or_404(id)

  if current_user.role_id == 1: # restrict customer functions
    abort(404)

  if selected_post:
    db.session.delete(selected_post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for('newsletter.newsletter_all_posts'))
  else:
    flash("Invalid subscriber or unauthorized access.", "error")
    return redirect(url_for('newsletter.newsletter_all_posts'))