USE mydatabase;

DROP TABLE IF EXISTS suppliers, products, orders, order_details;

CREATE TABLE suppliers (
    brand_name VARCHAR(500) PRIMARY KEY,
    address TEXT,
    brand_description TEXT,
    founding_year INT UNSIGNED,
    num_of_products INT UNSIGNED
);

CREATE TABLE products (
    product_name VARCHAR(500) PRIMARY KEY,
    category TEXT,
    sub_category TEXT,
    brand VARCHAR(500) NOT NULL,
    sale_price INT UNSIGNED,
    market_price INT UNSIGNED,
    type TEXT,
    rating INT UNSIGNED,
    product_description TEXT,
    CONSTRAINT fk_brand_suppliers FOREIGN KEY (brand) REFERENCES suppliers(brand_name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT UNSIGNED PRIMARY KEY,
    date TEXT,
    total_price INT UNSIGNED
);

CREATE TABLE order_details (
    product VARCHAR(500),
    order_ INT UNSIGNED,
    PRIMARY KEY (product, order_),
    CONSTRAINT fk_product_products FOREIGN KEY (product) REFERENCES products(product_name) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_orders FOREIGN KEY (order_) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE
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
    brand VARCHAR(500) NOT NULL,
    sale_price INT UNSIGNED,
    market_price INT UNSIGNED,
    type TEXT,
    rating INT UNSIGNED,
    description TEXT,
    CONSTRAINT fk_brand_suppliers FOREIGN KEY (brand) REFERENCES suppliers(brand_name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT UNSIGNED PRIMARY KEY,
    date TEXT,
    total_price INT UNSIGNED
);

CREATE TABLE order_details (
    product VARCHAR(500),
    order_ INT UNSIGNED,
   	PRIMARY KEY (product, order_),
    CONSTRAINT fk_product_products FOREIGN KEY (product) REFERENCES products(product_name) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_orders FOREIGN KEY (order_) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE
);
