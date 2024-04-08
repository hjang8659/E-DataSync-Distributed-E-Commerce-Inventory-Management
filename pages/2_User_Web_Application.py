import streamlit as st
from backend.user_web_app_operations import UserOperations
from backend.dbm_ui_operations import DBMOperations

opr = DBMOperations()

def main():
    st.title("End-User Web Application")
    
    # Prompt user for action choice
    action_choice = st.radio("Select an action to perform:", ["", "Insert", "Update", "Delete", "Search"])
    
    # Display appropriate tables based on user choice
    if action_choice == "Insert":
        insert_action()
    elif action_choice == "Update":
        update_action()
    elif action_choice == "Delete":
        delete_action()
    elif action_choice == "Search":
        search_action()
    
def insert_action():
    st.header("Insert Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to insert into:", ["", "Suppliers", "Products", "Orders", "Order Details"], index=0)
    
    # Display appropriate actions based on table choice
    if table_choice == "Suppliers":
        insert_supplier()
    elif table_choice == "Products":
        insert_product()
    elif table_choice == "Orders":
        insert_order()
    elif table_choice == "Order Details":
        insert_order_detail()

def update_action():
    st.header("Update Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to update:", ["", "Suppliers", "Products", "Orders", "Order Details"], index=0)
    
    if table_choice != "":
        st.subheader(f"Update {table_choice}")
        # Assuming `opr.select` retrieves data from the database based on the table choice
        status, table_data = opr.select(f"SELECT * FROM {table_choice.lower()}")
        
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
            
            # Display primary key information
            primary_key_info = get_primary_key_info(table_choice)
            if primary_key_info:
                st.write(f"Primary Key: {primary_key_info}")
                
                # Prompt user to enter the primary key value
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to update:")
                
                # Button to trigger the search operation
                if st.button("Find"):
                    if pk_value:
                        # Assuming you have a function to handle the search operation
                        found_rows = handle_search_update(table_choice.lower(), primary_key_info, pk_value)
                        if found_rows:
                            st.write(f"")
                        else:
                            st.write("Not found.")
            else:
                st.warning("Primary key information not available for this table.")
        else:
            st.error("Error occurred while fetching data from the database.")  # Display error message if query failed

def handle_search_update(table_name, primary_key, pk_value):
    # Function to handle the search operation based on the primary key value
    # This function will search for rows in the database based on the primary key value
    # Replace the example logic with your actual implementation
    
    # Assuming you have a DBMOperations object instantiated as opr
    if isinstance(pk_value, str):
        pk_value = "'" + pk_value + "'"  # Enclose string values in single quotes
    
    query = f"SELECT * FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag, result = opr.select(query)
    
    if flag == 1:
        if result:
            # Display the table with one row
            st.table(result)
            
            # Generate text input boxes for each column
            column_names = ['brand_name', 'address', 'description', 'founding_year', 'num_of_products']
            updated_values = []
            for index, value in enumerate(result[0]):
                updated_value = st.text_input(f"Update {column_names[index]}:", value=value)
                updated_values.append(updated_value)
            
            # Save button to update the row in the database
            if st.button("Save"):
                # Logic to update the value in the database
                updated_row = dict(zip(column_names, updated_values))
                # Assuming you have a function to update the row
                update_status = update_row_in_database(table_name, primary_key, pk_value, updated_row)
                if update_status:
                    st.success("Row updated successfully.")
                else:
                    st.error("Failed to update row.")
            
            return result  # Return the found row(s)
    else:
        st.error("Error occurred while fetching data from the database.")
        return None


def handle_search(table_name, primary_key, pk_value):
    # Function to handle the search operation based on the primary key value
    # This function will search for rows in the database based on the primary key value
    # Replace the example logic with your actual implementation
    
    # Assuming you have a DBMOperations object instantiated as opr
    if isinstance(pk_value, str):
        pk_value = "'" + pk_value + "'"  # Enclose string values in single quotes
    
    query = f"SELECT * FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag, result = opr.select(query)
    
    if flag == 1:
        if result:
            # Display the result as a table using st.table()
            st.table(result)
            return 1
    else:
        st.error("Error occurred while fetching data from the database.")
        return 0


def get_primary_key_info(table_name):
    # Function to retrieve primary key information for the given table
    # You need to implement this function based on how you store and retrieve primary key information
    # Example: return "ID" if the primary key is "ID" for the specified table
    # You may fetch this information from a separate metadata table or directly from the database schema
    # Replace the example logic with your actual implementation
    if table_name == "Suppliers":
        return "brand_name"
    elif table_name == "Products":
        return "product_name"
    elif table_name == "Orders":
        return "order_id"
    elif table_name == "Order Details":
        return "OrderDetailID"
    else:
        return None

def delete_action():
    st.header("Delete Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to delete from:", ["", "Suppliers", "Products", "Orders", "Order Details"])
    
    if table_choice != "":
        st.subheader(f"Delete {table_choice}")
        # Assuming `opr.select` retrieves data from the database based on the table choice
        status, table_data = opr.select(f"SELECT * FROM {table_choice.lower()}")
        
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
            
            # Display primary key information
            primary_key_info = get_primary_key_info(table_choice)
            if primary_key_info:
                st.write(f"Primary Key: {primary_key_info}")
                
                # Prompt user to enter the primary key value
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to remove:")
                
                # Button to trigger the search operation
                if st.button("Find"):
                    if pk_value:
                        # Assuming you have a function to handle the search operation
                        found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
                        if found_rows:
                            st.write(f"{pk_value} was found")
                            # Prompt user to confirm deletion
                            confirmation = st.radio("Are you sure you want to remove this record?", ["", "Yes", "No"], index=0)
                            if confirmation == "Yes":
                                # Assuming you have a function to handle deletion
                                deletion_status = handle_delete(table_choice.lower(), primary_key_info, pk_value)
                                if deletion_status:
                                    st.write(f"{pk_value} was removed")
                                else:
                                    st.write("An error occurred while deleting the record.")
                            elif confirmation == "No":
                                st.write("Deletion cancelled.")
                                return  # Don't proceed further if deletion is cancelled
                            else:
                                st.write("")
                        else:
                            st.write("Not found.")
            else:
                st.warning("Primary key information not available for this table.")
        else:
            st.error("Error occurred while fetching data from the database.")


def handle_delete(table_name, primary_key, pk_value):
    # Function to handle the deletion of a record from the database
    # Replace the example logic with your actual implementation
    
    # Assuming you have a DBMOperations object instantiated as opr
    if isinstance(pk_value, str):
        pk_value = "'" + pk_value + "'"  # Enclose string values in single quotes
    
    query = f"DELETE FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag, result = opr.execute(query)
    
    if flag == 1:
        return True
    else:
        return False
            
def search_action():
    st.header("Search Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to search from:", ["", "Suppliers", "Products", "Orders", "Order Details"])
    
    if table_choice != "":
        st.subheader(f"Search {table_choice}")
        # Assuming `opr.select` retrieves data from the database based on the table choice
        status, table_data = opr.select(f"SELECT * FROM {table_choice.lower()}")
        
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
            
            # Display primary key information
            primary_key_info = get_primary_key_info(table_choice)
            if primary_key_info:
                st.write(f"Primary Key: {primary_key_info}")
                
                # Prompt user to enter the primary key value
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to remove:")
                
                # Button to trigger the search operation
                if st.button("Find"):
                    if pk_value:
                        # Assuming you have a function to handle the search operation
                        found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
                        if found_rows:
                            st.write(f"{pk_value} was found")

# Functions for handling actions on Suppliers
def insert_supplier():
    st.subheader("Insert Supplier")
    # Add logic to insert supplier into the database

def update_supplier():
    st.subheader("Update Supplier")
    # Add logic to update supplier in the database

def delete_supplier():
    st.subheader("Delete Supplier")
    # Add logic to delete supplier from the database

def search_supplier():
    st.subheader("Search Supplier")
    # Add logic to search for supplier in the database

# Functions for handling actions on Products
def insert_product():
    st.subheader("Insert Product")
    # Add logic to insert product into the database

def update_product():
    st.subheader("Update Product")
    # Add logic to update product in the database

def delete_product():
    st.subheader("Delete Product")
    # Add logic to delete product from the database

def search_product():
    st.subheader("Search Product")
    # Add logic to search for product in the database

# Functions for handling actions on Orders
def insert_order():
    st.subheader("Insert Order")
    # Add logic to insert order into the database

def update_order():
    st.subheader("Update Order")
    # Add logic to update order in the database

def delete_order():
    st.subheader("Delete Order")
    # Add logic to delete order from the database

def search_order():
    st.subheader("Search Order")
    # Add logic to search for order in the database

# Functions for handling actions on Order Details
def insert_order_detail():
    st.subheader("Insert Order Detail")
    # Add logic to insert order detail into the database

def update_order_detail():
    st.subheader("Update Order Detail")
    # Add logic to update order detail in the database

def delete_order_detail():
    st.subheader("Delete Order Detail")
    # Add logic to delete order detail from the database

def search_order_detail():
    st.subheader("Search Order Detail")
    # Add logic to search for order detail in the database

if __name__ == "__main__":
    main()
