# seed.py
from .models import Product, Category, db, User
from werkzeug.security import generate_password_hash

def insert_default_roles():
  from .models import Role
  roles = ['Customer', 'Admin', 'Owner']

  for role_name in roles:
    role_exists = Role.query.filter_by(role_name=role_name).first()
    if not role_exists:
      new_role = Role(role_name=role_name)
      db.session.add(new_role)
    
  db.session.commit()
  print('Inserted default roles into the database!')

def insert_users():
  from .models import User
  admin1 = User(
    first_name = "Admin", 
    last_name = "1",
    username = "admin1",
    email = "admin1@gmail.com",
    image = None,
    google_account = False,
    password = generate_password_hash("admin1", method='pbkdf2:sha256'),
    orderCount = 0,
    role_id = 2
  )

  admin2 = User(
    first_name = "Admin", 
    last_name = "2",
    username = "admin2",
    email = "admin2@gmail.com",
    image = None,
    google_account = False,
    password = generate_password_hash("admin2", method='pbkdf2:sha256'),
    orderCount = 0,
    role_id = 2
  )

  owner = User(
    first_name = "Owner", 
    last_name = "3",
    username = "owner",
    email = "owner@gmail.com",
    image = None,
    google_account = False,
    password = generate_password_hash("ownerApp", method='pbkdf2:sha256'),
    orderCount = 0,
    role_id = 3
  )

  users = [
    ("admin1@gmail.com", admin1),
    ("admin2@gmail.com", admin2),
    ("owner@gmail.com", owner)
  ]

  for email, user in users:
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
      db.session.add(user)

  db.session.commit()
  print('Inserted Admin and Owner accounts!')


def insert_categories():
    category1 = Category(category_name="Music")
    db.session.add(category1)
    db.session.commit()
    print('Inserted categories.')

def add_products():
    lorem = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)."
    dummy1 = Product(
                name='dummy 1',
                creator='dummy 1',
                image_thumbnail="media/uploads/dummy1.jpg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 100, 'stock': 1}],
                category_id=1
            )
    dummy2 = Product(
                name='dummy 2',
                creator='dummy 2',
                image_thumbnail="media/uploads/dummy2.jpg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 10, 'stock': 20}],
                category_id=1
            )
    dummy3 = Product(
                name='dummy 3',
                creator='dummy 3',
                image_thumbnail="media/uploads/dummy3.jpeg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 20, 'stock': 5}],
                category_id=1
            )
    dummy4 = Product(
                name='dummy 4',
                creator='dummy 4',
                image_thumbnail="media/uploads/dummy4.jpeg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 50, 'stock': 10}],
                category_id=1
            )
    dummy5 = Product(
                name='dummy 5',
                creator='dummy 5',
                image_thumbnail="media/uploads/dummy5.png",
                description=lorem,
                variants=[{'name': 'standard', 'price': 20, 'stock': 200}],
                category_id=1
            )
    dummies = []
    dummies.extend([dummy1, dummy2, dummy3, dummy4, dummy5])
    for dummy in dummies:
        db.session.add(dummy)
    db.session.commit()