from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysql'

# Configure the MySQL connection
db = pymysql.connect(host='localhost', user='ricky', password='mysql@root', database='e_commerce')

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.init_app(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    # Retrieve user from the database based on user_id
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()

    if user_data:
        user = User()
        user.id = user_data[0]  # user_id is the first column
        user.username = user_data[1]  # username is the second column
        user.email = user_data[2]  # email is the third column
        user.role = user_data[3]  # role is the fourth column
        user.password_hash = user_data[4]  # password_hash is the fifth column
        return user

# ... (existing code)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

        if user_data and check_password_hash(user_data[4], password):  # Assuming 'password_hash' is the fifth column
            # Existing user login
            user = User()
            user.id = user_data[0]  # user_id is the first column
            user.username = user_data[1]  # username is the second column
            user.email = user_data[2]  # email is the third column
            user.role = user_data[3]  # role is the fourth column
            login_user(user)

            if user.role == 'admin':
                flash(f"Welcome, {user.username} (Admin)!", 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f"Welcome, {user.username} (Customer)!", 'success')
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if the user already exists
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', error="Username already exists. Choose a different one.")

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Insert the new user into the database
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, email, role, password_hash) VALUES (%s, %s, %s, %s)",
                           (username, email, 'customer', hashed_password))
            db.commit()

            # Log in the newly registered user
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            user = User()
            user.id = user_data[0]  # user_id is the first column
            user.username = user_data[1]  # username is the second column
            user.email = user_data[2]  # email is the third column
            user.role = user_data[3]  # role is the fourth column
            login_user(user)

            return redirect(url_for('customer_dashboard'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        if current_user.username == 'admin':  # You can replace this condition with your own logic
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    # Retrieve products and orders from the database
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT product_id, product_name, price, quantity FROM products")
        products = cursor.fetchall()

        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()

        # Fetch reviews for each product
        for product in products:
            cursor.execute("SELECT * FROM reviews WHERE product_id = %s", (product['product_id'],))
            product['reviews'] = cursor.fetchall()

    return render_template('admin_dashboard.html', products=products, orders=orders)

    
def get_available_products():
    products = []
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching available products: {e}")
    finally:
        return products
    
def get_ordered_items(user_id):
    ordered_items = []
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            # Assuming you have a table named 'orders' to store order information
            # Adjust the query based on your data model
            query = """
                SELECT p.product_name, o.quantity, p.price
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.user_id = %s
            """
            cursor.execute(query, (user_id,))
            ordered_items = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching ordered items: {e}")
    finally:
        return ordered_items
    

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    if current_user.is_authenticated and current_user.role == 'customer':
        # Fetch data for available products and ordered items
        products = get_available_products()  # Implement this function to retrieve products
        order_items = get_ordered_items(current_user.id)  # Implement this function to retrieve ordered items

        # Print or log the data to check
        print("Available Products:", products)
        print("Ordered Items:", order_items)

        return render_template('customer_dashboard.html', products=products, order_items=order_items)
    else:
        flash('Access denied. You must be a customer to view this page.', 'error')
        return redirect(url_for('login'))
    
@app.route('/order_product/<int:product_id>', methods=['POST'])
@login_required
def order_product(product_id):
    try:
        if request.method == 'POST':
            quantity = int(request.form['quantity'])
            user_id = current_user.id

            # Call the stored procedure to place the order
            with db.cursor() as cursor:
                cursor.callproc('place_order', (user_id, product_id, quantity))
                db.commit()

        # Redirect back to the customer dashboard after placing the order
        return redirect(url_for('customer_dashboard'))

    except BadRequestKeyError:
        # Redirect with an error flash message if 'quantity' is not present in the form data
        flash('Invalid request. Please try again.', 'error')
        return redirect(url_for('customer_dashboard'))

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    # Fetch the product from the database based on product_id
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

    if request.method == 'POST':
        # Update the product in the database based on the form data
        product_name = request.form['product_name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])

        with db.cursor() as cursor:
            cursor.execute("UPDATE products SET product_name = %s, price = %s, quantity = %s WHERE product_id = %s",
                           (product_name, price, quantity, product_id))
            db.commit()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product)

@app.route('/remove_product/<int:product_id>')
@login_required
def remove_product(product_id):
    # Remove the product and related records from the database
    with db.cursor() as cursor:
        try:
            # Call the stored procedure to delete the product and related order items
            cursor.callproc('delete_product_and_orders', (product_id,))
            db.commit()
            flash('Product removed successfully!', 'success')
        except Exception as e:
            # Handle any exceptions, and flash an error message
            print(e)
            db.rollback()
            flash('Error removing the product.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        quantity = request.form['quantity']

        # Insert the new product into the database
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO products (product_name, price, quantity) VALUES (%s, %s, %s)",
                           (product_name, price, quantity))
            db.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')

def get_order_details(order_id):
    """
    Get order details including order items for a specific order_id.

    Parameters:
    - order_id: The ID of the order.

    Returns:
    - order_details: A dictionary containing order information and items.
    """
    order_details = {}

    # Fetch order details
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Replace the following query with your actual query
        cursor.execute("SELECT * FROM orders WHERE order_id = %s AND user_id = %s", (order_id, current_user.id))
        order_details['order'] = cursor.fetchone()

    # Fetch order items
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        # Replace the following query with your actual query
        cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        order_details['items'] = cursor.fetchall()

    return order_details

@app.route('/view_orders')
@login_required
def view_orders():
    # Retrieve orders from the database
    with db.cursor() as cursor:
        # Modify the query to join the orders and order_items tables
        cursor.execute("""
                        SELECT orders.order_id, orders.order_date, order_items.product_id, order_items.quantity, order_items.price, products.product_name
                        FROM orders
                        JOIN order_items ON orders.order_id = order_items.order_id
                        JOIN products ON order_items.product_id = products.product_id
                    """)
        orders = cursor.fetchall()

    print(orders)  # Print orders to the console for debugging

    return render_template('view_orders.html', orders=orders)

@app.route('/update_stock', methods=['GET', 'POST'])
@login_required
def update_stock():
    if request.method == 'POST':
        # Update the stock in the database based on the form data
        product_id = int(request.form['product_id'])
        new_stock = int(request.form['new_stock'])

        with db.cursor() as cursor:
            cursor.execute("UPDATE products SET stock = %s WHERE product_id = %s", (new_stock, product_id))
            db.commit()

        flash('Stock updated successfully!', 'success')

    # Retrieve the product information for the form
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

    return render_template('update_stock.html', products=products)

@app.route('/product_reviews')
@login_required
def product_reviews():
    # Fetch product details and reviews
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT products.product_id, product_name, price, 
                   COALESCE(AVG(rating), 0) AS average_rating, COUNT(reviews.review_id) AS review_count
            FROM products
            LEFT JOIN reviews ON products.product_id = reviews.product_id
            GROUP BY products.product_id, product_name, price
        """)
        products = cursor.fetchall()

    # Fetch individual reviews for each product
    for product in products:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT rating, comment
                FROM reviews
                WHERE product_id = %s
            """, (product['product_id'],))
            product['reviews'] = cursor.fetchall()

    return render_template('product_reviews.html', products=products)

@app.route('/view_products')
@login_required
def view_products():
    # Retrieve products from the database
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

    return render_template('view_products.html', products=products)

@app.route('/give_review', methods=['GET', 'POST'])
@login_required
def give_review():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        rating = int(request.form['rating'])
        comment = request.form['comment']

        # Insert the review into the database
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)",
                           (product_id, current_user.id, rating, comment))
            db.commit()

        flash('Review submitted successfully!', 'success')

        # Redirect to the customer dashboard after submitting the review
        return redirect(url_for('customer_dashboard'))

    # Retrieve the products for which the customer can give reviews
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

    return render_template('give_review.html', products=products)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)