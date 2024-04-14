import streamlit as st
from backend.user_web_app_operations import UserOperations
from backend.dbm_ui_operations import DBMOperations
from streamlit_extras.stateful_button import button
import numpy as np


opr = UserOperations()

def main():
    st.title("End-User Web Application")
    st.image('frontend/ERD.png')
    
    # Prompt user for action choice
    action_choice = st.radio("Select an action to perform:", ["Insert", "Update", "Delete", "Search"], index=None)
    
    # Display appropriate tables based on user choice
    if action_choice == "Insert":
        insert_action()
    elif action_choice == "Update":
        update_action()
    elif action_choice == "Delete":
        delete_action()
    elif action_choice == "Search":
        search_action()


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
        return "product, order_"
    else:
        return None


def get_table_name(table_name):
    # Function to retrieve primary key information for the given table
    # You need to implement this function based on how you store and retrieve primary key information
    # Example: return "ID" if the primary key is "ID" for the specified table
    # You may fetch this information from a separate metadata table or directly from the database schema
    # Replace the example logic with your actual implementation
    if table_name == "Suppliers":
        return "suppliers"
    elif table_name == "Products":
        return "products"
    elif table_name == "Orders":
        return "orders"
    elif table_name == "Order Details":
        return "order_details"
    else:
        return None
    

def insert_action():
    st.header("Insert Actions")
        
    st.write("Choose one table to insert from:")
    buttons = ["Suppliers", "Products", "Orders", "Order Details"]

    table_choice = None

    for i, button_label in enumerate(buttons):
        if button(button_label, key=f"button{i+1}"):  # Use unique keys for each button
            table_choice = button_label

    table_name = get_table_name(table_choice)

    if table_choice:
        st.write(f"You selected {table_choice}.")
        
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
    
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
            
        st.subheader(f"Insert {table_choice}")

        if table_choice == "Products":
            st.markdown("<p style='color:red'><strong>Make sure that the brand name corresponds to the correct brand name in the suppliers table.</strong></p>", unsafe_allow_html=True)
        if table_choice == "Order Details":
            st.markdown("<p style='color:red'><strong>Make sure that the order id corresponds to the correct order id in the orders table.</strong></p>", unsafe_allow_html=True)
            st.markdown("<p style='color:red'><strong>Make sure that the product name corresponds to the correct product name in the products table.</strong></p>", unsafe_allow_html=True)
            
        st.write(f"Enter the following text boxes to insert:")

        # Assuming you have a function to get column names for the selected table
        column_names = np.unique(get_column_names(table_choice))
        # Create text input boxes for each column
        inputs = {}
        for column_name in column_names:
            inputs[column_name] = st.text_input(f"Enter {column_name}:")
            
        if button("Insert", key="insert_confirm"):
            # Confirmation prompt
            st.write("Are you sure you want to insert this data?")
            if button("Yes", key="insert_confirm_yes"):
                # Get values from text inputs  
                attributes = [inputs[column_name] for column_name in column_names]
                # print('attributessSSSSSSSSS', attributes)
                # print('column_namesSSSSSSSSS', column_names)

                # Call insert_data function with table name and attributes
                column_names_str = ", ".join(column_names)
                # Assuming attributes is a list of values corresponding to the column_names
                attributes_str = ", ".join([f"'{str(attribute)}'" for attribute in attributes])
                query = f"INSERT INTO {table_name} ({column_names_str}) VALUES ({attributes_str})"
                print('QUERY OUTPUT TESTING:', query)
                print('ATTRIBUTES OUTPUT TESTING:', attributes)

                flag = opr.opr.insert(query, attributes)
                
                if flag:
                    st.success("Data inserted successfully!")
                else:
                    st.error(f"Error inserting data")
            if button("No", key="insert_no"):
                st.write("Insertion cancelled")


def get_column_names(table_name):
    """
    Retrieve column names of the specified table.
    """
    table_name = get_table_name(table_name)

    # Query to retrieve column names from information_schema.columns table
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"

    # Execute the query to fetch column names
    flag, result = opr.opr.select(query)

    # Check if the query was successful
    if flag == 1:
        # Extract column names from the result
        column_names = [row[0] for row in result]
        return column_names
    else:
        # Display error message if query failed
        st.error("Error occurred while fetching column names.")
        return []


def update_action():
    deletion_status = None
    st.header("Update Actions")
        
    st.write("Choose one table to update from:")
    buttons = ["Suppliers", "Products", "Orders", "Order Details"]

    table_choice = None

    for i, button_label in enumerate(buttons):
        if button(button_label, key=f"button_{button_label}"):  # Use a unique key for each button
            table_choice = button_label

    if table_choice:
        st.write(f"You selected {table_choice}.")
        st.subheader(f"Update {table_choice}")
        primary_key_info = get_primary_key_info(table_choice)
            
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
    
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
        
        primary_key_info = get_primary_key_info(table_choice)
        if primary_key_info:
            if table_choice == "Order Details":
                st.write(f"Composite Key: product, order_")
                st.write("e.g. Product72,5")
                pk_value = st.text_input(f"Enter the product and order_ you would like to modify. Follow the provided example above:")
            else:
                st.write(f"Primary Key: {primary_key_info}")
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to modify:")

        if pk_value:
            # Assuming you have a function to handle the search operation
            found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
            if found_rows:
                st.write(f"{pk_value} was found")
                table_name = get_table_name(table_choice)
                column_names = np.unique(get_column_names(table_choice))
                inputs = {}
                for column_name in column_names:
                    inputs[column_name] = st.text_input(f"Enter {column_name}:")
                if button("Update", key="update_confirm"):
                    attributes = [inputs[column_name] for column_name in column_names]
                    print("TABLE NAME:", table_name)
                    print("ATTRIBUTES:", attributes)
                    print("COLUMNS:", column_names)
                    print("PRIMARY KEY INFO:", primary_key_info)
                    print("PK VALUE:", pk_value)
                    key = [primary_key_info]
                    search = [pk_value]
                    flag = opr.modify(table_name, column_names, attributes, key, search)
                    if flag == 1:
                        update_action()
                    else:
                        st.write("Update failed")
            else:
                st.write("Row cannot be found")
        # if pk_value:
        #     # Assuming you have a function to handle the search operation
        #     found_rows = handle_search_update(table_choice.lower(), primary_key_info, pk_value)
        #     if found_rows:
        #         st.write(f"")
        #     else:
        #         st.write("Not found.")
        # else:
        #     st.error("Error occurred while fetching data from the database.")  # Display error message if query failed
                
                
# def handle_search_update(table_name, primary_key, pk_value):
    # Function to handle the search operation based on the primary key value
    # This function will search for rows in the database based on the primary key value
    # Replace the example logic with your actual implementation
    
    # if isinstance(pk_value, str):
    #     if ',' in pk_value:
    #         # Split the string by comma and enclose each value in single quotes
    #         split_pkv = [f"'{val.strip()}'" for val in pk_value.split(',')]
    #     else:
    #         pk_value = "'" + pk_value + "'"  # Enclose single value in single quotes

    # if table_name == 'order details':
    #     table_name = 'order_details'
    #     query = f"SELECT * FROM order_details WHERE product = {split_pkv[0]} AND order_ = {split_pkv[1]}"
    # else:
    #     query = f"SELECT * FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    # flag, result = opr.opr.select(query)
    
    # if flag == 1:
    #     if result:
    #         # Display the result as a table using st.table()
    #         st.table(result)
    #         return 1
    # else:
    #     st.error("Error occurred while fetching data from the database.")
    #     return 0
    
    
    # # Assuming you have a DBMOperations object instantiated as opr
    # if isinstance(pk_value, str):
    #     pk_value = "'" + pk_value + "'"  # Enclose string values in single quotes
    
    # query = f"SELECT * FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    # flag, result = opr.opr.select(query)
    
    # if flag == 1:
    #     if result:
    #         # Display the table with one row
    #         st.table(result)
            
    #         # Generate text input boxes for each column
    #         column_names = ['brand_name', 'address', 'description', 'founding_year', 'num_of_products']
    #         updated_values = []
    #         for index, value in enumerate(result[0]):
    #             updated_value = st.text_input(f"Update {column_names[index]}:", value=value)
    #             updated_values.append(updated_value)
            
    #         # Save button to update the row in the database
    #         if st.button("Save"):
    #             # Logic to update the value in the database
    #             updated_row = dict(zip(column_names, updated_values))
    #             # Assuming you have a function to update the row
    #             update_status = update_row_in_database(table_name, primary_key, pk_value, updated_row)
    #             if update_status:
    #                 st.success("Row updated successfully.")
    #             else:
    #                 st.error("Failed to update row.")
            
    #         return result  # Return the found row(s)
    # else:
    #     st.error("Error occurred while fetching data from the database.")
    #     return None


def handle_search(table_name, primary_key, pk_value):
    # Function to handle the search operation based on the primary key value
    # This function will search for rows in the database based on the primary key value
    # Replace the example logic with your actual implementation
    
    if isinstance(pk_value, str):
        if ',' in pk_value:
            # Split the string by comma and enclose each value in single quotes
            split_pkv = [f"'{val.strip()}'" for val in pk_value.split(',')]
        else:
            pk_value = "'" + pk_value + "'"  # Enclose single value in single quotes

    if table_name == 'order details':
        table_name = 'order_details'
        query = f"SELECT * FROM order_details WHERE product = {split_pkv[0]} AND order_ = {split_pkv[1]}"
    else:
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
    

def delete_action():
    deletion_status = None
    st.header("Delete Actions")
        
    st.write("Choose one table to delete from:")
    buttons = ["Suppliers", "Products", "Orders", "Order Details"]

    table_choice = None

    for i, button_label in enumerate(buttons):
        if button(button_label, key=f"button{i+1}"):  # Use unique keys for each button
            table_choice = button_label

    if table_choice:
        st.write(f"You selected {table_choice}.")
        st.subheader(f"Delete {table_choice}")
        primary_key_info = get_primary_key_info(table_choice)
            
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
    
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
        
        primary_key_info = get_primary_key_info(table_choice)
        if primary_key_info:
            if table_choice == "Order Details":
                st.write(f"Composite Key: product, order_")
                st.write("e.g. Product72,5")
                pk_value = st.text_input(f"Enter the product and order_ you would like to remove. Follow the provided example above:")
            else:
                st.write(f"Primary Key: {primary_key_info}")
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to remove:")
            
        if pk_value:
            # Assuming you have a function to handle the search operation
            found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
            if found_rows:
                st.write(f"{pk_value} was found")
                st.write("Are you sure you want to remove this record?")
                y = button("Yes, remove", key=f'yes00_{table_choice}_{pk_value}')  # Unique key for each button
                n = button("No, cancel", key=f'no00_{table_choice}_{pk_value}')  # Unique key for each button
                if y:
                    deletion_status, msg = handle_delete(table_choice.lower(), primary_key_info, pk_value)
                    if deletion_status:
                        st.write(f"{pk_value} {msg}")
                        # Prompt user to remove another record
                        st.write("Would you like to remove another?")
                        if button("Yes", key=f'yes1_{table_choice}'):  # Unique key for each button
                            delete_action()  # Restart delete action
                        if button("No", key=f'no1_{table_choice}'):  # Unique key for each button
                            st.write("Deletion process ended.")
                elif n:
                    st.write(f"{pk_value} deletion cancelled.")
                else:
                    st.write("")
            else:
                st.write("Row cannot be found")


def handle_delete(table_name, primary_key, pk_value):
    # Function to handle the deletion of a record from the database
    # Replace the example logic with your actual implementation

    if isinstance(pk_value, str):
        if ',' in pk_value:
            # Split the string by comma and enclose each value in single quotes
            split_pkv = [f"'{val.strip()}'" for val in pk_value.split(',')]
        else:
            pk_value = "'" + pk_value + "'"  # Enclose single value in single quotes

    if table_name == 'order details':
        table_name = 'order_details'
        query = f"DELETE FROM order_details WHERE product = {split_pkv[0]} AND order_ = {split_pkv[1]}"
    else:
        query = f"DELETE FROM {table_name} WHERE {primary_key} = {pk_value}"
    
    flag = opr.opr.delete(query)  # Assuming opr.delete returns an integer status
    
    if flag == 1:
        return True, "Deletion successful"
    else:
        return False, "Deletion failed"


def search_action():
    st.header("Search Actions")
        
    st.write("Choose one table to search from:")
    buttons = ["Suppliers", "Products", "Orders", "Order Details"]

    table_choice = None

    for i, button_label in enumerate(buttons):
        if button(button_label, key=f"button{i+1}"):  # Use unique keys for each button
            table_choice = button_label

    if table_choice:
        st.write(f"You selected {table_choice}.")
        st.subheader(f"Search {table_choice}")
        primary_key_info = get_primary_key_info(table_choice)
        if table_choice == "Order Details":
            status, table_data = opr.opr.select(f"SELECT * FROM order_details")
        else:
            status, table_data = opr.opr.select(f"SELECT * FROM {table_choice.lower()}")
    
        if status == 1:  # Check if the query was successful
            st.table(table_data[:5])  # Display only the first 5 rows of data
        
        primary_key_info = get_primary_key_info(table_choice)
        if primary_key_info:
            if table_choice == "Order Details":
                st.write(f"Composite Key: product, order_")
                st.write("e.g. Product72,5")
                pk_value = st.text_input(f"Enter the product and order_ you would like to search. Follow the provided example above:")
            else:
                st.write(f"Primary Key: {primary_key_info}")
                pk_value = st.text_input(f"Enter the {primary_key_info} you would like to search:")
            
        if pk_value:
            # Assuming you have a function to handle the search operation
            found_rows = handle_search(table_choice.lower(), primary_key_info, pk_value)
            if found_rows:
                st.write(f"{pk_value} was found")
            else:
                st.write("Row cannot be found")


if __name__ == "__main__":
    main()