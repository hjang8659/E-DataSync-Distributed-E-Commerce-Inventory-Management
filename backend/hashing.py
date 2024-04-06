class hash_supplier():
    def __init__(self):
        self.db = {
                0: 'mydatabase',
                1: 'mydatabase2'
            }

    def generate_hash(self, supplier_name):
        hash_value = 0

        for chr in supplier_name:
            hash_value += ord(chr) # generate the ordinal unicode equivalent of the characters in the supplier name and sum them 
        db_index = hash_value % 2 # generate a hash value for the supplier name before taking mod to retrieve a binary output for associating supplier names with relevant db
        
        return db_index
    
if __name__ == '__main__':
    hash = hash_supplier()
    index = hash.db[hash.generate_hash("test")]
    print("db: ", index)