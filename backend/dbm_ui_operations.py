from sqlalchemy import create_engine, text
from backend.hashing import hash_supplier
# from hashing import hash_supplier
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
                    # print(e)
                    raise e
                    # return 0
                
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
                # print(e)
                raise e
                # return 0

    
    def insertMany(self, query):
        parts = query.split("VALUES")
        insert_into_part = parts[0].strip()
        values_part = parts[1].strip(" ;")

        # Split the values part into individual value groups
        # We need to be careful to only split on commas that are not enclosed in quotes
        # This is a simple parser that assumes values are not nested and do not contain parentheses
        individual_values = []
        current_value = ""
        parentheses_count = 0
        for char in values_part:
            if char == ',' and parentheses_count == 0:
                individual_values.append(current_value)
                current_value = ""
            else:
                if char == '(':
                    parentheses_count += 1
                elif char == ')':
                    parentheses_count -= 1
                current_value += char
        individual_values.append(current_value)  # Add the last value group

        # Remove any leading/trailing whitespace or commas
        individual_values = [val.strip(" ,") for val in individual_values]

        # Create individual insert statements
        individual_inserts = [f"{insert_into_part} VALUES {val};" for val in individual_values]

        for q in individual_inserts:
            print(q)
            self.insert(q)
        
        return 1


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
            return 1, results
        except Exception as e:
            # print(e)
            raise e
            # return 0

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
            # print(e)
            raise e
            # return 0

    def delete(self, query):
        """
        Delete records from both databases.
        """
        try:
            for engine in self.engines.values():
                self._execute_query(engine, query)
            return 1
        except Exception as e:
            # print(e)
            raise e
            # return 0

if __name__ == '__main__':
    opr = DBMOperations()
    # opr.insertMany("INSERT INTO suppliers (brand_name, address, brand_description, founding_year, num_of_products) VALUES ('Brand100', 'Address1', 'Description1', 2000, 50),('Brand200', 'Address2', 'Description2', 1995, 60);")