# Rewwwind

Rewwwind is a store that sells second-hand refurbished books and records, which allows customers to access affordable and unique literary and musical content while promoting sustainability by reducing waste and extending lifespan of pre-loved items. 

In addition, customers have the option to trade in their used books and records, with the condition depending of the incentive offered, such as cash, credits, discounts, or exclusive rewards.

Members:
- Benny Goh (Users, Customer Experience, Overview/Analytics, Newsletter)
- Nelson Jonathan (Products, Orders, Checkout)
- Ryan Yeo (Trade-ins)
- Femina Jasmin (Wishlist, Vouchers, Cart)

# Features
- Role-based Dashboard System and Overview: Customised interfaces for Customers, Admins, and Owners, each displaying relevant data and metrics through ChartJS
- Comprehensive user system: Account listing, view customer statistics, add/edit/delete user profile, billing and payment information, adjust notification and security settings. Users can enable 2FA authentication, and can too register/login with Google.
- Chat feature: Customers can inquire with our store's AI for enquiries and support, customers can in addition switch to chatting with a support representative.
- Newsletter: Customers have the ability to sign up for newsletter and receive subscription emails.
- Voucher system: Ability to create and gift vouchers to customers.
- Streamlined Products system: Able to search and order products, ability to search via uploading images and ability to rate and add reviews.
- Checkout system: Users can dynamically apply vouchers and checkout with vouchers applied. The checkout ordering process is handled via Stripe.
- Trade-in system: Ability to file out a trade-in application and fill out details based on status of approval. The customer will then be compensated according to the item condition.

# Technologies
- Frontend: HTML, JavaScript, CSS, Bootstrap
- Backend: Python, Flask, WTForms, Flask-Mail, SQLAlchemy
- Technologies: PyTorch, Google OAuth, Dotenv, PyPDF
- APIs: ChartJS, Google Gemini, Socketio, Cloudinary
- Payments: Stripe

# Contributions

Benny:
- Project environment and setup
- Designed and drafted UI/UX for Storefront, Footer, About pages, Rewards page, Legal pages, Error (401, 403, 404) pages
- 3 Account Role levels (Customer, Admin, Owner (superuser))
- Dashboard system that houses for all business functions
    - Dashboard pages are shown accordingly to role levels
- Overview
    - Shows customer related data and metrics on a dashboard using ChartJS (Only viewable for Customers)
    - Shows admin related data and metrics on a dashboard using ChartJS (Only viewable for Admins, Owners)
- Profile Page
    - Shows user's recent orders
    - Has a product recommendation algorithm that recommends products based on user's order history (Recommends 5 products based on user's ordered category ratio)
- User Settings
    - Edit personal information
        - Edit personal particulars, including profile picture
        - Change email
        - Delete Account and related information
    - Security Settings
        - Option to enable/disable 2FA
        - Enabling 2FA will send a 6 digit code for users to verify their email before activating
        - Change Password
    - Add/Edit/Delete Billing information
    - Add/Edit/Delete Payment information
    - Ability to subscribe and unsubscribe to newsletter notifications
- Authentication
    - Ability to register normally or with google login (OAuth)
        - Username suggestions when setting username
    - Ability to login normally or with google
    - Two-Factor Authentication (2FA) via email. Users can activate and deactivate 2FA via settings. 6 Digit code is provided for verification.
    - Default identicon profile picture generation for new registered Accounts
    - Reset password functionality using flask mail, with secure token URL
- Manage Accounts
    - Account listing
        - Ability to search, paginate and filter accounts
    - Account details viewing (Admin can only view customer accounts, whereas Owners can view both admin and customer accounts but except other owner accounts) with statistics using ChartJS
    - Account editing and deletion (Admin can only modify customer accounts, whereas Owners can modify both admin and customer accounts but except other owner accounts)
    - Account password change (Same for roles I described)
    - Owner has the ability to add any role-level accounts
- Customer Chat
    - Use of socketio to faciliate communication between customer and admin (as support representative) and customer
    - Typing indicators
    - Ability to save and summarise chat conversation, and view it later (Chat summary by Gemini AI)
    - Chat History Page (To view previous chat conversations)
        - Ability to search, paginate and filter chat conversations
        - Ability to compensate vouchers to customers
- Chat with AI
    - Ability to chat with AI, which will provide product/search recommendations and store-related inquiries. (Using Gemini AI)
- Newsletter
    - Ability for users to subscribe to newsletter
    - Ability to search and delete users from mailing listing
    - Ability to send out emails to every person in the mailing list, which will create a post in the database
    - Ability to search, paginate and filter newsletter posts
    - Ability to read and delete posted newsletters
    - Ability to unsubscribe from the link provided in the email

Nelson:
- Products Pagination
    - Products filter
    - Similar image search using openai/clip-vit-base-patch32
        - Matches closest product within a specified threshold
        - Returns none if no matches are found
    - List and grid view
    - Product-Specific Pages
        - Dynamic pricing according to selected condition
        - Add Review
            - Rate products
            - Optional annonymity (Hides the username)
            - Optional comments
        - Update Review
        - Delete Review
- Manage Products (Viewable by Admins & Owners Only)
    - Add Products
        - Basic product information
        - Condition selector
        - Image(s) are upload to the cloud (Cloudinary)
            - All images are obtained from Cloudinary
            - Automatic deletion of images from Cloudinary
        - Filled information is temporarily stored upon exit
    - Update Products
        - All of the above
    - Delete Products
        - Deletes product and all related information
        - Aborts when product is matched in an ongoing order
- Manage Orders
    - View Orders (Viewable by All Roles)
        - Summary of Order
        - Invoice Generation (Only when approved by admin)
    - Update Orders (Viewable by Admins & Owners Only)
        - Update Approval Status
- Checkout / Payment
    - Pre-Payment
        - Delivery Type (Method)
        - Pick-Up Information or Billing Information (Depending on delivery type chosen)
        - Voucher Selection (If any)
    - Payment via Stripe
        - Payment information securely stored in Stripe
        - Automatic retrieval of saved payment information upon checkout
    - Persistent Information Throughout Checkout Process (until cancellation or success)


Ryan:
- Drafted the overall UI/UX for the Trade-in, and Condition Guidelines onboarding pages.
- Trade in request form and Dashboard (For both Customer and Admin sides)
   - Customers can send in trade-in requests where Admin can approve or reject their request
   - For approved requests, customers can input their payment details and method of drop-off

Femina:
- Wishlist creation
    - favourite items from products page to wishlist page 
    - display all wishlited/favourited items
    - from wishlisted page able to add to cart 
- Cart page
    - Ability to add and remove products from cart
    - Ability to adjust quantity
    - Abililty to apply Vouchers
- Voucher CRUD for admin-side
- Voucher listing for both customers and admins
- Voucher Gifting to customers
    - must have met the requirements in order to apply the voucher

