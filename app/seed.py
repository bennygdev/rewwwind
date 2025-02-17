# seed.py
from .models import Product, Category, SubCategory, Order, OrderItem, PaymentInformation, BillingAddress, db, User, Voucher, VoucherType, UserVoucher, Review
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

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

# Real users
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

  customer = User(
    stripe_id = 'cus_RgCvkhikneQdWk',
     first_name = "Customer",
     last_name = "4",
     username = "Customer",
     email = "customer@gmail.com",
     image = None,
     google_account = False,
     password = generate_password_hash("customer", method='pbkdf2:sha256'),
     orderCount = 0,
     role_id = 1
  )

  clean_customer = User(
    first_name = "dummy",
    last_name = "5",
    username = "dummy",
    email = "dummy@gmail.com",
    image = None,
    google_account = False,
    password = generate_password_hash("testtest", method='pbkdf2:sha256'),
    orderCount = 0,
    role_id = 1
  )

  users = [
    ("admin1@gmail.com", admin1),
    ("admin2@gmail.com", admin2),
    ("owner@gmail.com", owner),
    ("customer@gmail.com", customer),
    ("dummy@gmail.com", clean_customer)
  ]

  for email, user in users:
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
      db.session.add(user)

  db.session.commit()
  print('Inserted Customer, Admin and Owner accounts!')

def insert_payment_types():
  from .models import PaymentType
  payment_types = ['Visa', 'Mastercard', 'American Express']

  for type in payment_types:
    types_exists = PaymentType.query.filter_by(payment_type=type).first()
    if not types_exists:
      new_method = PaymentType(payment_type=type)
      db.session.add(new_method)
    
  db.session.commit()
  print('Inserted payment types into the database!')

# Dummy users
def insert_dummy_users():
  first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah", "Michael", "Sarah", "David", "Emily", "Matthew", "Rebecca", "Jason", "Olivia", "Daniel", "Sophia"]
  last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Thompson", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia"]
    
  # Date range (June 2024 - Feb 2025)
  start_date = datetime(2024, 6, 1)
  end_date = datetime(2025, 2, 28)
    
  for i in range(20):
    # Generate a random date within the range
    random_days = random.randint(0, (end_date - start_date).days)
    signup_date = start_date + timedelta(days=random_days)
        
    username = f"{first_names[i].lower()}{random.randint(100, 999)}"
    email = f"{username}@example.com"
        
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
      new_user = User(
        first_name=first_names[i],
        last_name=last_names[i],
        username=username,
        email=email,
        image=None,
        google_account=False,
        password=generate_password_hash(f"password{i+1}", method='pbkdf2:sha256'),
        orderCount=random.randint(0, 5),
        role_id=1,
        created_at=signup_date,
        updated_at=signup_date
      )
      db.session.add(new_user)
    
  db.session.commit()
  print('Inserted 20 dummy users!')

def insert_categories():
    categories = []
    category1 = Category(category_name="Vinyl")
    category2 = Category(category_name="Book")
    categories.extend([category1, category2])
    for category in categories:
       db.session.add(category)
    db.session.commit()
    print('Inserted categories.')

def insert_subcategories():
  vinyl_subcategories = [
    "Rock",
    "Psychedelic", 
    "Pop",
    "Jazz",
    "Classical",
    "Hip Hop",
    "Electronic",
    "Blues",
    "Country",
    "Soul",
    "Reggae",
    "Punk",
    "Metal",  
    "Hard Rock", 
    "Indie",
    "Soundtracks",
    "Folk",
    "Experimental",     
    "Concept Album",         
    "Compilation" 
  ]
  for sub in vinyl_subcategories:
    new_sub = SubCategory(
       subcategory_name = sub,
       category_id = 1
    )
    db.session.add(new_sub)
    db.session.commit()

  book_subcategories = [
    "Fiction",
    "Non-Fiction",
    "Mystery/Thriller",
    "Science Fiction",
    "Dystopian",
    "Fantasy",
    "Adventure",
    "Romance",
    "Biography",
    "Self-Help",
    "History",
    "Science",
    "Poetry",
    "Young Adult",
    "Children's Books",
    "Graphic Novels",
    "Cookbooks",
    "Travel"
  ]
  for sub in book_subcategories:
    new_sub = SubCategory(
       subcategory_name = sub,
       category_id = 2
    )
    db.session.add(new_sub)
    db.session.commit()
  print("Added subcategories.")

def insert_products():
  vinyl_products = [
      {
          "name": "Abbey Road",
          "creator": "The Beatles",
          "description": "Abbey Road is the eleventh studio album by the English rock band the Beatles, released on 26 September 1969, by Apple Records. It is the last album the group recorded, although Let It Be (1970) was the last album completed before the band's break-up in April 1970. It was mostly recorded in April, July, and August 1969, and topped the record charts in both the United States and the United Kingdom. A double A-side single from the album, 'Something' / 'Come Together', was released in October, which also topped the charts in the US.",
          "image_thumbnail": "abbey_road.png",
          "images": ["abbey_road.png", "abbey_road_vinyl_only.png", "abbey_road_vinyl.png"],
          "conditions": [{"condition": 'Brand New', "price": 100, "stock": 10},
                         {"condition": 'Like New', "price": 80, "stock": 20},
                         {"condition": 'Lightly Used', "price": 60, "stock": 30},
                         {"condition": 'Well Used', "price": 40, "stock": 20}],
          "is_featured_special": True,
          "is_featured_staff": False,
          "category_id": 1,
          "subcategories": ["Rock", "Pop"]
      },
      {
          "name": "Kind of Blue",
          "creator": "Miles Davis",
          "description": "Kind of Blue is a studio album by the American jazz trumpeter and composer Miles Davis. It was released on August 17, 1959 through Columbia Records. For the recording, Davis led a sextet featuring saxophonists John Coltrane and Julian 'Cannonball' Adderley, pianist Bill Evans, bassist Paul Chambers, and drummer Jimmy Cobb, with new band pianist Wynton Kelly appearing on one track—'Freddie Freeloader'—instead of Evans. The album was recorded in two sessions on March 2 and April 22, 1959, at Columbia's 30th Street Studio in New York City.",
          "image_thumbnail": "kind_of_blue.png",
          "images": ['kind_of_blue.png', 'kind_of_blue_vinyl.png', 'kind_of_blue_vinyl_only.png'],
          "conditions": [{"condition": 'Brand New', "price": 100, "stock": 10},
                         {"condition": 'Like New', "price": 80, "stock": 20},
                         {"condition": 'Lightly Used', "price": 60, "stock": 30},
                         {"condition": 'Well Used', "price": 40, "stock": 20}],
          "is_featured_special": False,
          "is_featured_staff": True,
          "category_id": 1,  # Vinyl
          "subcategories": ["Jazz", "Classical"]  # Link to these subcategories
      },
      {
        "name": "The Dark Side of the Moon",
        "creator": "Pink Floyd",
        "description": "The Dark Side of the Moon is the eighth studio album by the English rock band Pink Floyd. It was released on 1 March 1973 by Harvest Records. The album explores themes of conflict, greed, time, and mental illness.",
        "image_thumbnail": "the_dark_side_of_the_moon.png",
        "images": ['the_dark_side_of_the_moon.png', 'the_dark_side_of_the_moon_vinyl.png'],
        "conditions": [{"condition": 'Brand New', "price": 120, "stock": 5},
                       {"condition": 'Like New', "price": 90, "stock": 15},
                       {"condition": 'Lightly Used', "price": 70, "stock": 20},
                       {"condition": 'Well Used', "price": 50, "stock": 10}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 1,
        "subcategories": ["Rock", "Psychedelic"]
      },
      {
        "name": "The Wall",
        "creator": "Pink Floyd",
        "description": "The Wall is a rock opera by the English rock band Pink Floyd, released as the band's eleventh studio album on 30 November 1979. The album deals with themes of isolation and personal struggle.",
        "image_thumbnail": "the_wall.png",
        "images": ["the_wall.png"],
        "conditions": [{"condition": 'Brand New', "price": 110, "stock": 8},
                      {"condition": 'Like New', "price": 85, "stock": 12},
                      {"condition": 'Lightly Used', "price": 65, "stock": 25},
                      {"condition": 'Well Used', "price": 45, "stock": 10}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 1,
        "subcategories": ["Rock", "Concept Album"]
      },
      {
        "name": "Revolver",
        "creator": "The Beatles",
        "description": "Revolver is the seventh studio album by the English rock band the Beatles, released on 5 August 1966. The album is known for its innovative use of studio techniques and exploration of new musical styles.",
        "image_thumbnail": "revolver.png",
        "images": ['revolver.png'],
        "conditions": [{"condition": 'Brand New', "price": 90, "stock": 10},
                      {"condition": 'Like New', "price": 70, "stock": 20},
                      {"condition": 'Lightly Used', "price": 50, "stock": 30},
                      {"condition": 'Well Used', "price": 30, "stock": 15}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 1,
        "subcategories": ["Rock", "Pop"]
      },
      {
        "name": "Back in Black",
        "creator": "AC/DC",
        "description": "Back in Black is the seventh studio album by Australian rock band AC/DC, released on 25 July 1980. It is the band's first album with vocalist Brian Johnson and is widely considered one of the greatest albums of all time.",
        "image_thumbnail": "back_in_black.png",
        "images": ['back_in_black.png'],
        "conditions": [{"condition": 'Brand New', "price": 100, "stock": 15},
                      {"condition": 'Like New', "price": 75, "stock": 25},
                      {"condition": 'Lightly Used', "price": 55, "stock": 35},
                      {"condition": 'Well Used', "price": 35, "stock": 20}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 1,
        "subcategories": ["Rock", "Hard Rock"]
      },
      {
        "name": "The Best of Miles Davis",
        "creator": "Miles Davis",
        "description": "A collection of some of the best works by Miles Davis, including his early jazz compositions and later experiments in fusion. Released in 1980, this album showcases his versatility and influence in modern music.",
        "image_thumbnail": "the_best_of_miles_davis.png",
        "images": ['the_best_of_miles_davis.png'],
        "conditions": [{"condition": 'Brand New', "price": 80, "stock": 10},
                      {"condition": 'Like New', "price": 60, "stock": 20},
                      {"condition": 'Lightly Used', "price": 45, "stock": 30},
                      {"condition": 'Well Used', "price": 30, "stock": 15}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 1,
        "subcategories": ["Jazz", "Compilation"]
      },
      {
        "name": "Electric Ladyland",
        "creator": "Jimi Hendrix",
        "description": "Electric Ladyland is the third and final studio album by the Jimi Hendrix Experience, released on October 16, 1968. The album is often regarded as one of the greatest albums of all time, blending rock, blues, and psychedelia.",
        "image_thumbnail": "electric_ladyland.png",
        "images": ['electric_ladyland.png'],
        "conditions": [{"condition": 'Brand New', "price": 120, "stock": 8},
                      {"condition": 'Like New', "price": 95, "stock": 10},
                      {"condition": 'Lightly Used', "price": 70, "stock": 18},
                      {"condition": 'Well Used', "price": 50, "stock": 12}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 1,
        "subcategories": ["Rock", "Psychedelic"]
      },
      {
        "name": "Let It Be",
        "creator": "The Beatles",
        "description": "Let It Be is the twelfth and final studio album by the Beatles, released in 1970. The album captures the band's struggles during their breakup, with many songs having been recorded in chaotic circumstances.",
        "image_thumbnail": "let_it_be.png",
        "images": ['let_it_be.png'],
        "conditions": [{"condition": 'Brand New', "price": 100, "stock": 5},
                       {"condition": 'Like New', "price": 75, "stock": 15},
                       {"condition": 'Lightly Used', "price": 50, "stock": 25},
                       {"condition": 'Well Used', "price": 30, "stock": 10}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 1,
        "subcategories": ["Rock", "Pop"]
      },
      {
        "name": "Rumours",
        "creator": "Fleetwood Mac",
        "description": "Rumours is the eleventh studio album by Fleetwood Mac, released in 1977. It is one of the best-selling albums of all time, blending rock and pop with emotionally intense themes.",
        "image_thumbnail": "rumours.png",
        "images": ['rumours.png'],
        "conditions": [{"condition": 'Brand New', "price": 110, "stock": 10},
                      {"condition": 'Like New', "price": 85, "stock": 20},
                      {"condition": 'Lightly Used', "price": 60, "stock": 25},
                      {"condition": 'Well Used', "price": 40, "stock": 15}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 1,
        "subcategories": ["Rock", "Pop"]
      },
      {
        "name": "A Night at the Opera",
        "creator": "Queen",
        "description": "A Night at the Opera is the fourth studio album by the British rock band Queen, released in 1975. The album features the iconic 'Bohemian Rhapsody' and blends opera with hard rock.",
        "image_thumbnail": "a_night_at_the_opera.png",
        "images": ['a_night_at_the_opera.png'],
        "conditions": [{"condition": 'Brand New', "price": 120, "stock": 8},
                      {"condition": 'Like New', "price": 95, "stock": 15},
                      {"condition": 'Lightly Used', "price": 70, "stock": 18},
                      {"condition": 'Well Used', "price": 50, "stock": 12}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 1,
        "subcategories": ["Rock", "Classic"]
      }
  ]
  
  book_products = [
      {
        "name": "To Kill a Mockingbird",
        "creator": "Harper Lee",
        "description": "To Kill a Mockingbird is a coming-of-age story about a girl named Scout. Scout and her brother Jem try to understand and relate to their father, Atticus, who is a lawyer charged with defending a Black man falsely accused of harassing a white woman.",
        "image_thumbnail": "to_kill_a_mockingbird.png",
        "images": ['to_kill_a_mockingbird.png', 'to_kill_a_mockingbird2.png'],
        "conditions": [{"condition": 'Brand New', "price": 40, "stock": 20},
                        {"condition": 'Like New', "price": 35, "stock": 20},
                        {"condition": 'Lightly Used', "price": 30, "stock": 30},
                        {"condition": 'Well Used', "price": 15, "stock": 5}],
        "is_featured_special": True,
        "is_featured_staff": True,
        "category_id": 2,  # Book
        "subcategories": ["Fiction", "Young Adult"]  # Link to these subcategories
      },
      {
          "name": "Sapiens: A Brief History of Humankind",
        "creator": "Yuval Noah Harari",
        "description": "Sapiens by Yuval Noah Harari is a historical overview of human evolution and civilization, addressing how humans became the dominant species and shaped their societies, economies, and cultures.",
        "image_thumbnail": "sapiens__a_brief_history_of_humankind.png",
        "images": ['sapiens__a_brief_history_of_humankind.png'],
        "conditions": [{"condition": 'Brand New', "price": 40, "stock": 20},
                        {"condition": 'Like New', "price": 35, "stock": 20},
                        {"condition": 'Lightly Used', "price": 30, "stock": 30},
                        {"condition": 'Well Used', "price": 15, "stock": 5}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 2,  # Book
        "subcategories": ["Non-Fiction", "History", "Science"]  # Link to these subcategories
      },
      {
        "name": "1984",
        "creator": "George Orwell",
        "description": "1984 is a dystopian novel set in a totalitarian society governed by 'Big Brother.' The protagonist, Winston Smith, struggles to rebel against the oppressive regime, which manipulates truth and history.",
        "image_thumbnail": "1984.png",
        "images": ['1984.png'],
        "conditions": [{"condition": 'Brand New', "price": 20, "stock": 15},
                       {"condition": 'Like New', "price": 18, "stock": 25},
                       {"condition": 'Lightly Used', "price": 15, "stock": 30},
                       {"condition": 'Well Used', "price": 10, "stock": 10}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 2,
        "subcategories": ["Fiction", "Dystopian"]
      },
      {
        "name": "The Great Gatsby",
        "creator": "F. Scott Fitzgerald",
        "description": "The Great Gatsby tells the story of Jay Gatsby's unrequited love for Daisy Buchanan. Set in the Jazz Age, it critiques the American Dream and the corruption of the era.",
        "image_thumbnail": "the_great_gatsby.png",
        "images": ['the_great_gatsby.png'],
        "conditions": [{"condition": 'Brand New', "price": 25, "stock": 20},
                      {"condition": 'Like New', "price": 20, "stock": 30},
                      {"condition": 'Lightly Used', "price": 15, "stock": 35},
                      {"condition": 'Well Used', "price": 10, "stock": 15}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 2,
        "subcategories": ["Fiction", "Classic"]
      },
      {
        "name": "The Catcher in the Rye",
        "creator": "J.D. Salinger",
        "description": "The Catcher in the Rye follows Holden Caulfield, a troubled teenager navigating life in New York City after being expelled from his prep school. The novel explores themes of alienation and disillusionment.",
        "image_thumbnail": "the_catcher_in_the_rye.png",
        "images": ["the_catcher_in_the_rye.png"],
        "conditions": [{"condition": 'Brand New', "price": 20, "stock": 25},
                      {"condition": 'Like New', "price": 15, "stock": 30},
                      {"condition": 'Lightly Used', "price": 12, "stock": 35},
                      {"condition": 'Well Used', "price": 8, "stock": 20}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 2,
        "subcategories": ["Fiction", "Classic"]
      },
      {
        "name": "The Hobbit",
        "creator": "J.R.R. Tolkien",
        "description": "The Hobbit follows the journey of Bilbo Baggins, a hobbit who sets out on an adventure to help a group of dwarves reclaim their homeland from a dragon. A tale of bravery, magic, and friendship.",
        "image_thumbnail": "the_hobbit.png",
        "images": ['the_hobbit.png'],
        "conditions": [{"condition": 'Brand New', "price": 22, "stock": 20},
                      {"condition": 'Like New', "price": 18, "stock": 25},
                      {"condition": 'Lightly Used', "price": 15, "stock": 30},
                      {"condition": 'Well Used', "price": 10, "stock": 15}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 2,
        "subcategories": ["Fantasy", "Adventure"]
      },
      {
        "name": "Brave New World",
        "creator": "Aldous Huxley",
        "description": "Brave New World is a dystopian novel set in a future where technology, genetic engineering, and surveillance have created a society that is designed for the perfect order, stability, and happiness.",
        "image_thumbnail": "brave_new_world.png",
        "images": ['brave_new_world.png'],
        "conditions": [{"condition": 'Brand New', "price": 18, "stock": 15},
                       {"condition": 'Like New', "price": 15, "stock": 20},
                       {"condition": 'Lightly Used', "price": 12, "stock": 25},
                       {"condition": 'Well Used', "price": 8, "stock": 10}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 2,
        "subcategories": ["Fiction", "Dystopian"]
      },
      {
        "name": "The Lord of the Rings: The Fellowship of the Ring",
        "creator": "J.R.R. Tolkien",
        "description": "The Fellowship of the Ring is the first part of J.R.R. Tolkien's epic fantasy trilogy, 'The Lord of the Rings.' It tells the story of Frodo Baggins and his journey to destroy the One Ring.",
        "image_thumbnail": "lotr_the_fellowship_of_the_ring.png",
        "images": ["lotr_the_fellowship_of_the_ring.png"],
        "conditions": [{"condition": 'Brand New', "price": 25, "stock": 18},
                       {"condition": 'Like New', "price": 20, "stock": 22},
                       {"condition": 'Lightly Used', "price": 17, "stock": 30},
                       {"condition": 'Well Used', "price": 12, "stock": 12}],
        "is_featured_special": False,
        "is_featured_staff": True,
        "category_id": 2,
        "subcategories": ["Fantasy", "Adventure"]
      },
      {
        "name": "The Catcher Was a Spy: The Mysterious Life of Moe Berg",
        "creator": "Nicholas Dawidoff",
        "description": "The Catcher Was a Spy tells the incredible true story of Moe Berg, a Major League Baseball player who was also an undercover spy during World War II, balancing two distinct lives.",
        "image_thumbnail": "the_catcher_was_a_spy.png",
        "images": ['the_catcher_was_a_spy.png'],
        "conditions": [{"condition": 'Brand New', "price": 20, "stock": 15},
                       {"condition": 'Like New', "price": 18, "stock": 18},
                       {"condition": 'Lightly Used', "price": 15, "stock": 25},
                       {"condition": 'Well Used', "price": 12, "stock": 10}],
        "is_featured_special": True,
        "is_featured_staff": False,
        "category_id": 2,
        "subcategories": ["Non-Fiction", "Biography", "History"]
      }
  ]

  all_products = vinyl_products + book_products

  for product_data in all_products:
      # Create a Product instance
      product = Product(
          name=product_data["name"],
          creator=product_data["creator"],
          description=product_data["description"],
          image_thumbnail=product_data["image_thumbnail"],
          images=product_data["images"],
          conditions=product_data["conditions"],
          is_featured_special=product_data["is_featured_special"],
          is_featured_staff=product_data["is_featured_staff"],
          category_id=product_data["category_id"]
      )
      db.session.add(product)
      db.session.commit()  # Commit to generate product.id

      # Link to subcategories
      for subcategory_name in product_data["subcategories"]:
          subcategory = SubCategory.query.filter_by(subcategory_name=subcategory_name).first()
          if subcategory:
              product.subcategories.append(subcategory)

      db.session.commit()

  print("Inserted products.")

def insert_reviews():
  products = Product.query.all()
  from random import randint
  from sqlalchemy.orm.attributes import flag_modified

  for product in products:
    for x in range(randint(1,7)):
      rev = Review(
        show_username=[True, False][randint(0,1)],
        rating=randint(3,5),
        description='This is a dummy review.',
        product_id=product.id,
        user_id=4
      )
      db.session.add(rev)
    if not product.rating:
      product.update_rating()
      flag_modified(product, 'rating')

  db.session.commit()

def insert_orders():
  payment_info = PaymentInformation(
      user_id=4,
      paymentType_id=1,
      card_number="1234567812345678",
      card_name="John Doe",
      expiry_date="12/25",
      card_cvv="123"
  )
  db.session.add(payment_info)
  db.session.commit()

  billing_info = BillingAddress(
    user_id=4,
    address_one='123 Milky Way Drive, Arizona, #40-888, 39482',
    unit_number='1',
    postal_code='123456',
    phone_number='+65 1234 56789',
  )
  db.session.add(billing_info)
  db.session.commit()

# uncomment only if needed, otherwise will create duplicate customer account.
  # import stripe 
  # user = User.query.filter_by(id=4).first()
  # stripe.Customer.create(
  #   name= f"{user.first_name} {user.last_name}",
  #   email= user.email,
  #   shipping={
  #     'address': {
  #       'line1': billing_info.address_one,
  #       'postal_code': billing_info.postal_code
  #     },
  #     'name': f"{user.first_name} {user.last_name}",
  #     'phone': billing_info.phone_number
  #   }
  # )
  
  for x in range(4):
    order = Order(
        user_id=4,
        total_amount=0,
        delivery='standard',
        payment_type_id=1,
        payment_information_id=payment_info.id,
        billing_id=billing_info.id
    )
    db.session.add(order)
    db.session.commit()
    
    products = Product.query.all()
    from random import randint
    for product in products[:randint(1,4)]:
      i = randint(0,3)
      item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_condition=product.conditions[i],
        quantity=randint(1,2),
        unit_price=product.conditions[i]['price']
      )
      db.session.add(item)
      db.session.commit()

      order.update_total()
      db.session.commit()

  # second
  payment_info = PaymentInformation(
      user_id=4,
      paymentType_id=2,
      card_number="1234567812345678",
      card_name="John Doe",
      expiry_date="12/25",
      card_cvv="123"
  )
  db.session.add(payment_info)
  db.session.commit()

  billing_info = BillingAddress(
    user_id=4,
    address_one='123 Milky Way Drive, Arizona, #40-888, 39482',
    unit_number='1',
    postal_code='123456',
    phone_number='+65 1234 56789',
  )
  db.session.add(billing_info)
  db.session.commit()
  
  for x in range(5):
    from datetime import datetime,timedelta
    order = Order(
        user_id=4,
        order_date=datetime.now()-timedelta(days=randint(20, 40)),
        total_amount=0,
        delivery='expedited',
        payment_type_id=2,
        payment_information_id=payment_info.id,
        billing_id=billing_info.id
    )
    db.session.add(order)
    db.session.commit()
    
    products = Product.query.all()
    from random import randint
    for product in products[4:randint(5,15)]:
      i = randint(0,3)
      item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_condition=product.conditions[i],
        quantity=randint(1,2),
        unit_price=product.conditions[i]['price']
      )
      db.session.add(item)
      db.session.commit()

    order.update_total()
    db.session.commit()

def insert_voucher_types():
  types = [
    VoucherType(voucher_type='percentage'),
    VoucherType(voucher_type='fixed_amount'),
    VoucherType(voucher_type='free_shipping')
  ]
    
  for type in types:
    existing = VoucherType.query.filter_by(voucher_type=type.voucher_type).first()
    if not existing:
      db.session.add(type)
    
  db.session.commit()
  print("Inserted voucher types.")

def insert_vouchers():
  from .models import Voucher, VoucherType
    
  # mapping of type names to their IDs
  type_map = {type.voucher_type: type.id for type in VoucherType.query.all()}
    
  vouchers_data = {
    # Vinyl Exclusive Vouchers
    'VINYLSHIP': {
      'description': 'Enjoy free shipping on any vinyl record purchase above $50. Perfect for building your collection!',
      'type': 'free_shipping',
      'discount_value': 0,
      'criteria': [{'type': 'min_cart_amount', 'value': 50}],
      'eligible_categories': ['Vinyl'],
      'expiry_days': 30
    },
    'VINYL25': {
      'description': 'Get 25% off on your vinyl purchase. Maximum discount of $30.',
      'type': 'percentage',
      'discount_value': 25,
      'criteria': [{'type': 'min_cart_items', 'value': 1}],
      'eligible_categories': ['Vinyl'],
      'expiry_days': 14
    },
    'VINYLNEW15': {
      'description': 'Save $15 on any new release vinyl record. Minimum purchase of $75 required.',
      'type': 'fixed_amount',
      'discount_value': 15,
      'criteria': [
        {'type': 'min_cart_amount', 'value': 75}
      ],
      'eligible_categories': ['Vinyl'],
      'expiry_days': 7
    },
    'VINYL2FOR1': {
      'description': 'Buy any vinyl and get 50% off on your second vinyl of equal or lesser value.',
      'type': 'percentage',
      'discount_value': 50,
      'criteria': [{'type': 'min_cart_amount', 'value': 2}],
      'eligible_categories': ['Vinyl'],
      'expiry_days': 30
    },
        
    # Book Lovers' Specials
    'BOOKWORM20': {
      'description': 'Enjoy 20% off on all books. Perfect for expanding your reading collection!',
      'type': 'percentage',
      'discount_value': 20,
      'criteria': [{'type': 'min_cart_items', 'value': 1}],
      'eligible_categories': ['Book'],
      'expiry_days': 30
    },
    'BOOKSHIP': {
      'description': 'Free shipping on any book order above $35. Stock up on your reading list!',
      'type': 'free_shipping',
      'discount_value': 0,
      'criteria': [{'type': 'min_cart_amount', 'value': 50}],
      'eligible_categories': ['Book'],
      'expiry_days': 14
    },
    'BOOK10OFF': {
      'description': 'Take $10 off when you spend $50 or more on books.',
      'type': 'fixed_amount',
      'discount_value': 10,
      'criteria': [{'type': 'min_cart_amount', 'value': 50}],
      'eligible_categories': ['Book'],
      'expiry_days': 30
    },
    'BOOKNEW': {
      'description': 'Get 15% off on all new release books. Stay current with the latest titles!',
      'type': 'percentage',
      'discount_value': 15,
      'criteria': [{'type': 'min_cart_items', 'value': 1}],
      'eligible_categories': ['Book'],
      'expiry_days': 21
    },
        
    # Special Vouchers
    'FIRSTOFF10': {
      'description': 'Enjoy 10% off on your first order. Start your journey at Rewwwind!',
      'type': 'percentage',
      'discount_value': 10,
      'criteria': [{'type': 'first_purchase_only', 'value': 'true'}],
      'eligible_categories': ['Book', 'Vinyl'],
      'expiry_days': 30
    },
    'FREESHIP': {
      'description': 'Free shipping on your order above $50. Stock up on your reading list!',
      'type': 'free_shipping',
      'discount_value': 0,
      'criteria': [{'type': 'min_cart_amount', 'value': 50}],
      'eligible_categories': ['Book', 'Vinyl'],
      'expiry_days': 14
    },
    'GET10OFF': {
      'description': 'Take $15 off when you spend $100 or more.',
      'type': 'fixed_amount',
      'discount_value': 15,
      'criteria': [{'type': 'min_cart_amount', 'value': 100}],
      'eligible_categories': ['Book', 'Vinyl'],
      'expiry_days': 30
    },
    'SPECIAL15': {
      'description': 'Get 15% off on all new specials. Stay current with the latest titles!',
      'type': 'percentage',
      'discount_value': 15,
      'criteria': [{'type': 'min_cart_items', 'value': 1}],
      'eligible_categories': ['Book', 'Vinyl'],
      'expiry_days': 21
    }
  }

  for code, data in vouchers_data.items():
    voucher_exists = Voucher.query.filter_by(voucher_code=code).first()
    if not voucher_exists:
      new_voucher = Voucher(
        voucher_code=code,
        voucher_description=data['description'],
        voucherType_id=type_map[data['type']],
        discount_value=data['discount_value'],
        criteria=data['criteria'],
        eligible_categories=data['eligible_categories'],
        expiry_days=data['expiry_days'],
        is_active=True
      )
      db.session.add(new_voucher)
      db.session.commit()

      new_user_voucher = UserVoucher(
        user_id=4,
        voucher_id=new_voucher.id,
        expires_at=datetime.now() + timedelta(days=new_voucher.expiry_days)
      )

      if new_voucher.voucher_code == 'FIRSTOFF10':
        new_user_voucher2 = UserVoucher(
          user_id=5,
          voucher_id=new_voucher.id,
          expires_at=datetime.now() + timedelta(days=new_voucher.expiry_days)
        )
        db.session.add(new_user_voucher2)
        db.session.commit()
        
      db.session.add(new_user_voucher)
      db.session.commit()
  print('Inserted default vouchers into the database!')