import streamlit as st
from backend.user_web_app_operations import UserOperations
from backend.dbm_ui_operations import DBMOperations
from streamlit_extras.stateful_button import button


opr = UserOperations()

def main():
    st.title("End-User Web Application")
    st.image('frontend/ERD.png')
    
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


def update_action():
    st.header("Update Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to update:", ["", "Suppliers", "Products", "Orders", "Order Details"], index=0)
    
    if table_choice != "":
        st.subheader(f"Update {table_choice}")
        # Assuming `opr.select` retrieves data from the database based on the table choice
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
        
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
    
    flag, result = opr.opr.select(query)
    
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

    if table_name == 'order details':
        table_name = 'order_details'
    query = f"SELECT * FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag, result = opr.opr.select(query)
    
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
        return "product"
    else:
        return None
    
    
def delete_action():
    deletion_status = None
    st.header("Delete Actions")
        
    st.write("Choose one table to delete from:")
    buttons = ["Suppliers", "Products", "Orders", "Order Details"]

    table_choice = None

    for i, button_label in enumerate(buttons):
        if button(button_label, key=f"button{i+1}"):
            table_choice = button_label

    if table_choice:
        st.write(f"You selected {table_choice}.")
        st.subheader(f"Delete {table_choice}")
        primary_key_info = get_primary_key_info(table_choice)
        if primary_key_info:
            st.write(f"Primary Key: {primary_key_info}")
            
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
    
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
        
        primary_key_info = get_primary_key_info(table_choice)
        if primary_key_info:
            st.write(f"Primary Key: {primary_key_info}")
            # Prompt user to enter the primary key value
            pk_value = st.text_input(f"Enter the {primary_key_info} you would like to remove:")
            
        if pk_value:
            # Assuming you have a function to handle the search operation
            found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
            if found_rows:
                st.write(f"{pk_value} was found")
                st.write("Are you sure you want to remove this record?")
                y = button("Yes, remove", key='yes00')
                n = button("No, cancel", key='no00')
                if y:
                    deletion_status = handle_delete(table_choice.lower(), primary_key_info, pk_value)
                    if deletion_status:
                        st.write(f"{pk_value} was successfully removed")
                        # Prompt user to remove another record
                        st.write("Would you like to remove another?")
                        if button("Yes", key='yes1'):
                            delete_action()  # Restart delete action
                        if button("No", key='no1'):
                            st.write("Deletion process ended.")
                elif n:
                    st.write("Deletion process ended.")
                else:
                    st.write("")
            else:
                st.write("Row cannot be found")


def handle_delete(table_name, primary_key, pk_value):
    # Function to handle the deletion of a record from the database
    # Replace the example logic with your actual implementation
    
    # Assuming you have a DBMOperations object instantiated as opr
    if isinstance(pk_value, str):
        pk_value = "'" + pk_value + "'"  # Enclose string values in single quotes
    
    query = f"DELETE FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag = opr.opr.delete(query)  # Assuming opr.delete returns an integer status
    
    if flag == 1:
        return True, "Deletion successful"
    else:
        return False, "Deletion failed"


def search_action():
    st.header("Search Actions")
    # Prompt user for table choice
    table_choice = st.radio("Select a table to search from:", ["", "Suppliers", "Products", "Orders", "Order Details"])
    
    if table_choice != "":
        st.subheader(f"Search {table_choice}")
        # Assuming `opr.select` retrieves data from the database based on the table choice
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
        
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
            
            # Display primary key information
            primary_key_info = get_primary_key_info(table_choice)
            if primary_key_info:
                st.write(f"Primary Key: {primary_key_info}")
                
                # Prompt user to enter the primary key value
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to search:")
                
                # Button to trigger the search operation
                if st.button("Find"):
                    if pk_value:
                        # Assuming you have a function to handle the search operation
                        found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
                        if found_rows:
                            st.write(f"{pk_value} was found")


if __name__ == "__main__":
    main()