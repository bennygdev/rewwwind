# Rewwwind

Rewwwind is a store that sells second-hand refurbished books and records, which allows customers to access affordable and unique literary and musical content while promoting sustainability by reducing waste and extending lifespan of pre-loved items. 

In addition, customers have the option to trade in their used books and records, with the condition depending of the incentive offered, such as cash, credits, discounts, or exclusive rewards.

Members:
- Benny Goh (Users, Customer Experience)
- Nelson Jonathan (Products, Orders, Checkout)
- Ryan Yeo (Trade-ins)
- Femina Jasmin (Wishlist, Vouchers)

# Features
WIP (will be updated before presentation)

# Contributions
What features did we do? (Paste all contents of this file into readme.so to view editing live)

NOTE: I've moved the instructions to run and contribute to `HOWTORUN.md`, same exact content.

Benny:
- Project environment and setup
- Designed Home landing page, Footer, About pages, Rewards page, Legal pages, Error (401, 403, 404) pages
- 3 Account Role levels (Customer, Admin, Owner (superuser))
- Dashboard system that houses for all business functions
- Overview
    - Shows customer related data and metrics on a dashboard using ChartJS (Only viewable for Customers)
    - Shows admin related data and metrics on a dashboard using ChartJS (Only viewable for Admins, Owners)
- User Settings
    - Edit personal information
        - Edit personal particulars, including profile picture
        - Change email
        - Change Password
        - Delete Account and related information
    - Add/Edit/Delete Billing information
    - Add/Edit/Delete Payment information
    - Ability to subscribe and unsubscribe to newsletter notifications
- Authentication
    - Ability to register normally or with google
        - Username suggestions when setting username
    - Ability to login normally or with google
    - Default identicon profile picture generation for new registered Accounts
    - Reset password functionality using flask mail
- Manage Accounts
    - Account listing
    - Account details viewing (Admin can only view customer accounts, whereas Owners can view both admin and customer accounts but except other owner accounts) with statistics using ChartJS
    - Account editing and deletion (Admin can only modify customer accounts, whereas Owners can modify both admin and customer accounts but except other owner accounts)
    - Account password change (Same for roles I described)
    - Owner has the ability to add any role-level accounts
- Customer Chat
    - Use of socket to faciliate communication between admin (as support representative) and customer
    - Typing indicators
    - Ability to save and summarise chat conversation, and view it later (Chat summary by Gemini AI)
    - Ability to compensate vouchers to customers
- Chat with AI
    - Ability to chat with AI, which will provide product recommendations and store-related inquiries. (Using Gemini AI)
- Newsletter
    - Ability for users to subscribe to newsletter
    - Ability to search and delete users from mailing listing
    - Ability to send out emails to every person in the mailing list, which will create a post in the database
    - Ability to read and delete posted newsletters
    - Ability to unsubscribe from the link provided in the email

Nelson:

(fill in what you have done)

Ryan:
- Designed Trade-in and Condition guidelines onboarding pages
- Trade in application, request
- Trade in 
(fill in what you have done)

Femina:
- Wishlist creation
- Cart page
    - Ability to add and remove products from cart
    - Ability to adjust quantity
    - Abililty to apply Vouchers
- Voucher CRUD for admin-side
- Voucher listing for both customers and admins
- Voucher Gifting to customers
(fill in what you have done)
