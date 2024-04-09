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

        

        
        if existing_user:
            if existing_user[1] == username:
                return render_template('signup.html', message='Username already taken. Please choose a different one.')
            elif existing_user[2] == email:
                return render_template('signup.html', message='Email already taken. Please choose a different one.')
            
        
        is_seller = 'seller' if role == 'seller' else 'buyer'
        
        if is_seller=='seller':
            session['is_seller']='seller'
        else:
            session['is_seller']='buyer'
    # Insert user into database with the  role
        cursor.execute('INSERT INTO users (username, email, password, is_seller) VALUES (%s, %s, %s, %s)',
                   (username, email, hashed_password, is_seller))
        
        conn.commit()

        # Set session variables based on the user's role
        if is_seller == 'seller':
            session['is_seller'] = True
        else:
            session['is_buyer'] = True
        return redirect(url_for('home'))

    
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        cursor = conn.cursor()
        cursor.execute('SELECT id, password, is_seller FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        
        
        if user and bcrypt.check_password_hash(user[1], password):
            session['username'] = username
            session['user_id'] = user[0]
            session['is_seller'] = user[2]

            # # Print out user information
            print("ID:", user[0])
            #print("Username:", user[])
            print("is_seller:", user[2])
            # print("Is Seller:", user[4]) 
            # print("column:",user[0])
            # print('column')

            # Debugging output
            print("User ID:", user[0])
            print("Role:", user[2])

        
            if  user[2] == 'seller':
                session['seller_id'] = user[0]
                return redirect(url_for('seller_page'))
            else:
                session['buyer_id'] = user[0]
                return redirect(url_for('buyer_page'))
            
            
            # # if user.is_seller == 'seller':
            #     return redirect(url_for('seller_page'))
            # else:
            #     return redirect(url_for('buyer_page'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')

    return render_template('login.html')

@app.route('/seller_page')
def seller_page():
    # Check if the current user is a seller
        
        if session.get('is_seller') != 'seller':
            # Redirect buyers or unauthorized users to a different page
            return redirect(url_for('login'))
    #  for rendering the seller page
        return render_template('seller_page.html')



@app.route('/buyer_account')
def view_buyer_account():
    # Check if user is logged in
    # Check if user is logged in and is a buyer
    if 'user_id' in session and session.get('is_seller') == 'buyer':
        user_id = session['user_id']
        
        # Query the database to fetch the buyer's information based on the user_id and is_seller column
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = %s ', (user_id,))
        buyer_info = cursor.fetchone()
        cursor.close()

        if buyer_info:
            return render_template('view_buyer_account.html', buyer=buyer_info)
        else:
            return "Buyer account not found."
    else:
        return "You need to log in to view your buyer account."

# @app.route('/delete/<int:id>',methods=['GET'])
# def delete_user(id):
#     cursor=conn.cursor()
#     cursor.execute('DELETE from users where id=%s',(id,))
#     conn.commit()
#     # conn.close()
#     return redirect(url_for('home'))

@app.route('/delete/<int:id>',methods=['GET'])

def delete_user(id):
    try:
        cursor = conn.cursor()

        # Delete bids associated with the user
        cursor.execute('DELETE FROM bids WHERE buyer_id = %s', (id,))

        # Then, delete the user
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))

        # Commit the transaction
        conn.commit()

        # Close the cursor
        cursor.close()

        return redirect(url_for('view_buyer_account'))
    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while deleting the user."


@app.route('/update/<int:id>',methods=['GET','POST'])
def update_account(id):
    if request.method == 'POST':
        cursor = conn.cursor()
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = cursor.fetchone()

        if user:
            # Create variables for updated values
            updated_username = name if name else user[1]
            updated_email = email if email else user[2]
            updated_password = bcrypt.generate_password_hash(password).decode('utf-8') if password else user[3]

            # Execute the update query
            cursor.execute('UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s',
                           (updated_username, updated_email, updated_password, id))
            conn.commit()

            return redirect(url_for('view_buyer_account')) 
        else:
            # Handle case where user is not found
            return "User not found."
    else:
        # Render the form to update user account
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = cursor.fetchone()

        if user:
            return render_template('update_user.html', user=user)
        else:
            # Handle case where user is not found
            return "User not found."
        

@app.route('/update_seller_account/<int:id>',methods=['GET','POST'])
def update_seller_account(id):
    if request.method == 'POST':
        cursor = conn.cursor()
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = cursor.fetchone()

        if user:
            # Create variables for updated values
            updated_username = name if name else user[1]
            updated_email = email if email else user[2]
            updated_password = bcrypt.generate_password_hash(password).decode('utf-8') if password else user[3]

            # Execute the update query
            cursor.execute('UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s',
                           (updated_username, updated_email, updated_password, id))
            conn.commit()

            return redirect(url_for('view_seller_account')) 
        else:
            # Handle case where user is not found
            return "User not found."
    else:
        # Render the form to update user account
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = cursor.fetchone()

        if user:
            return render_template('update_seller_account.html', user=user)
        else:
            # Handle case where user is not found
            return "User not found."
        
@app.route('/delete_seller/<int:id>', methods=['GET'])
def delete_seller(id):
    try:
        cursor = conn.cursor()

        # Delete bids associated with the seller
        cursor.execute('DELETE FROM bids WHERE buyer_id = %s', (id,))

        # Update the seller_id to NULL in the products table for products associated with the seller
        cursor.execute('UPDATE products SET seller_id = NULL WHERE seller_id = %s', (id,))

        # Then, delete the seller
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))

        # Commit the transaction
        conn.commit()

        # Close the cursor
        cursor.close()

        return redirect(url_for('view_seller_account'))
    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {str(e)}")
        return "An error occurred while deleting the seller."
    

@app.route('/view_seller_account')
def view_seller_account():
    # Check if user is logged in
    if 'user_id' in session and session.get('is_seller') == 'seller':
        user_id = session['user_id']
        
        # Query the database to fetch the buyer's information based on the user_id and is_seller column
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM users WHERE id = %s', (user_id,))
        seller_info = cursor.fetchone()
        cursor.close()

        if seller_info:
            return render_template('view_seller_account.html', seller=seller_info)
        else:
            return "seller account not found."
    else:
        return "You need to log in to view your seller account."

@app.route('/insert_product', methods=['GET', 'POST'])
def insert_product():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if the user is not logged in

    # Check if the user is a seller
    if session.get('is_seller') != 'seller':
        # return "You are not authorized to access this page."
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # Get product details from the form data
        description = request.form['description']
        price = request.form['price']
        # quantity = request.form['quantity']
        name = request.form['name']
        min_bid = request.form['min_bid']
        bidding_deadline = request.form['bidding_deadline']

        # Get seller_id from the session 
        seller_id = session.get('user_id')  

        # Insert the new product into the database
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (seller_id, description, price,quantity, name, min_bid, bidding_deadline) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (seller_id, description, price,0, name, min_bid, bidding_deadline))
        conn.commit()
        cursor.close()

        # Redirect  after inserting the product
        return redirect('view_products')  

    # If the request method is GET, render the insert product form
    return render_template('insert_product.html')



@app.route('/view_products', methods=['GET', 'POST'])
def seller_view():
    try:

        # Check if the current user is a seller
        if session.get('is_seller') != 'seller':
            # Redirect buyers or unauthorized users to a different page
            return redirect(url_for('login'))



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

        current_datetime = datetime.now()  # Calculate current datetime

         # Update total revenue for products with passed bidding deadline and highest bid
        for product in products:
            if product[8] < current_datetime and product[10] > 0:
                cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product[10], product[0]))

        for product in products:

            # Print product details for debugging
            print("Product ID:", product[0])
            print("Bidding Deadline:", product[8])
            print("Purchased Status:", product[9])
            print("Highest Bid Price:", product[10])

            # Check if the deadline has passed and there's no highest bid
            if product[8] < current_datetime and product[9] != 'yes' and product[10] == 0:
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

       

        session['products'] = products

        if not products:
            print("No products found for seller with ID:", seller_id)
            return "No products found."  

        cursor.close()

        return render_template('seller_view.html', products=products,current_datetime=current_datetime)
    except:
        print("An error occurred:")
        # Return an error message to the client
        return "An error occurred while fetching product data. Please try again later."




@app.route('/buyer_page', methods=['GET', 'POST'])
def buyer_page():
    try:
        # Check if the user is logged in as a buyer
        if session.get('is_seller') == 'seller':
            return redirect(url_for('login'))  # Redirect to the login page

        cursor = conn.cursor()
        buyer_id = session.get('user_id')

        # Fetch products available for buyers from the database
        cursor.execute('''
            SELECT p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                   p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased, 
                   COALESCE(MAX(b.bid_price), 0) AS max_bid_price, 
                   COALESCE(SUM(b.bid_price), 0) AS total_bid_price,
                   COALESCE(MAX(CASE WHEN b.buyer_id = %s THEN b.bid_price ELSE NULL END), 0) AS buyer_highest_bid
            FROM products p
            LEFT JOIN bids b ON p.id = b.product_id
            WHERE p.bidding_deadline > %s
            GROUP BY p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                     p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased
        ''', (buyer_id, datetime.now()))  # Filter out products with expired deadlines

        products = cursor.fetchall()

        session['products'] = products
        session['is_buyer'] = True  # Set session to buyer

        # if not products:
        #     print("No products available.")
        #     return "No products found."

        cursor.close()

        return render_template('buyer_page.html', products=products)
    except:
        print("An error occurred:")
        return "An error occurred while fetching product data. Please try again later."





@app.route('/buyer_bid', methods=['GET','POST'])
def buyer_bid():
    try:
        # Retrieve the current buyer's ID from the session
        buyer_id = session.get('user_id')
        
        
        if buyer_id is None:
            return "User ID not found in session. Please log in first."

        # Retrieve the product ID and bid amount from the form data
        product_id = request.form.get('product_id')
        bid_price = request.form.get('bid_price')

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
        if float(bid_price) < min_bid:
            return "Bid doesn't meet the minimum bid requirement."
        
        
        
        # Fetch the highest bid for the product
        cursor.execute('''
            SELECT MAX(bid_price) FROM bids WHERE product_id = %s
        ''', (product_id,))
        highest_bid = cursor.fetchone()[0]

        # Check if the current bid is greater than the highest bid
        if highest_bid is not None and float(bid_price) <= highest_bid:
            return "Someone else has placed a higher bid. Please bid higher."
        
         # If all checks pass,  place the bid
        cursor.execute('''
            INSERT INTO bids (product_id, buyer_id, bid_price) 
            VALUES (%s, %s, %s)
        ''', (product_id, buyer_id, bid_price))
        conn.commit()

        # If all checks pass,  place the bid
       
        session['is_seller'] = 'seller'
        cursor.close()

        #  redirect to a success page or return a success message
        return "Bid placed successfully!"

    except:
        print("An error occurred:")
        # Return an error message to the client
        return "An error occurred while processing the bid. Please try again later."
    



@app.route('/view_bids', methods=['GET', 'POST'])
def view_bids():
    try:
        # Check if the user is logged in as a buyer
        if session.get('is_seller') == 'seller':
            return redirect(url_for('login'))  # Redirect to the login page

        cursor = conn.cursor()
        buyer_id = session.get('user_id')

        # Fetch products with bids placed by the buyer from the database
        cursor.execute('''
                SELECT p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                   p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased, 
                   COALESCE(MAX(b.bid_price), 0) AS max_bid_price, 
                   COALESCE(SUM(b.bid_price), 0) AS total_bid_price,
                   (SELECT MAX(bid_price) FROM bids WHERE product_id = p.id) AS highest_bid
            FROM products p
            LEFT JOIN bids b ON p.id = b.product_id AND b.buyer_id = %s
            WHERE b.buyer_id = %s
            GROUP BY p.id, p.seller_id, p.name, p.description, p.price, p.quantity, 
                     p.total_revenue, p.min_bid, p.bidding_deadline, p.purchased
        ''', (buyer_id, buyer_id))

        products = cursor.fetchall()

        # Update total revenue for products with passed bidding deadline and highest bid
        for product in products:
            if product[8] < datetime.now() and product[10] > 0:
                cursor.execute("UPDATE products SET total_revenue = %s WHERE id = %s", (product[10], product[0]))
                conn.commit()

        session['products'] = products
        session['is_buyer'] = True  # Set session to buyer

        if not products:
            print("No products found.")
            return "No products found."

        cursor.close()

        return render_template('view_bids.html', products=products)
    except:
        print("An error occurred:")
        return "An error occurred while fetching product data. Please try again later."
    
    


@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if request.method == 'POST':
        # Process the updated product details submitted via the form
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Fetch existing product details from the database
        cursor = conn.cursor()
        cursor.execute('SELECT name, description FROM products WHERE id = %s', (product_id,))
        existing_name, existing_description = cursor.fetchone()
        cursor.close()
        
        # Update the product record in the database
        if name:
            updated_name = name
        else:
            updated_name = existing_name
        
        if description:
            updated_description = description
        else:
            updated_description = existing_description
        
        if updated_name or updated_description:
            # Update the product record in the database with the updated name and description
            cursor = conn.cursor()
            cursor.execute('UPDATE products SET name = %s, description = %s WHERE id = %s',
                           (updated_name, updated_description, product_id))
            conn.commit()
            cursor.close()
            
            # Redirect to the seller view page after updating the product
            return redirect(url_for('seller_view'))
        else:
            return "Please enter either the name or description of the product."

    
    # Fetch product details from the database based on the product_id
    cursor = conn.cursor()
    cursor.execute('SELECT name, description FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()

    return render_template('update_product.html', product=product)




@app.route('/update_deadline/<int:product_id>', methods=['GET', 'POST'])
def update_deadline(product_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to the login page if the user is not logged in

    # Check if the user is a seller
    if session.get('is_seller') != 'seller':
        return redirect(url_for('login'))

    # Fetch the product details from the database based on the product_id
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

   

    if request.method == "POST":
        # Get the new bidding deadline from the form data
        description = request.form['description']
        price = request.form['price']
        # quantity = request.form['quantity']
        name = request.form['name']
        min_bid = request.form['min_bid']
        new_deadline = request.form['bidding_deadline']

        # Fetch existing product details from the database
        cursor = conn.cursor()
        cursor.execute("SELECT description, price, quantity, name, min_bid, bidding_deadline FROM products WHERE id = %s", (product_id,))
        existing_description, existing_price, existing_quantity, existing_name, existing_min_bid, existing_bidding_deadline = cursor.fetchone()
        cursor.close()
        
        # Update the product record in the database
        updated_description = description if description else existing_description
        updated_price = price if price else existing_price
        # updated_quantity = quantity if quantity else existing_quantity
        updated_name = name if name else existing_name
        updated_min_bid = min_bid if min_bid else existing_min_bid
        updated_deadline = new_deadline if new_deadline else existing_bidding_deadline

        cursor = conn.cursor()
        cursor.execute("UPDATE products SET description = %s, price = %s,  name = %s, min_bid = %s, bidding_deadline = %s WHERE id = %s",
               (updated_description, updated_price, updated_name, updated_min_bid, updated_deadline, product_id))
        conn.commit()
        cursor.close()

        # Redirect to the seller view page after updating the deadline
        return redirect(url_for('seller_view'))

    # If the request method is GET, render the form for updating the deadline
    return render_template('update_deadline.html', product=product, product_id=product_id)


if __name__ == "__main__":
    app.run(debug=True)
