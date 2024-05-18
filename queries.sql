CREATE DATABASE e_commerce;

USE e_commerce;

-- Users table
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL
);

ALTER TABLE users ADD COLUMN role VARCHAR(255) DEFAULT 'customer';

ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);

-- Products table
CREATE TABLE products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2) NOT NULL
);

ALTER TABLE products ADD COLUMN quantity INT DEFAULT 0;

ALTER TABLE products ADD COLUMN average_rating DECIMAL(3, 2) DEFAULT 0.0;

-- Orders table
CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

alter table orders add column total_price DECIMAL(10, 2) DEFAULT 0.0;

-- Order Items table
CREATE TABLE order_items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  product_id INT,
  quantity INT NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Reviews table
CREATE TABLE reviews (
  review_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT,
  user_id INT,
  rating INT NOT NULL,
  comment TEXT,
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

DELIMITER //

CREATE TRIGGER update_average_rating AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
  DECLARE total_ratings INT;
  DECLARE total_rating_sum INT;
  DECLARE average_rating DECIMAL(3, 2);

  SELECT COUNT(*), SUM(rating) INTO total_ratings, total_rating_sum
  FROM reviews
  WHERE product_id = NEW.product_id;

  IF total_ratings > 0 THEN
    SET average_rating = total_rating_sum / total_ratings;
    UPDATE products
    SET average_rating = average_rating
    WHERE product_id = NEW.product_id;
  END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE PROCEDURE place_order(
  IN p_user_id INT,
  IN p_product_id INT,
  IN p_quantity INT
)
BEGIN
  DECLARE total_price DECIMAL(10, 2);

  -- Calculate total price
  SELECT price * p_quantity INTO total_price
  FROM products
  WHERE product_id = p_product_id;

  -- Check if there is sufficient stock
  SELECT quantity INTO @current_stock
  FROM products
  WHERE product_id = p_product_id;

  IF @current_stock >= p_quantity THEN
    -- Insert into orders table
    INSERT INTO orders (user_id, total_price)
    VALUES (p_user_id, total_price);

    -- Get the last inserted order_id
    SET @order_id = LAST_INSERT_ID();

    -- Insert into order_items table
    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES (@order_id, p_product_id, p_quantity, total_price);

    -- Update stock in products table
    UPDATE products
    SET quantity = quantity - p_quantity
    WHERE product_id = p_product_id;

    SELECT 'Order placed successfully' AS status;
  ELSE
    SELECT 'Insufficient stock' AS status;
  END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE PROCEDURE delete_product_and_orders(
  IN p_product_id INT
)
BEGIN
  -- Delete related order items
  DELETE FROM order_items
  WHERE product_id = p_product_id;
	
  -- Delete the review
  DELETE FROM reviews
  where product_id = p_product_id;
  
  -- Delete the product
  DELETE FROM products
  WHERE product_id = p_product_id;

END;
//

DELIMITER ;



CREATE USER 'ricky'@'localhost' IDENTIFIED BY 'mysql@root';
GRANT ALL PRIVILEGES ON e_commerce.* TO 'ricky'@'localhost';
FLUSH PRIVILEGES;

-- Queries

select * from users;

select * from products;

select * from orders;

select * from order_itemsm

select * from reviews;

UPDATE users
SET role = 'admin'
WHERE username = 'ricky';

UPDATE users
SET role = 'admin'
WHERE username = 'fawaz';
