from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from datetime import datetime
from flask import render_template
# from flask_login import LoginManager

# import mysql.connector as mysql 
import os

from flask_session import Session
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# login_manager = LoginManager()
# login_manager.init_app(app)

app.config['SECRET_KEY'] = os.urandom(24) #'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
bcrypt = Bcrypt()
CORS(app)
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='P@ssw0rd',
    database='project 1 commerce'
)

# Define route for the homepage
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s ', (username,))
        existing_user = cursor.fetchone()

        # print( "hello"+ existing_user[2])

        
        if existing_user:
            if existing_user[1] == username:
                return render_template('signup.html', message='Username already taken. Please choose a different one.')
            elif existing_user[2] == email:
                return render_template('signup.html', message='Email already taken. Please choose a different one.')
            #return render_template('signup.html', message='Username already taken. Please choose a different one.')
        
        is_seller = 'seller' if role == 'seller' else 'buyer'

    # Insert user into database with the determined role
        cursor.execute('INSERT INTO users (username, email, password, is_seller) VALUES (%s, %s, %s, %s)',
                   (username, email, hashed_password, is_seller))
        
        conn.commit()
        return redirect(url_for('home'))

    
    return render_template('signup.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, password, is_seller FROM users WHERE username = %s', (username,))
#         user = cursor.fetchone()

         
        
#         if user and bcrypt.check_password_hash(user[1], password):
            
#                 session['username'] = username
#                 session['user_id'] = user[0]
#                 session['is_seller'] = user[4] # Set the is_seller session variable to the value fetched from the database
            
#                 if session['is_seller'] == 'buyer':
#                     return redirect(url_for('buyer_page'))
#                 else:
#                     return redirect(url_for('seller_page'))
#         else:
#             return render_template('login.html', message='Invalid credentials. Please try again.')
#     else:
#         return render_template('login.html')

# from flask import render_template, session


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        cursor = conn.cursor()
        cursor.execute('SELECT id, password, is_seller FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        
        
        if user and bcrypt.check_password_hash(user[1], password):
            
            # # Print out user information
            print("ID:", user[0])
            print("Username:", user[1])
            print("Is Seller:", user[2])
            # print("Is Seller:", user[4]) 
            # print("column:",user[0])
            # print('column')


            session['username'] = username
            session['user_id'] = user[0]
            session['is_seller'] = user[2]

            # print("User found:")
           
            
        
            # if user:
            #     # Print out user information
            #     print("User found:")
            #     for i, value in enumerate(user):
            #         print(f"Column {i}: {value}")


            if  user[2] == 'seller':
            # if user.is_seller == 'seller':
                return redirect(url_for('seller_page'))
            else:
                return redirect(url_for('buyer_page'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')

    return render_template('login.html')




@app.route('/buyer_account')
def view_buyer_account():
    # Check if user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Query the database to fetch the buyer's information based on the user_id and is_seller column
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = %s AND is_seller = 0', (user_id,))
        buyer_info = cursor.fetchone()
        cursor.close()

        if buyer_info:
            return render_template('view_buyer_account.html', buyer=buyer_info)
        else:
            return "Buyer account not found."
    else:
        return "You need to log in to view your buyer account."


@app.route('/delete/<int:id>',methods=['GET'])
def delete_user(id):
    cursor=conn.cursor()
    cursor.execute('DELETE from users where id=%s',(id,))
    conn.commit()
    # conn.close()
    return redirect(url_for('view_users'))


@app.route('/update/<int:id>',methods=['GET','POST'])
def update_account(id):
    cursor=conn.cursor()
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute('UPDATE users set name=%s, email=%s where id=%s',(name,email,hashed_password,id))
        conn.commit()
        return redirect(url_for(''))
    cursor.execute('select * from users where id=%s',(id,))
    user=cursor.fetchone()
    return render_template('update_user.html', user=user)

@app.route('/seller_page')
def seller_page():
    # Logic for rendering the seller page
    return render_template('seller_page.html')

@app.route('/insert_product',methods=['GET','POST'])
def insert_product():
    if request.method == "POST":
        # Retrieve product details from the form data
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        name = request.form['name']
        min_bid = request.form['min_bid']
        bidding_deadline = request.form['bidding_deadline']

     # Retrieve seller_id from the session or wherever you store user information
        seller_id = session.get('user_id')  # Adjust this based on your authentication logic

        cursor = conn.cursor()

        # Insert the new product into the database
        cursor.execute("INSERT INTO products (seller_id, description, price, quantity, name, min_bid, bidding_deadline) VALUES (%s, %s, %s, %s, %s, %s,%s)",
                       (seller_id, description, price, quantity, name, min_bid, bidding_deadline))
        conn.commit()

        cursor.close()

        # Redirect to a success page or any other appropriate action after inserting the product
        return redirect('/view_products')  # Replace '/success' with the appropriate URL

    # If the request method is GET, render the insert product form
    return render_template('insert_product.html')

# @app.route('/view_products', methods=['GET', 'POST'])
# def seller_view():
#     try:
#         cursor = conn.cursor()
#         seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#         # Fetch products available for the seller from the database
#         cursor.execute('SELECT * FROM products WHERE seller_id = %s', (seller_id,))
#         products = cursor.fetchall()
#         session['products'] = products

#         if not products:
#             print("No products found for seller with ID:", seller_id)
#         else:
#             print("Products found:", products)

#         # Check if any bids have expired and update purchase status if necessary
#         for product in products:
#             if product['bidding_deadline'] < datetime.now() and product['purchased'] != 'yes':
#                 # Update the purchase status in the database
#                 cursor.execute("UPDATE products SET purchased = 'yes' WHERE id = %s", (product['id'],))
#                 conn.commit()

#         cursor.close()

#         return render_template('seller_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # # Render an error page or return an error message to the client
#         # return render_template('error.html', message="An error occurred while fetching product data.")



# @app.route('/view_products', methods=['GET', 'POST'])
# def seller_view():
#     try:
#         cursor = conn.cursor()
#         seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#         # Fetch products available for the seller from the database
#         cursor.execute('''
#             SELECT p.*, 
#                    COALESCE((SELECT MAX(bid_price) FROM bids WHERE product_id = p.id AND bid_time > p.bidding_deadline), 0) AS total_revenue
#             FROM products p
#             WHERE p.seller_id = %s
#         ''', (seller_id,))
#         products = cursor.fetchall()
#         session['products'] = products

#         if not products:
#             print("No products found for seller with ID:", seller_id)
#         else:
#             print("Products found:", products)

#         cursor.close()

#         return render_template('seller_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # Render an error page or return an error message to the client
#         return render_template('error.html', message="An error occurred while fetching product data.")




# @app.route('/view_products', methods=['GET', 'POST'])
# def seller_view():
#     try:
#         cursor = conn.cursor()
#         seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#         # Fetch products available for the seller from the database
#         cursor.execute('''
#             SELECT p.*, 
#                    COALESCE(MAX(b.bid_price), 0) AS bid_price,
#                    COALESCE(SUM(b.bid_price), 0) AS total_revenue
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             WHERE p.seller_id = %s
#             GROUP BY p.id
#         ''', (seller_id,))
#         products = cursor.fetchall()
#         session['products'] = products

#         if not products:
#             print("No products found for seller with ID:", seller_id)
#         else:
#             print("Products found:", products)

#         cursor.close()

#         return render_template('seller_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # Render an error page or return an error message to the client
#         return render_template('error.html', message="An error occurred while fetching product data.")


# @app.route('/view_products', methods=['GET', 'POST'])
# def seller_view():
#     try:
#         cursor = conn.cursor()
#         seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#         # Fetch products available for the seller from the database
#         cursor.execute('''
#             SELECT p.*, 
#                    COALESCE(MAX(b.bid_price), 0) AS bid_price
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             WHERE p.seller_id = %s
#             GROUP BY p.id
#         ''', (seller_id,))
#         products = cursor.fetchall()

#         # Process each product to check if bid_price should be set to 0
#         for product in products:
#             if product['bid_price'] == 0:
#                 product['bid_price'] = None  # Set bid_price to None if it's 0

#         session['products'] = products

#         if not products:
#             print("No products found for seller with ID:", seller_id)
#             return "No products found. Please try again later."  # Return a simple error message

#         cursor.close()

#         return render_template('seller_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         return "An error occurred while fetching product data. Please try again later."  # Return a simple error message


# @app.route('/view_products', methods=['GET', 'POST'])
# def seller_view():
#     try:
#         cursor = conn.cursor()
#         seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#         # Fetch products available for the seller from the database
#         cursor.execute('''
#             SELECT p.*, COALESCE(MAX(b.bid_price), 0) AS max_bid_price
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             WHERE p.seller_id = %s
#             GROUP BY p.id
#         ''', (seller_id,))
#         products = cursor.fetchall()

#         session['products'] = products

#         if not products:
#             print("No products found for seller with ID:", seller_id)
#             return "No products found."  # Display a simple error message

#         cursor.close()

#         return render_template('seller_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # Return an error message to the client
#         return "An error occurred while fetching product data. Please try again later."


@app.route('/view_products', methods=['GET', 'POST'])
def seller_view():
    try:
        cursor = conn.cursor()
        seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

        # Fetch products available for the seller from the database
        cursor.execute('''
            SELECT p.*, COALESCE(MAX(b.bid_price), 0) AS max_bid_price, COALESCE(SUM(b.bid_price), 0) AS total_revenue
            FROM products p
            LEFT JOIN bids b ON p.id = b.product_id
            WHERE p.seller_id = %s
            GROUP BY p.id
        ''', (seller_id,))
        products = cursor.fetchall()


        for product in products:

            # Print product details for debugging
            print("Product ID:", product[0])
            print("Bidding Deadline:", product[8])
            print("Purchased Status:", product[9])
            print("Highest Bid Price:", product[10])


            # Check if the deadline has passed and there's no highest bid
            if product[8] < datetime.now() and product[9] != 'yes' and product[10] == 0:
                # Update the purchased status to 'no' if the deadline passed with no bids
                cursor.execute("UPDATE products SET purchased = 'no' WHERE id = %s", (product[0],))
                conn.commit()
            elif product[10] != 0:
                # If there is a highest bid, set purchased status to 'yes'
                cursor.execute("UPDATE products SET purchased = 'yes' WHERE id = %s", (product[0],))
                conn.commit()

            else:
                # If there's no highest bid and the deadline hasn't passed, keep the purchased status unchanged
                cursor.execute("UPDATE products SET purchased = %s WHERE id = %s", ('no', product[0]))
                conn.commit()

        # for product in products:
        #     # Check if the deadline has passed and there's no highest bid
        #     if product[8] < datetime.now() and product[9] != 'yes' and product[10] == 0:
        #         # Update the purchased status to 'yes'
        #         cursor.execute("UPDATE products SET purchased = 'yes' WHERE id = %s", (product[0],))
        #         conn.commit()

        session['products'] = products

        if not products:
            print("No products found for seller with ID:", seller_id)
            return "No products found."  # Display a simple error message

        cursor.close()

        return render_template('seller_view.html', products=products)
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {str(e)}")
        # Return an error message to the client
        return "An error occurred while fetching product data. Please try again later."




# @app.route('/buyer_page', methods=['GET', 'POST'])
# def buyer_page():
#     try:
#         cursor = conn.cursor()

#         # Fetch products available for buyers from the database
#         cursor.execute('''
#             SELECT p.*, COALESCE(MAX(b.bid_price), 0) AS max_bid_price, COALESCE(SUM(b.bid_price), 0) AS total_revenue
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             GROUP BY p.id
#         ''')
#         products = cursor.fetchall()

#         # Update total revenue for products with passed bidding deadline and highest bid
#         for product in products:
#             # if product['bidding_deadline'] < datetime.now() and product['max_bid_price'] >= product['min_bid']:
#             if product[8] < datetime.now() and product[10] > 0:
#                 cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product[10], product[0]))
#                 conn.commit()
            
            
            
#             # if product['bidding_deadline'] < datetime.now() and product['max_bid_price'] > 0:
                
#             #     cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product['max_bid_price'], product['id']))
#             #     conn.commit()

#         session['products'] = products

#         if not products:
#             print("No products found.")
#             return "No products found."

#         cursor.close()

#         return render_template('buyer_page.html', products=products)
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return "An error occurred while fetching product data. Please try again later."
    
from datetime import datetime

# @app.route('/buyer_page', methods=['GET', 'POST'])
# def buyer_page():
#     try:
#         cursor = conn.cursor()

#         # Fetch available products for buyers from the database
#         cursor.execute('''
#             SELECT p.*, COALESCE(MAX(b.bid_price), 0) AS max_bid_price, COALESCE(SUM(b.bid_price), 0) AS total_revenue,
#             COALESCE((SELECT bid_price FROM bids WHERE product_id = p.id AND buyer_id = %s ORDER BY created_at DESC LIMIT 1), 0) AS buyer_bid_price
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             GROUP BY p.id
#         ''', (session.get('user_id'),))
#         products = cursor.fetchall()

#         # Delete products whose deadline has passed and no bids were placed
#         for product in products:
#             if product[8] < datetime.now() and product[10] == 0:
#                 cursor.execute("DELETE FROM products WHERE id = %s", (product[0],))
#                 conn.commit()

#         session['products'] = products

#         if not products:
#             print("No products found.")
#             return "No products found."

#         cursor.close()

#         return render_template('buyer_page.html', products=products)
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return "An error occurred while fetching product data. Please try again later."


from datetime import datetime


# @app.route('/buyer_page', methods=['GET', 'POST'])
# def buyer_page():
#     try:
#         cursor = conn.cursor()

#         # Fetch products available for buyers from the database
#         cursor.execute('''
#             SELECT p.*, COALESCE(MAX(b.bid_price), 0) AS max_bid_price, COALESCE(SUM(b.bid_price), 0) AS total_revenue
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id
#             GROUP BY p.id, p.seller_id, p.name, p.description, p.price, p.quantity, p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased
#         ''')
#         products = cursor.fetchall()

#         # Update total revenue for products with passed bidding deadline and highest bid
#         for product in products:
#             if product[8] < datetime.now() and product[10] > 0:
#                 cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product[10], product[0]))
#                 conn.commit()

#         session['products'] = products

#         if not products:
#             print("No products found.")
#             return "No products found."

#         cursor.close()

#         return render_template('buyer_page.html', products=products)
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return "An error occurred while fetching product data. Please try again later."


from flask import render_template, session
from datetime import datetime

@app.route('/buyer_page', methods=['GET', 'POST'])
def buyer_page():
    try:
        cursor = conn.cursor()

        # Fetch products available for buyers from the database
        cursor.execute('''
            SELECT p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                   p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased, 
                   COALESCE(MAX(b.bid_price), 0) AS max_bid_price, 
                   COALESCE(SUM(b.bid_price), 0) AS total_bid_price
            FROM products p
            LEFT JOIN bids b ON p.id = b.product_id
            GROUP BY p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                     p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased
        ''')
        products = cursor.fetchall()

        # Update total revenue for products with passed bidding deadline and highest bid
        for product in products:
            if product[8] < datetime.now() and product[10] > 0:
                cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product[10], product[0]))
                conn.commit()

        session['products'] = products

        if not products:
            print("No products found.")
            return "No products found."

        cursor.close()

        return render_template('buyer_page.html', products=products)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "An error occurred while fetching product data. Please try again later."






from datetime import datetime

# @app.route('/buyer_bid', methods=['POST'])
# def buyer_bid(product_id):
#     try:
#         bid_amount = request.form.get('bid_amount')

#         # Fetch product details including minimum bid and bidding deadline
#         cursor = conn.cursor()
#         cursor.execute('SELECT min_bid, bidding_deadline FROM products WHERE id = %s', (product_id,))
#         product_details = cursor.fetchone()
#         min_bid = product_details[0]      #from select min_bid
#         bidding_deadline = product_details[1]   #from select biddig_deadline

#         # Check if the bidding deadline has passed
#         if bidding_deadline < datetime.now():
#             return "Bidding for this product has ended."

#         # Check if the bid meets the minimum bid requirement
#         if float(bid_amount) < min_bid:
#             return "Bid doesn't meet the minimum bid requirement."

#         # If all checks pass, proceed to place the bid
#         # Your bid placement logic goes here...

#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # Return an error message to the client
#         return "An error occurred while processing the bid. Please try again later."


@app.route('/buyer_bid', methods=['GET','POST'])
def buyer_bid():
    try:
        # Retrieve the current buyer's ID from the session
        buyer_id = session.get('user_id')
        
        if buyer_id is None:
            return "User ID not found in session. Please log in first."

        # Retrieve the product ID and bid amount from the form data
        product_id = request.form.get('product_id')
        bid_amount = request.form.get('bid_amount')

        # Query the database to fetch product details including minimum bid and bidding deadline
        cursor = conn.cursor()
        cursor.execute('''
            SELECT min_bid, bidding_deadline FROM products WHERE id = %s
        ''', (product_id,))
        product_details = cursor.fetchone()

        # Check if product_details is None
        if product_details is None:
            return "Product not found."

        min_bid = product_details[0]
        bidding_deadline = product_details[1]

        # Check if the bidding deadline has passed
        if bidding_deadline < datetime.now():
            return "Bidding for this product has ended."

        # Check if the bid meets the minimum bid requirement
        if float(bid_amount) < min_bid:
            return "Bid doesn't meet the minimum bid requirement."
        
        
        
        # Fetch the highest bid for the product
        cursor.execute('''
            SELECT MAX(bid_price) FROM bids WHERE product_id = %s
        ''', (product_id,))
        highest_bid = cursor.fetchone()[0]

        # Check if the current bid is greater than the highest bid
        if highest_bid is not None and float(bid_amount) <= highest_bid:
            return "Someone else has placed a higher bid. Please bid higher."
        
         # If all checks pass, proceed to place the bid
        cursor.execute('''
            INSERT INTO bids (product_id, buyer_id, bid_price) 
            VALUES (%s, %s, %s)
        ''', (product_id, buyer_id, bid_amount))
        conn.commit()

        # If all checks pass, proceed to place the bid
        # Your bid placement logic goes here...

        cursor.close()

        # Optionally, redirect to a success page or return a success message
        return "Bid placed successfully!"

    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {str(e)}")
        # Return an error message to the client
        return "An error occurred while processing the bid. Please try again later."
    

# @app.route('/view_bids', methods=['GET', 'POST'])
# def view_bids():
#     try:
#         cursor = conn.cursor()
#         buyer_id = session.get('user_id')  # Retrieve the current buyer's ID from the session

#         # Fetch products the buyer has bid on along with the highest bid for each product
#         cursor.execute('''
#             SELECT p.*, b.bid_price AS current_bid, COALESCE(MAX(b2.bid_price), 0) AS highest_bid
#             FROM products p
#             LEFT JOIN bids b ON p.id = b.product_id AND b.buyer_id = %s
#             LEFT JOIN bids b2 ON p.id = b2.product_id
#             WHERE p.purchased IS NULL OR p.purchased = '' AND p.bidding_deadline > NOW()
#             GROUP BY p.id, p.seller_id, p.name, p.description, p.price, p.quantity, p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased
#         ''', (buyer_id,))
#         products = cursor.fetchall()

#         if not products:
#             print("No products found for buyer with ID:", buyer_id)
#             return "No products found."  # Display a simple error message

#         cursor.close()

#         return render_template('buyer_view.html', products=products)
#     except Exception as e:
#         # Log the error for debugging purposes
#         print(f"An error occurred: {str(e)}")
#         # Return an error message to the client
#         return "An error occurred while fetching product data. Please try again later."

@app.route('/view_bids', methods=['GET', 'POST'])
def view_bids():
    try:
        cursor = conn.cursor()
        buyer_id = session.get('user_id')  # Retrieve the current buyer's ID from the session

       # Fetch products the buyer has bid on along with the highest bid for each product
        cursor.execute('''
        SELECT 
            p.id, p.seller_id, p.name, p.description, p.price, p.quantity, p.total_revenue, 
            p.min_bid, p.bidding_deadline, p.purchased, 
            COALESCE(b.bid_price, 0) AS current_bid, 
            COALESCE(MAX(b2.bid_price), 0) AS highest_bid
        FROM 
            products p
        LEFT JOIN 
            bids b ON p.id = b.product_id AND b.buyer_id = %s
        LEFT JOIN 
            bids b2 ON p.id = b2.product_id
        WHERE 
            (p.purchased IS NULL OR p.purchased = '') 
            AND p.bidding_deadline > NOW()
        GROUP BY 
            p.id, p.seller_id, p.name, p.description, p.price, p.quantity, p.total_revenue, 
            p.min_bid, p.bidding_deadline, p.purchased, 
            b.bid_price, b2.product_id;  -- Include b2.product_id in the GROUP BY clause
    ''', (buyer_id,))
        products = cursor.fetchall()

        if not products:
            print("No products found for buyer with ID:", buyer_id)
            return "No products found."  # Display a simple error message

        cursor.close()

        return render_template('buyer_view.html', products=products)
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {str(e)}")
        # Return an error message to the client
        return "An error occurred while fetching product data. Please try again later."


if __name__ == "__main__":
    app.run(debug=True)