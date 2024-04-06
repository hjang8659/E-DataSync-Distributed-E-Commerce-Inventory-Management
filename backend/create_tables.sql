USE mydatabase;

DROP TABLE IF EXISTS suppliers, products, orders, order_details;

CREATE TABLE suppliers (
    brand_name VARCHAR(500) PRIMARY KEY,
    address TEXT,
    description TEXT,
    founding_year INT UNSIGNED,
    num_of_products INT UNSIGNED
);

CREATE TABLE products (
    product_name VARCHAR(500) PRIMARY KEY,
    category TEXT,
    sub_category TEXT,
    brand_name VARCHAR(500) NOT NULL,
    sale_price INT UNSIGNED,
    market_price INT UNSIGNED,
    type TEXT,
    rating INT UNSIGNED,
    description TEXT,
    CONSTRAINT fk_brand_name_suppliers FOREIGN KEY (brand_name) REFERENCES suppliers(brand_name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT UNSIGNED PRIMARY KEY,
    date TEXT,
    total_price INT UNSIGNED
);

CREATE TABLE order_details (
    product_name VARCHAR(500),
    order_id INT UNSIGNED,
    PRIMARY KEY (product_name, order_id),
    CONSTRAINT fk_product_name_products FOREIGN KEY (product_name) REFERENCES products(product_name) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_id_orders FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE
);

USE mydatabase2;

DROP TABLE IF EXISTS suppliers, products, orders, order_details;

CREATE TABLE suppliers (
    brand_name VARCHAR(500) PRIMARY KEY,
    address TEXT,
    description TEXT,
    founding_year INT UNSIGNED,
    num_of_products INT UNSIGNED
);

CREATE TABLE products (
    product_name VARCHAR(500) PRIMARY KEY,
    category TEXT,
    sub_category TEXT,
    brand_name VARCHAR(500) NOT NULL,
    sale_price INT UNSIGNED,
    market_price INT UNSIGNED,
    type TEXT,
    rating INT UNSIGNED,
    description TEXT,
    CONSTRAINT fk_brand_name_suppliers FOREIGN KEY (brand_name) REFERENCES suppliers(brand_name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT UNSIGNED PRIMARY KEY,
    date TEXT,
    total_price INT UNSIGNED
);

CREATE TABLE order_details (
    product_name VARCHAR(500),
    order_id INT UNSIGNED,
    PRIMARY KEY (product_name, order_id),
    CONSTRAINT fk_product_name_products FOREIGN KEY (product_name) REFERENCES products(product_name) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_id_orders FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE
);

