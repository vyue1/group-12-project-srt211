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
            print("Email:", user[2])
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

@app.route('/buyer_page',methods=['GET','POST'])
def buyer_page():
    return render_template('buyer_page.html')


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

# @app.route('/view_products', methods=('GET','POST'))
# def seller_view():
    
#     cursor = conn.cursor()
#     seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

#     # Fetch products available for bidding from the database
#     cursor.execute('SELECT p.*, b.bid_price FROM products p LEFT JOIN bids b ON p.id = b.product_id WHERE p.seller_id = %s', (seller_id,))
#     products = cursor.fetchall()

#     # Process each product individually
#     for product in products:
#         if request.method == "POST":
#             # Check if bidding deadline has passed and update purchase status if necessary
#             if product['bidding_deadline'] < datetime.now():
#                 if product['bid_price'] is not None:
#                     new_quantity = product['quantity'] - 1
#                     cursor.execute("UPDATE products SET purchased = 'yes', quantity = %s WHERE id = %s", (new_quantity, product['id']))
#                     conn.commit()

#     cursor.close()

#     return render_template('seller_view.html', products=products)



@app.route('/view_products', methods=['GET', 'POST'])
def seller_view():
    try:
        if 'user_id' in session:
            seller_id = session['user_id']
        
            cursor = conn.cursor()
            #seller_id = session.get('user_id')  # Retrieve the current seller's ID from the session

             # Update purchase status automatically for products with expired bidding deadlines
            cursor.execute('''
                UPDATE products 
                SET purchased = 'yes' 
                WHERE seller_id = %s 
                AND bidding_deadline < NOW() 
                AND purchased != 'yes'
            ''', (seller_id,))
            conn.commit()



            # Fetch products available for the seller from the database along with the highest bid price
            cursor.execute('''
                SELECT p.*, 
                    (SELECT MAX(bid_price) FROM bids WHERE product_id = p.id) AS bid_price
                FROM products p
                WHERE p.seller_id = %s
            ''', (seller_id,))
            products = cursor.fetchall()
            session['products'] = products

            if not products:
                print("No products found for seller with ID:", seller_id)
            else:
                print("Products found:", products)

            # # Check if any bids have expired and update purchase status if necessary
            # for product in products:
            #     if product['bidding_deadline'] < datetime.now() and product['purchased'] != 'yes':
            #         # Update the purchase status in the database
            #         cursor.execute("UPDATE products SET purchased = 'yes' WHERE id = %s", (product['id'],))
            #         conn.commit()

            cursor.close()

            return render_template('seller_view.html', products=products)
        else:
            return "You need to log in to view your products."

        #return render_template('seller_view.html', products=products)
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {str(e)}")
        # Return a generic error message
        return "An error occurred while fetching product data. Please try again later."




if __name__ == "__main__":
    app.run(debug=True)