from sqlalchemy import create_engine, text
from dbm_backend.hashing import hash_prod

class DBMOperations:
    """
    Class to perform database operations.
    """

    def __init__(self):
        """
        Initialize the class with database engines.
        """
        self.hash = hash_prod()
        self.engines = {
            0: create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase'),
            1: create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase2')
        }

    def _get_product_name(self, query):
        """
        Helper function to extract product name from query.
        """
        return query.split('values')[1].split(')')[0].split('(')[1].split(',')[0]

    def insert(self, query):
        """
        Insert record into hashed database after hashing product name.
        """
        product_name = self._get_product_name(query)
        db_index = self.hash.generate_hash(product_name)
        
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
    
    flag, res= opr.select("select * from products limit 10")
    print(flag, res)
