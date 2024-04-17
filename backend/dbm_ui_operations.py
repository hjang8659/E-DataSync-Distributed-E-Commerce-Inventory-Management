from sqlalchemy import create_engine, text
from backend.hashing import hash_supplier
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
        return query.split('VALUES')[1].split(')')[0].split('(')[1].split(',')[0]
    
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
        values_match = re.search(r"VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
        columns_match = re.search(r"INSERT INTO\s+[^\s]+\s*\(([^)]+)\)", query, re.IGNORECASE)
        if not values_match or not columns_match:
            raise ValueError("Malformed INSERT query.")
        
        values_list = [val.strip() for val in values_match.group(1).split(',')]
        columns_list = [col.strip() for col in columns_match.group(1).split(',')]
        
        if len(columns_list) != len(values_list):
            raise ValueError("Mismatch between number of columns and number of values.")

        new_values = [self._format_value(value.strip("'\""), col, data_type_dict) for col, value in zip(columns_list, values_list)]
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
                    where_clause = re.sub(pattern, lambda m: f"{m.group(1)}'{m.group(2).strip('\'')}'", where_clause, flags=re.IGNORECASE)

        # Construct the updated query
        before_set = query[:set_match.start()]  # Everything before SET
        after_where = query[where_match.end():] if where_match else ''  # Anything after WHERE clause
        updated_query = f"{before_set}SET {new_set_str} WHERE {where_clause}{after_where}"
        return updated_query

    def _format_value(self, value, column, data_type_dict):
        # Helper to format value based on column's data type
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
            db_index = self.hash.generate_hash(supplier_name)

        elif table_name == "products":
            # Join products and suppliers as a view, then get supplier name from it and database index
            # products "brand" FK connects to "brand_name" PK in suppliers

            # getting "brand"
            match = re.search(r"VALUES\s*\(\s*'([^']*)'", query, re.IGNORECASE)

            if match:
                brand = match.group(1)
                db_index = self.hash.generate_hash(brand)

            else:
                print("Regex pattern couldn't find brand")
                return 0

        elif table_name == "order_details":
            # Join order_details to the products view to get the supplier name and database index
            # product name in the "product" attribute

            # Getting "product" from query
            match = re.search(r"VALUES\s*\(\s*\d+\s*,\s*'([^']*)'", query, re.IGNORECASE)

            if match:
                product = match.group(1)
                # Search by primary key for row, then obtain suppliers name
                query2 = f"SELECT brand FROM products WHERE product_name = '{product}'"
                flag, result = self.select(query2)
                db_index = self.hash.generate_hash(result[0][0])
                
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
    
    #flag= opr.insert("INSERT INTO orders (order_id, date, total_price) VALUES (99, '04-10-2025', 100)")
    flag, res = opr.select("SELECT * FROM orders")
    print(flag)
    print(res)