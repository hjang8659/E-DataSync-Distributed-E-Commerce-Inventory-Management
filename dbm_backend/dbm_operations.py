from sqlalchemy import create_engine
from hashing import hash_prod

class dbm_operations(): # before calling the methods of this class: 1. Get table name 2. Get CLI input 3. Validate query 4. Call relevant functions based on contains method
    def __init__(self):
        self.connection_string = 'mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/'

    def validate_query(self, text):
        pass

    def insert(self, table, text): # insert record in hashed db

        pass

    def modify(self, table, text): # modify records in both dbs, return successful message if successful else return unsuccessful message explaining reason
        pass

    def delete(self, table, text): # perform on both dbs, return successful message if successful else return unsuccessful message explaining reason
        pass

    def select(self, table, text): # perform on both dbs, return combine results if successful else return unsuccessful message explaining reason
        pass
    
    





