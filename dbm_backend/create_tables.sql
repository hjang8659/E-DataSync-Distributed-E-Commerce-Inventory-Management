USE mydatabase;
--CREATE TABLE Suppliers (brand_name VARCHAR(500) primary key, address TEXT, description TEXT, founding_year INT, num_of_products INT);
--CREATE TABLE Products (product_name VARCHAR(500) primary key, category TEXT, sub_category TEXT, brand VARCHAR(500), sale_price INT, market_price INT, type TEXT, rating INT, description TEXT, foreign key (brand) references Suppliers(brand_name));
DROP TABLE Suppliers, Products;

--
USE mydatabase2;
--CREATE TABLE Suppliers (brand_name VARCHAR(500) primary key, address TEXT, description TEXT, founding_year INT, num_of_products INT);
--CREATE TABLE Products (product_name VARCHAR(500) primary key, category TEXT, sub_category TEXT, brand VARCHAR(500), sale_price INT, market_price INT, type TEXT, rating INT, description TEXT, foreign key (brand) references Suppliers(brand_name));
DROP TABLE Suppliers, Products;
