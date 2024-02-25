import streamlit as st

def main():
    st.title("Database 🗄️")

    # Prompt user for database choice
    database_choice = st.radio("Select a database to access:", ["Products", "Suppliers"])

    # Display appropriate actions based on user choice
    if database_choice == "Products":
        perform_product_action()
    elif database_choice == "Suppliers":
        perform_supplier_action()

def perform_product_action():
    st.header("Product Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an action:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_product()
    elif action_choice == "Modify":
        modify_product()
    elif action_choice == "Search":
        search_product()
    elif action_choice == "Delete":
        delete_product()

def perform_supplier_action():
    st.header("Supplier Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an action:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_supplier()
    elif action_choice == "Modify":
        modify_supplier()
    elif action_choice == "Search":
        search_supplier()
    elif action_choice == "Delete":
        delete_supplier()

def insert_product():
    st.subheader("Insert Product")
    # Add logic to insert product into the database

def modify_product():
    st.subheader("Modify Product")
    # Add logic to modify product in the database

def search_product():
    st.subheader("Search Product")
    # Add logic to search for product in the database

def delete_product():
    st.subheader("Delete Product")
    # Add logic to delete product from the database

def insert_supplier():
    st.subheader("Insert Supplier")
    # Add logic to insert supplier into the database

def modify_supplier():
    st.subheader("Modify Supplier")
    # Add logic to modify supplier in the database

def search_supplier():
    st.subheader("Search Supplier")
    # Add logic to search for supplier in the database

def delete_supplier():
    st.subheader("Delete Supplier")
    # Add logic to delete supplier from the database

if __name__ == "__main__":
    main()
