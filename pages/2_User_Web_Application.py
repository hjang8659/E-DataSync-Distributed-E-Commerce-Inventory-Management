import streamlit as st
from backend.user_web_app_operations import UserOperations

def main():
    st.title("End-User Web Application")
    # Prompt user for database choice
    database_choice = st.radio("Select a table to access:", ["Suppliers, Products, Orders, Order Details"])

    # Display appropriate actions based on user choice
    if database_choice == "Suppliers":
        perform_supplier_action()
    elif database_choice == "Products":
        perform_product_action()
    elif database_choice == "Orders":
        perform_order_action()
    elif database_choice == "Order Details":
        perform_order_detail_action()

def perform_supplier_action():
    st.header("Supplier Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an operation to perform:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_supplier()
    elif action_choice == "Modify":
        modify_supplier()
    elif action_choice == "Search":
        search_supplier()
    elif action_choice == "Delete":
        delete_supplier()

def perform_product_action():
    st.header("Product Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an operation to perform:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_product()
    elif action_choice == "Modify":
        modify_product()
    elif action_choice == "Search":
        search_product()
    elif action_choice == "Delete":
        delete_product()

def perform_order_action():
    st.header("Order Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an operation to perform:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_order()
    elif action_choice == "Modify":
        modify_order()
    elif action_choice == "Search":
        search_order()
    elif action_choice == "Delete":
        delete_order()

def perform_order_detail_action():
    st.header("Order Detail Actions")

    # Prompt user for action choice
    action_choice = st.radio("Select an operation to perform:", ["Insert", "Modify", "Search", "Delete"])

    if action_choice == "Insert":
        insert_order_detail()
    elif action_choice == "Modify":
        modify_order_detail()
    elif action_choice == "Search":
        search_order_detail()
    elif action_choice == "Delete":
        delete_order_detail()

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

def insert_order():
    st.subheader("Insert Order")
    # Add logic to insert order into the database

def modify_order():
    st.subheader("Modify Order")
    # Add logic to modify order in the database

def search_order():
    st.subheader("Search Order")
    # Add logic to search for order in the database

def delete_order():
    st.subheader("Delete Order")
    # Add logic to delete order from the database

def insert_order_detail():
    st.subheader("Insert Order Detail")
    # Add logic to insert order detail into the database

def modify_order_detail():
    st.subheader("Modify Order Detail")
    # Add logic to modify order detail in the database

def search_order_detail():
    st.subheader("Search Order Detail")
    # Add logic to search for order detail in the database

def delete_order_detail():
    st.subheader("Delete Order Detail")
    # Add logic to delete order detail from the database


if __name__ == "__main__":
    main()
