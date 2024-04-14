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
        
        if table_name == "suppliers":
            # Looks like it can only insert 1 value at a time
            supplier_name = self._get_supplier_name(query)
            db_index = self.hash.generate_hash(supplier_name)

        elif table_name == "products":
            # Join products and suppliers as a view, then get supplier name from it and database index
            # products "brand" FK connects to "brand_name" PK in suppliers

            # getting "brand"
            match = re.search(r"VALUES\s*\(\s*'(?:[^']|'')*'\s*,\s*'(?:[^']|'')*'\s*,\s*'(?:[^']|'')*'\s*,\s*'((?:[^']|'')*)'", query, re.IGNORECASE)

            if match:
                brand = match.group(1)
                db_index = self.hash.generate_hash(brand)

            else:
                print("Brand could not be found.")
                return 0

        elif table_name == "order_details":
            # Join order_details to the products view to get the supplier name and database index
            # product name in the "product" attribute

            # Getting "product" from query
            match = re.search(r"VALUES\s*\(\s*'([^']*)'", query, re.IGNORECASE)

            if match:
                product = match.group(1)
                # Search by primary key for row, then obtain suppliers name
                query = f"SELECT brand FROM products WHERE product_name = {product}"
                flag, result = self.select(query)
                db_index = self.hash.generate_hash(result)
                
            else:
                print("Product could not be found.")
                return 0

        elif table_name == "orders":
            # ex query/ INSERT INTO orders (order_id, date, total_price) VALUES (1, '2024-04-10', 100);
            # Insert into database based on odd/even orders_id value
            # database 0 if even, database 1 if odd
            # Regular expression to find and capture the order_id
            match = re.search(r"VALUES\s*\(\s*(\d+)", query, re.IGNORECASE)

            if match:
                order_id = int(match.group(1))
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

            else:
                print("Order ID could not be found.")
                return 0

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
            return 1, results
        except Exception as e:
            print(e)
            return 0, None

    def update(self, query):
        """
        Modify records in both databases.
        """
        try:
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