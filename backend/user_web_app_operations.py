from backend.hashing import hash_supplier
from backend.dbm_ui_operations import DBMOperations

class UserOperations:
    """
    Class to perform User operations.
    """

    def __init__(self):
        """
        Initialize the class with database engines.
        """
        self.opr = DBMOperations()

   
    def insert(self, table_name, columns, values):
        """
        function to insert table_name with columns and values.
        """
        if len(columns) != len(values):
            print("Error: Length of columns and values do not match.")

        str_columns = ", ".join(columns)
        str_values = ", ".join(values)
        print(f'INSERT INTO {table_name} ({str_columns}) VALUES ({str_values})')

        flag = self.opr.insert(f'INSERT INTO {table_name} ({str_columns}) VALUES ({str_values})')
        print(flag)
        return flag
    
    def modify(self, table_name, columns, vals, key, search):
        """
        function to modify table_name with set attributes, operators, and values. Lastly, use the conditions. 
        """

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
        flag = self.opr.update(f'UPDATE {table_name} SET {str_set_part} WHERE {str_conditions}')
        print(flag)
        return flag
    

    def search(self, table_name, attributes):
        """
        function to search table_name with set attributes. 
        """

        str_attributes = ", ".join(attributes)
        flag, res = self.opr.select(f'SELECT {str_attributes} FROM {table_name}')
        print(flag, res)
        return flag, res
    
    # def searchMany(self, table_name, attributes, col, search_cond):
    #     """
    #     function to search table_name with set attributes. 
    #     """

    #     str_attributes = ", ".join(attributes)
    #     flag, res = self.opr.select(f'SELECT {str_attributes} FROM {table_name}')
    #     print(flag, res)
    #     return flag, res

    
    def delete(self, table_name, conditions):
        """
        function to delete 1 row from table_name with conditions. 
        """
        # Delete based on specific primary key, finish
        str_conditions = ", ".join(conditions)
        flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
        print(flag, res)
        return flag, res
    
    # def deleteOne(self, table_name, conditions):
    #     """
    #     function to delete 1 row from table_name with conditions. 
    #     """
    #     # Delete based on specific primary key, finish
    #     str_conditions = ", ".join(conditions)
    #     flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
    #     print(flag, res)
    #     return flag, res
    
    # def deleteMany(self, table_name, conditions):
    #     """
    #     function to delete many rows from table_name with conditions. 
    #     """
        
    #     str_conditions = ", ".join(conditions)
    #     flag, res = self.opr.select(f'DELETE FROM {table_name} WHERE {str_conditions}')
    #     print(flag, res)
    #     return flag, res