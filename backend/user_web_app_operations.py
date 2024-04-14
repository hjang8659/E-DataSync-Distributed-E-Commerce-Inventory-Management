from backend.hashing import hash_supplier
from backend.dbm_ui_operations import DBMOperations

#TODO: make general insert function which can insert into any of the 4 tables correctly
# - make 2nd hash function even/odd

class UserOperations:
    """
    Class to perform User operations.
    """

    def __init__(self):
        """
        Initialize the class with database engines.
        """
        self.opr = DBMOperations()

   
    def insert(self, table_name, attributes):
        """
        function to insert table_name with attributes.
        """
        # Insert from opr is only for supplier name, would need to change it to work with any table
        str_attributes = ", ".join(attributes)

        flag, res = self.opr.insert(f'INSERT INTO {table_name} VALUES {str_attributes}')
        print(flag, res)
        return flag, res
    
    def modify(self, table_name, columns, vals, key, search):
        """
        function to modify table_name with set attributes, operators, and values. Lastly, use the conditions. 
        """
        # UPDATE table_name
        # SET column1 = value1, column2 = value2, ...
        # WHERE condition;

        if len(key) != len(search):
            print("Error: Length of key and search do not match.")
        results = []
        for i in range(len(key)):
            results.append(key[i] + " = " + search[i])

        if len(columns) != len(vals):
            print("Error: Length of columns and vals do not match.")
        set_part = []
        for i in range(len(columns)):
            set_part.append(columns[i] + " = " + vals[i])

        str_conditions = ", ".join(results)
        str_set_part = ", ".join(set_part)
        flag, res = self.opr.update(f'UPDATE {table_name} SET {str_set_part} WHERE {str_conditions}')
        print(flag, res)
        return flag, res
    

    def search(self, table_name, attributes):
        """
        function to search table_name with set attributes. 
        """

        str_attributes = ", ".join(attributes)
        flag, res = self.opr.select(f'SELECT {str_attributes} FROM {table_name}')
        print(flag, res)
        return flag, res
    
    def delete(self, table_name, conditions):
        """
        function to delete 1 row from table_name with conditions. 
        """
        # Delete based on specific primary key, finish
        str_conditions = ", ".join(conditions)
        flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
        print(flag, res)
        return flag, res
    
    def deleteOne(self, table_name, conditions):
        """
        function to delete 1 row from table_name with conditions. 
        """
        # Delete based on specific primary key, finish
        str_conditions = ", ".join(conditions)
        flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
        print(flag, res)
        return flag, res
    
    def deleteMany(self, table_name, conditions):
        """
        function to delete many rows from table_name with conditions. 
        """
        
        str_conditions = ", ".join(conditions)
        flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
        print(flag, res)
        return flag, res