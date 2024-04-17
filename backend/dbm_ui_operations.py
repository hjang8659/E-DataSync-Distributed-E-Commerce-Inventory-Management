from sqlalchemy import create_engine, text
# from backend.hashing import hash_supplier
from hashing import hash_supplier
import re

class DBMOperations:
    """
    Class to perform database operations.
    """

    def __init__(self):
        """
        Initialize the class with database engines.
        """
        self.hash = hash_supplier()
        self.engines = {
            0: create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase'),
            1: create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase2')
        }

    def _get_supplier_name(self, query):
        """
        Helper function to extract supplier name from query.
        """

        # Search for the column names in the INSERT statement
        columns_match = re.search(r"INSERT INTO suppliers \(([^)]+)\)", query, re.IGNORECASE)
        if not columns_match:
            print("Column names could not be found.")
            return 0

        # Parse the columns from the query and clean up any whitespace
        columns = [column.strip() for column in columns_match.group(1).split(',')]

        # Find index of 'brand_name' in the columns list
        try:
            brand_name_index = columns.index('brand_name')
        except ValueError:
            print("Brand name column could not be found.")
            return 0

        # Extract the corresponding value from the VALUES clause
        values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
        if not values_match:
            print("Values could not be found.")
            return 0

        # Parse the values from the query and remove any surrounding whitespace or quotes
        values = [value.strip().strip("'\"") for value in values_match.group(1).split(',')]

        # Retrieve the 'brand_name' value using the found index
        brand_name = values[brand_name_index]

        return brand_name
    
    def update_query_values(self, query, table_name):
        """
        Update values in an INSERT or UPDATE SQL query based on the column data types from the schema.

        :param query: The original SQL query.
        :param table_name: The table name to fetch schema details for.
        :return: The updated SQL query with values formatted according to their specific data types.
        """
        # Fetch column data types from the database's schema
        schema_query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
        flag, res = self.select(schema_query)
        if not flag or not res:
            raise ValueError("Could not fetch column data types from the database.")
        
        data_type_dict = {item[0]: item[1] for item in res}

        # Detect query type (INSERT or UPDATE)
        if re.search(r"^INSERT", query, re.IGNORECASE):
            return self._update_insert_query_values(query, data_type_dict)
        elif re.search(r"^UPDATE", query, re.IGNORECASE):
            return self._update_update_query_values(query, data_type_dict)
        else:
            raise ValueError("Query must be either INSERT or UPDATE.")

    def _update_insert_query_values(self, query, data_type_dict):
        # Extract and format VALUES for INSERT query
        print(query)
        values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
        columns_match = re.search(r"INSERT INTO\s+[^\s]+\s*\(([^)]+)\)", query, re.IGNORECASE)
        if not values_match or not columns_match:
            raise ValueError("Malformed INSERT query.")
        
        values_list = [val.strip() for val in values_match.group(1).split(',')]
        columns_list = [col.strip() for col in columns_match.group(1).split(',')]
        print(values_list)
        
        if len(columns_list) != len(values_list):
            raise ValueError("Mismatch between number of columns and number of values.")

        new_values = [self._format_value(value.strip("'\""), col, data_type_dict) for col, value in zip(columns_list, values_list)]
        print(new_values)
        new_values_str = ', '.join(new_values)
        updated_query = re.sub(r"VALUES\s*\([^)]+\)", f"VALUES ({new_values_str})", query, flags=re.IGNORECASE)
        return updated_query

    def _update_update_query_values(self, query, data_type_dict):
        """
        Extract and format the SET part of an UPDATE query while preserving the WHERE clause.
        """
        # Extract the entire portion after SET up to an optional WHERE or the end of the query
        # Extract the SET part and format it
        set_match = re.search(r"SET\s+(.+?)(?=\sWHERE\s|\s*$)", query, re.IGNORECASE)
        if not set_match:
            raise ValueError("Malformed UPDATE query.")
        
        set_list = [pair.strip() for pair in set_match.group(1).split(',')]
        new_set_parts = []
        for pair in set_list:
            column, value = pair.split('=')
            column = column.strip()
            value = value.strip().strip("'\"")  # Remove existing quotes for uniformity
            formatted_value = self._format_value(value, column, data_type_dict)
            new_set_parts.append(f"{column} = {formatted_value}")

        new_set_str = ', '.join(new_set_parts)

        # Check for and format the WHERE clause
        where_match = re.search(r"WHERE\s+(.+)$", query, re.IGNORECASE)
        where_clause = ""
        if where_match:
            where_clause = where_match.group(1)
            for column, dtype in data_type_dict.items():
                if dtype in ["text", "varchar", "date"]:
                    # Quote string values in WHERE clause
                    pattern = rf"(\b{column}\b\s*=\s*)([^\s]+)"
                    def replacement(match):
                        # Extract the parts from the regex match
                        before_value = match.group(1)
                        value = match.group(2).strip('\'')
                        
                        # Prepare the value with quotes, avoiding backslashes in f-string expressions
                        quoted_value = f"'{value}'"
                        
                        # Return the concatenation of the parts
                        return before_value + quoted_value

                    # Apply the replacement function
                    where_clause = re.sub(pattern, replacement, where_clause, flags=re.IGNORECASE)

        # Construct the updated query
        before_set = query[:set_match.start()]  # Everything before SET
        after_where = query[where_match.end():] if where_match else ''  # Anything after WHERE clause
        updated_query = f"{before_set}SET {new_set_str} WHERE {where_clause}{after_where}"
        return updated_query

    def _format_value(self, value, column, data_type_dict):
        # Helper to format value based on column's data type
        if column not in data_type_dict:
            print("Error:", column + " not found")
        
        if column in data_type_dict and data_type_dict[column] in ["date", "text", "varchar"]:
            return f"'{value}'"  # Ensure value is safely quoted
        return value

    def insert(self, query):
        """
        Insert record into hashed database after hashing supplier name.
        """
        # Getting table name
        match = re.search(r"INSERT INTO\s+([a-zA-Z0-9_]+)", query, re.IGNORECASE)
        if match:
            table_name = match.group(1)
        else:
            print("Table name could not be found.")
            return 0
        
        query = self.update_query_values(query, table_name)
        print(query)
        
        if table_name == "suppliers":
            # Looks like it can only insert 1 value at a time
            supplier_name = self._get_supplier_name(query)
            print(supplier_name)
            db_index = self.hash.generate_hash(supplier_name)
            print(db_index)

        elif table_name == "products":
            # Join products and suppliers as a view, then get supplier name from it and database index
            # products "brand" FK connects to "brand_name" PK in suppliers

            # Search for the column names in the INSERT statement
            columns_match = re.search(r"INSERT INTO products \(([^)]+)\)", query, re.IGNORECASE)
            if not columns_match:
                print("Column names could not be found.")
            else:
                # Parse the columns from the query and clean up any whitespace
                columns = [column.strip() for column in columns_match.group(1).split(',')]

                # Find index of 'brand_name' in the columns list
                try:
                    brand_name_index = columns.index('brand')
                except ValueError:
                    print("Brand name column could not be found.")
                else:
                    # Extract the corresponding value from the VALUES clause
                    values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
                    if not values_match:
                        print("Values could not be found.")
                    else:
                        # Since the values might include commas inside quotes, handling this requires a more robust approach:
                        values = re.findall(r"[^,]+", values_match.group(1))

                        # Parse the values and clean them
                        values = [value.strip().strip("'\"") for value in values]

                        # Retrieve the 'brand_name' value using the found index
                        if len(values) >= brand_name_index:  # Ensure we have enough values
                            brand = values[brand_name_index]
                            print(f"Brand Name: {brand}")
                            db_index = self.hash.generate_hash(brand)
                            print(db_index)

        elif table_name == "order_details":
            # Join order_details to the products view to get the supplier name and database index
            # product name in the "product" attribute

            columns_match = re.search(r"INSERT INTO order_details \(([^)]+)\)", query, re.IGNORECASE)
            if not columns_match:
                print("Column names could not be found.")
            else:
                # Parse the columns from the query and clean up any whitespace
                columns = [column.strip() for column in columns_match.group(1).split(',')]

                # Find index of 'product' in the columns list
                try:
                    product_name_index = columns.index('product')
                except ValueError:
                    print("product name column could not be found.")
                else:
                    # Extract the corresponding value from the VALUES clause
                    values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
                    if not values_match:
                        print("Values could not be found.")
                    else:
                        # Since the values might include commas inside quotes, handling this requires a more robust approach:
                        values = re.findall(r"[^,]+", values_match.group(1))

                        # Parse the values and clean them
                        values = [value.strip().strip("'\"") for value in values]

                        # Retrieve the 'brand_name' value using the found index
                        if len(values) >= product_name_index:  # Ensure we have enough values
                            product = values[product_name_index]
                            print(f"Product Name: {product}")
                            # Search by primary key for row, then obtain suppliers name
                            query2 = f"SELECT brand FROM products WHERE product_name = '{product}'"
                            flag, result = self.select(query2)
                            if result == [] or result is None:
                                raise ValueError(product + " not found")
                            print(result)
                            db_index = self.hash.generate_hash(result[0][0])
                            print(db_index)
                        else:
                            print("Product could not be found.")
                            return 0

        elif table_name == "orders":
            # WORKS
            # ex query/ INSERT INTO orders (date, order_id, total_price) VALUES ('2024-04-10', 1, 100);
            # Insert into database based on odd/even orders_id value
            # database 0 if even, database 1 if odd
            # Regular expression to find and capture the order_id
            columns_match = re.search(r"INSERT INTO orders \(([^)]+)\)", query, re.IGNORECASE)
            if not columns_match:
                print("Column names could not be found.")
                return 0

            columns = [column.strip() for column in columns_match.group(1).split(',')]
            
            # Find index of 'order_id' in the columns list
            try:
                order_id_index = columns.index('order_id')
            except ValueError:
                print("Order ID column could not be found.")
                return 0

            # Extract the corresponding value from the VALUES clause
            values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
            if not values_match:
                print("Values could not be found.")
                return 0

            values = [value.strip().strip("'\"") for value in values_match.group(1).split(',')]
            
            try:
                order_id = int(values[order_id_index])
            except (IndexError, ValueError) as e:
                print(f"Error parsing order ID: {e}")
                return 0

            db_index = order_id % 2

            with self.engines[db_index].connect() as con:
                try:
                    con.execute(text(query))
                    con.commit()
                    con.close()
                except Exception as e:
                    print(e)
                    return 0
                
            db_index = 1 - db_index 
            print("ok")
        
        else: 
            print("Table not found:", table_name)
        
        with self.engines[db_index].connect() as con:
            try:
                con.execute(text(query))
                con.commit()
                con.close()
                return 1
            except Exception as e:
                print(e)
                return 0

    def _execute_query(self, engine, query):
        """
        Execute query on a given engine.
        """
        with engine.connect() as con:
            res = con.execute(text(query))
            con.commit()
            con.close()
            return res
        
    def select(self, query):
        """
        Perform select operation on both databases and return combined results if successful.
        """
        try: 
            
            results = []
            for engine in self.engines.values():
                results.extend(self._execute_query(engine, query))
            print(results)
            return 1, results
        except Exception as e:
            print(e)
            return 0, None

    def update(self, query):
        """
        Modify records in both databases.
        """
        try:
            match = re.search(r"UPDATE\s+([^\s\(\)\;]+)", query, re.IGNORECASE)
            if not match:
                raise ValueError("Table name could not be found in the query.")

            table_name = match.group(1)

            query = self.update_query_values(query, table_name)
            print(query)
            for engine in self.engines.values():
                self._execute_query(engine, query)
            return 1
        except Exception as e:
            print(e)
            return 0

    def delete(self, query):
        """
        Delete records from both databases.
        """
        try:
            for engine in self.engines.values():
                self._execute_query(engine, query)
            return 1
        except Exception as e:
            print(e)
            return 0

if __name__ == '__main__':
    opr = DBMOperations()

    supplier_queries = [
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand1', 'Address1', 'Description1', 2000, 50)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand2', 'Address2', 'Description2', 1995, 60)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand3', 'Address3', 'Description3', 2010, 40)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand4', 'Address4', 'Description4', 2008, 70)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand5', 'Address5', 'Description5', 2002, 55)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand6', 'Address6', 'Description6', 1998, 45)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand7', 'Address7', 'Description7', 2005, 65)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand8', 'Address8', 'Description8', 2012, 75)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand9', 'Address9', 'Description9', 2004, 80)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand10', 'Address10', 'Description10', 2006, 90)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand11', 'Address11', 'Description11', 1997, 85)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand12', 'Address12', 'Description12', 2003, 95)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand13', 'Address13', 'Description13', 2011, 100)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand14', 'Address14', 'Description14', 2001, 110)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand15', 'Address15', 'Description15', 2009, 120)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand16', 'Address16', 'Description16', 1999, 130)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand17', 'Address17', 'Description17', 2007, 140)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand18', 'Address18', 'Description18', 2013, 150)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand19', 'Address19', 'Description19', 2000, 160)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand20', 'Address20', 'Description20', 1995, 170)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand21', 'Address21', 'Description21', 2010, 180)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand22', 'Address22', 'Description22', 2008, 190)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand23', 'Address23', 'Description23', 2002, 200)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand24', 'Address24', 'Description24', 1998, 210)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand25', 'Address25', 'Description25', 2005, 220)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand26', 'Address26', 'Description26', 2012, 230)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand27', 'Address27', 'Description27', 2004, 240)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand28', 'Address28', 'Description28', 2006, 250)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand29', 'Address29', 'Description29', 1997, 260)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand30', 'Address30', 'Description30', 2003, 270)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand31', 'Address31', 'Description31', 2011, 280)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand32', 'Address32', 'Description32', 2001, 290)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand33', 'Address33', 'Description33', 2009, 300)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand34', 'Address34', 'Description34', 1999, 310)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand35', 'Address35', 'Description35', 2007, 320)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand36', 'Address36', 'Description36', 2013, 330)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand37', 'Address37', 'Description37', 2000, 340)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand38', 'Address38', 'Description38', 1995, 350)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand39', 'Address39', 'Description39', 2010, 360)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand40', 'Address40', 'Description40', 2008, 370)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand41', 'Address41', 'Description41', 2002, 380)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand42', 'Address42', 'Description42', 1998, 390)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand43', 'Address43', 'Description43', 2005, 400)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand44', 'Address44', 'Description44', 2012, 410)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand45', 'Address45', 'Description45', 2004, 420)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand46', 'Address46', 'Description46', 2006, 430)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand47', 'Address47', 'Description47', 1997, 440)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand48', 'Address48', 'Description48', 2003, 450)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand49', 'Address49', 'Description49', 2011, 460)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand50', 'Address50', 'Description50', 2001, 470)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand51', 'Address51', 'Description51', 2009, 480)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand52', 'Address52', 'Description52', 1999, 490)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand53', 'Address53', 'Description53', 2007, 500)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand54', 'Address54', 'Description54', 2013, 510)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand55', 'Address55', 'Description55', 2000, 520)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand56', 'Address56', 'Description56', 1995, 530)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand57', 'Address57', 'Description57', 2010, 540)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand58', 'Address58', 'Description58', 2008, 550)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand59', 'Address59', 'Description59', 2002, 560)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand60', 'Address60', 'Description60', 1998, 570)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand61', 'Address61', 'Description61', 2005, 580)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand62', 'Address62', 'Description62', 2012, 590)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand63', 'Address63', 'Description63', 2004, 600)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand64', 'Address64', 'Description64', 2006, 610)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand65', 'Address65', 'Description65', 1997, 620)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand66', 'Address66', 'Description66', 2003, 630)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand67', 'Address67', 'Description67', 2011, 640)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand68', 'Address68', 'Description68', 2001, 650)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand69', 'Address69', 'Description69', 2009, 660)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand70', 'Address70', 'Description70', 1999, 670)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand71', 'Address71', 'Description71', 2007, 680)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand72', 'Address72', 'Description72', 2013, 690)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand73', 'Address73', 'Description73', 2000, 700)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand74', 'Address74', 'Description74', 1995, 710)",
    "INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand75', 'Address75', 'Description75', 2010, 720)"
]

    product_queries = [
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product1', 'Category1', 'SubCategory1', 'Brand1', 100, 120, 'Type1', 4, 'Description1');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product2', 'Category2', 'SubCategory2', 'Brand2', 150, 180, 'Type2', 3, 'Description2');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product3', 'Category3', 'SubCategory3', 'Brand3', 200, 240, 'Type3', 5, 'Description3');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product4', 'Category4', 'SubCategory4', 'Brand1', 120, 140, 'Type4', 4, 'Description4');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product5', 'Category5', 'SubCategory5', 'Brand5', 180, 200, 'Type5', 4, 'Description5');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product6', 'Category6', 'SubCategory6', 'Brand6', 220, 260, 'Type6', 3, 'Description6');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product7', 'Category7', 'SubCategory7', 'Brand7', 250, 300, 'Type7', 5, 'Description7');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product8', 'Category8', 'SubCategory8', 'Brand8', 300, 360, 'Type8', 4, 'Description8');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product9', 'Category9', 'SubCategory9', 'Brand9', 280, 320, 'Type9', 4, 'Description9');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product10', 'Category10', 'SubCategory10', 'Brand10', 350, 400, 'Type10', 3, 'Description10');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product11', 'Category11', 'SubCategory11', 'Brand11', 400, 480, 'Type11', 5, 'Description11');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product12', 'Category12', 'SubCategory12', 'Brand12', 420, 500, 'Type12', 4, 'Description12');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product13', 'Category13', 'SubCategory13', 'Brand13', 480, 560, 'Type13', 4, 'Description13');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product14', 'Category14', 'SubCategory14', 'Brand14', 520, 600, 'Type14', 3, 'Description14');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product15', 'Category15', 'SubCategory15', 'Brand15', 600, 720, 'Type15', 5, 'Description15');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product16', 'Category16', 'SubCategory16', 'Brand3', 650, 780, 'Type16', 4, 'Description16');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product17', 'Category17', 'SubCategory17', 'Brand17', 720, 860, 'Type17', 4, 'Description17');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product18', 'Category18', 'SubCategory18', 'Brand18', 680, 800, 'Type18', 3, 'Description18');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product19', 'Category19', 'SubCategory19', 'Brand19', 800, 960, 'Type19', 5, 'Description19');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product20', 'Category20', 'SubCategory20', 'Brand20', 900, 1080, 'Type20', 4, 'Description20');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product21', 'Category21', 'SubCategory21', 'Brand21', 950, 1140, 'Type21', 4, 'Description21');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product22', 'Category22', 'SubCategory22', 'Brand22', 1100, 1320, 'Type22', 3, 'Description22');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product23', 'Category23', 'SubCategory23', 'Brand23', 1200, 1440, 'Type23', 5, 'Description23');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product24', 'Category24', 'SubCategory24', 'Brand24', 1300, 1560, 'Type24', 4, 'Description24');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product25', 'Category25', 'SubCategory25', 'Brand25', 1400, 1680, 'Type25', 4, 'Description25');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product26', 'Category26', 'SubCategory26', 'Brand26', 1500, 1800, 'Type26', 3, 'Description26');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product27', 'Category27', 'SubCategory27', 'Brand27', 1600, 1920, 'Type27', 5, 'Description27');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product28', 'Category28', 'SubCategory28', 'Brand28', 1650, 1980, 'Type28', 4, 'Description28');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product29', 'Category29', 'SubCategory29', 'Brand29', 1700, 2040, 'Type29', 4, 'Description29');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product30', 'Category30', 'SubCategory30', 'Brand50', 1800, 2160, 'Type30', 3, 'Description30');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product31', 'Category31', 'SubCategory31', 'Brand51', 1850, 2220, 'Type31', 5, 'Description31');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product32', 'Category32', 'SubCategory32', 'Brand52', 1900, 2280, 'Type32', 4, 'Description32');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product33', 'Category33', 'SubCategory33', 'Brand52', 2000, 2400, 'Type33', 4, 'Description33');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product34', 'Category34', 'SubCategory34', 'Brand54', 2100, 2520, 'Type34', 3, 'Description34');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product35', 'Category35', 'SubCategory35', 'Brand65', 2200, 2640, 'Type35', 5, 'Description35');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product36', 'Category36', 'SubCategory36', 'Brand66', 2300, 2760, 'Type36', 4, 'Description36');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product37', 'Category37', 'SubCategory37', 'Brand67', 2400, 2880, 'Type37', 4, 'Description37');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product38', 'Category38', 'SubCategory38', 'Brand73', 2500, 3000, 'Type38', 3, 'Description38');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product39', 'Category39', 'SubCategory39', 'Brand69', 2600, 3120, 'Type39', 5, 'Description39');",
    "INSERT INTO products (product_name, category, sub_category, brand, sale_price, market_price, type, rating, product_description) VALUES ('Product40', 'Category40', 'SubCategory40', 'Brand67', 2700, 3240, 'Type40', 4, 'Description40');"
]


    order_queries = [
    "INSERT INTO orders (order_id, date, total_price) VALUES (1, '2024-04-01', 500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (2, '2024-04-02', 700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (3, '2024-04-03', 900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (4, '2024-04-04', 1100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (5, '2024-04-05', 1300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (6, '2024-04-06', 1500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (7, '2024-04-07', 1700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (8, '2024-04-08', 1900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (9, '2024-04-09', 2100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (10, '2024-04-10', 2300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (11, '2024-04-11', 2500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (12, '2024-04-12', 2700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (13, '2024-04-13', 2900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (14, '2024-04-14', 3100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (15, '2024-04-15', 3300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (16, '2024-04-16', 3500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (17, '2024-04-17', 3700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (18, '2024-04-18', 3900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (19, '2024-04-19', 4100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (20, '2024-04-20', 4300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (78, '2024-06-18', 15900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (79, '2024-06-19', 16100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (80, '2024-06-20', 16300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (81, '2024-06-21', 16500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (82, '2024-06-22', 16700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (83, '2024-06-23', 16900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (84, '2024-06-24', 17100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (85, '2024-06-25', 17300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (86, '2024-06-26', 17500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (87, '2024-06-27', 17700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (88, '2024-06-28', 17900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (89, '2024-06-29', 18100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (90, '2024-06-30', 18300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (91, '2024-07-01', 18500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (92, '2024-07-02', 18700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (93, '2024-07-03', 18900);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (94, '2024-07-04', 19100);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (95, '2024-07-05', 19300);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (96, '2024-07-06', 19500);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (97, '2024-07-07', 19700);",
    "INSERT INTO orders (order_id, date, total_price) VALUES (98, '2024-07-08', 19900);"
]
    order_detail_queries = [
    "INSERT INTO order_details (product, order_) VALUES ('Product1', 1);",
    "INSERT INTO order_details (product, order_) VALUES ('Product2', 1);",
    "INSERT INTO order_details (product, order_) VALUES ('Product3', 3);",
    "INSERT INTO order_details (product, order_) VALUES ('Product4', 4);",
    "INSERT INTO order_details (product, order_) VALUES ('Product5', 5);",
    "INSERT INTO order_details (product, order_) VALUES ('Product6', 5);",
    "INSERT INTO order_details (product, order_) VALUES ('Product7', 5);",
    "INSERT INTO order_details (product, order_) VALUES ('Product8', 8);",
    "INSERT INTO order_details (product, order_) VALUES ('Product9', 9);",
    "INSERT INTO order_details (product, order_) VALUES ('Product10', 10);",
    "INSERT INTO order_details (product, order_) VALUES ('Product11', 11);",
    "INSERT INTO order_details (product, order_) VALUES ('Product12', 12);",
    "INSERT INTO order_details (product, order_) VALUES ('Product13', 13);",
    "INSERT INTO order_details (product, order_) VALUES ('Product14', 14);",
    "INSERT INTO order_details (product, order_) VALUES ('Product15', 15);",
    "INSERT INTO order_details (product, order_) VALUES ('Product16', 16);",
    "INSERT INTO order_details (product, order_) VALUES ('Product17', 17);",
    "INSERT INTO order_details (product, order_) VALUES ('Product18', 18);",
    "INSERT INTO order_details (product, order_) VALUES ('Product19', 19);",
    "INSERT INTO order_details (product, order_) VALUES ('Product20', 20);",
    "INSERT INTO order_details (product, order_) VALUES ('Product21', 21);",
    "INSERT INTO order_details (product, order_) VALUES ('Product22', 22);",
    "INSERT INTO order_details (product, order_) VALUES ('Product23', 23);",
    "INSERT INTO order_details (product, order_) VALUES ('Product24', 24);",
    "INSERT INTO order_details (product, order_) VALUES ('Product25', 25);",
    "INSERT INTO order_details (product, order_) VALUES ('Product26', 26);",
    "INSERT INTO order_details (product, order_) VALUES ('Product27', 27);",
    "INSERT INTO order_details (product, order_) VALUES ('Product28', 28);",
    "INSERT INTO order_details (product, order_) VALUES ('Product29', 29);",
    "INSERT INTO order_details (product, order_) VALUES ('Product29', 30);",
    "INSERT INTO order_details (product, order_) VALUES ('Product11', 31);",
    "INSERT INTO order_details (product, order_) VALUES ('Product12', 32);",
    "INSERT INTO order_details (product, order_) VALUES ('Product13', 33);",
    "INSERT INTO order_details (product, order_) VALUES ('Product14', 34);",
    "INSERT INTO order_details (product, order_) VALUES ('Product15', 35);",
    "INSERT INTO order_details (product, order_) VALUES ('Product16', 36);",
    "INSERT INTO order_details (product, order_) VALUES ('Product17', 37);",
    "INSERT INTO order_details (product, order_) VALUES ('Product18', 38);",
    "INSERT INTO order_details (product, order_) VALUES ('Product19', 39);",
    "INSERT INTO order_details (product, order_) VALUES ('Product20', 40);",
    "INSERT INTO order_details (product, order_) VALUES ('Product1', 41);",
    "INSERT INTO order_details (product, order_) VALUES ('Product2', 42);",
    "INSERT INTO order_details (product, order_) VALUES ('Product3', 43);",
    "INSERT INTO order_details (product, order_) VALUES ('Product4', 44);",
    "INSERT INTO order_details (product, order_) VALUES ('Product5', 45);",
    "INSERT INTO order_details (product, order_) VALUES ('Product6', 46);",
    "INSERT INTO order_details (product, order_) VALUES ('Product7', 47);",
    "INSERT INTO order_details (product, order_) VALUES ('Product8', 48);",
    "INSERT INTO order_details (product, order_) VALUES ('Product9', 49);",
    "INSERT INTO order_details (product, order_) VALUES ('Product10', 50);",
    "INSERT INTO order_details (product, order_) VALUES ('Product11', 51);",
    "INSERT INTO order_details (product, order_) VALUES ('Product12', 52);",
    "INSERT INTO order_details (product, order_) VALUES ('Product13', 53);",
    "INSERT INTO order_details (product, order_) VALUES ('Product14', 54);",
    "INSERT INTO order_details (product, order_) VALUES ('Product15', 55);",
    "INSERT INTO order_details (product, order_) VALUES ('Product16', 56);",
    "INSERT INTO order_details (product, order_) VALUES ('Product17', 57);",
    "INSERT INTO order_details (product, order_) VALUES ('Product18', 58);",
    "INSERT INTO order_details (product, order_) VALUES ('Product19', 59);",
    "INSERT INTO order_details (product, order_) VALUES ('Product20', 60);",
    "INSERT INTO order_details (product, order_) VALUES ('Product1', 61);",
    "INSERT INTO order_details (product, order_) VALUES ('Product2', 62);",
    "INSERT INTO order_details (product, order_) VALUES ('Product3', 63);",
    "INSERT INTO order_details (product, order_) VALUES ('Product4', 64);",
    "INSERT INTO order_details (product, order_) VALUES ('Product5', 65);",
    "INSERT INTO order_details (product, order_) VALUES ('Product6', 66);",
    "INSERT INTO order_details (product, order_) VALUES ('Product7', 67);",
    "INSERT INTO order_details (product, order_) VALUES ('Product8', 68);",
    "INSERT INTO order_details (product, order_) VALUES ('Product9', 69);",
    "INSERT INTO order_details (product, order_) VALUES ('Product10', 70);",
    "INSERT INTO order_details (product, order_) VALUES ('Product1', 71);",
    "INSERT INTO order_details (product, order_) VALUES ('Product2', 72);",
    "INSERT INTO order_details (product, order_) VALUES ('Product3', 73);",
    "INSERT INTO order_details (product, order_) VALUES ('Product4', 74);",
    "INSERT INTO order_details (product, order_) VALUES ('Product5', 75);",
    "INSERT INTO order_details (product, order_) VALUES ('Product6', 76);",
    "INSERT INTO order_details (product, order_) VALUES ('Product7', 77);",
    "INSERT INTO order_details (product, order_) VALUES ('Product8', 78);",
    "INSERT INTO order_details (product, order_) VALUES ('Product9', 79);",
    "INSERT INTO order_details (product, order_) VALUES ('Product31', 91);",
    "INSERT INTO order_details (product, order_) VALUES ('Product31', 92);",
    "INSERT INTO order_details (product, order_) VALUES ('Product32', 93);",
    "INSERT INTO order_details (product, order_) VALUES ('Product34', 94);",
    "INSERT INTO order_details (product, order_) VALUES ('Product35', 94);",
    "INSERT INTO order_details (product, order_) VALUES ('Product36', 96);",
    "INSERT INTO order_details (product, order_) VALUES ('Product35', 97);",
    "INSERT INTO order_details (product, order_) VALUES ('Product38', 94);"
]


    for query in supplier_queries:
        flag=opr.insert(query)

    for query in product_queries:
        flag=opr.insert(query)

    for query in order_queries:
        flag=opr.insert(query)

    for query in order_detail_queries:
        flag=opr.insert(query)