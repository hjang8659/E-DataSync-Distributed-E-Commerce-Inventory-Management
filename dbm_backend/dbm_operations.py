from sqlalchemy import create_engine
import sqlparse
from hashing import hash_prod

class dbm_operations(): # before calling the methods of this class: 1. Get table name 2. Get CLI input 3. Call relevant functions based on contains method
    def __init__(self):
        self.hash = hash_prod()
        self.engine_db1 = create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase')
        self.engine_db2 =  create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase2')
        self.engine_index = {0: self.engine_db1, 1: self.engine_db2}

    def insert(self, query): # insert record in hashed db after hashing on product name
        product_name = query.split('values')[1].split(')')[0].split('(')[1].split(',')[0]
        db_index = self.hash.db[self.hash.generate_hash(product_name)]
    
        with self.engine_index[db_index].connect() as con:
            try:
                res = con.execute(query)
                return 1
            
            except:
                return 0
            
    def select(self, query): # perform on both dbs, return combine results if successful else return unsuccessful message explaining reason
        try: 
            with self.engine_db1.connect() as con:
                    res1 = con.execute(query)
            with self.engine_db2.connect() as con:
                    res2 = con.execute(query)   

            res = res1 + res2
            return 1, res
         
        except:
            return 0
                

    def update(self, query): # modify records in both dbs, return successful message if successful else return unsuccessful message explaining reason
        try: 
            with self.engine_db1.connect() as con:
                    res = con.execute(query)
            with self.engine_db2.connect() as con:
                    res = con.execute(query)   

            return 1
         
        except:
            return 0
                

    def delete(self, query): # perform on both dbs, return successful message if successful else return unsuccessful message explaining reason
        try: 
            with self.engine_db1.connect() as con:
                    res = con.execute(query)
            with self.engine_db2.connect() as con:
                    res = con.execute(query)   
                    
            return 1
         
        except:
            return 0

 
    
    





