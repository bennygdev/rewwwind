# seed.py
from .models import Product, Category, db

def insert_categories():
    category1 = Category(category_name="Music")
    db.session.add(category1)
    db.session.commit()
    print('Inserted categories.')