# E-Commerce Website with Flask

This is a simple e-commerce website implemented using Flask, Flask-Login for user authentication, and MySQL for database management. The project includes features such as user registration, login/logout, role-based access control (admin and customer), product management, order placement, reviews, and more.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

1. User Registration and Login:
   - Users can register with a unique username, email, and password.
   - Login functionality with session management using Flask-Login.

2. Role-Based Access Control:
   - Admin role with access to product management, order management, and user management.
   - Customer role with access to view products, place orders, and give reviews.

3. Product Management:
   - Admin can add new products, edit existing products, and remove products from the store.
   - Customers can view available products and their details.

4. Order Placement:
   - Customers can add products to their cart and place orders.
   - Admin can view and manage orders placed by customers.

5. Reviews:
   - Customers can give ratings and reviews for products they have purchased.

6. Database Management:
   - Uses MySQL for storing user information, products, orders, and reviews.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/e-commerce-flask.git
2. Install dependencies
   ```bash
   pip install -r requirements.txt

## Usage

1. Run the Flask application:
   ```bash
   python app.py
2. Register a new user or use an existing user to login.
     To grant admin access to a user, execute the following SQL query in MySQL Workbench or any MySQL client:
     ```
     UPDATE users
    SET role = 'admin' 
    WHERE username = 'ricky';
    ```
    Change the username.

3. In app.py change the username and password.
   ```
   db = pymysql.connect(host='localhost', user='ricky', password='mysql@root', database='e_commerce')
4. Also change the premission in the queries file
     ```
     CREATE USER 'ricky'@'localhost' IDENTIFIED BY 'mysql@root';
    GRANT ALL PRIVILEGES ON e_commerce.* TO 'ricky'@'localhost';
    FLUSH PRIVILEGES;
     ```
     Change 'ricky' to your username.
   
