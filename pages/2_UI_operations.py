import streamlit as st
import subprocess
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dbm_backend.dbm_operations import DBMOperations
import sqlparse

class DeveloperPage:
    def __init__(self):
        st.set_page_config(
            page_title="Developer Page",
            page_icon="🛠️",
        )

    def authenticate(self):
        password = st.text_input("Enter Password:", type="password")
        return password == "dsci551"

    def run_dev_page(self):
        st.write("### Developer Page 🛠️")

        authenticated = self.authenticate()
        if authenticated:
            st.success("Authentication successful!")
            st.write("This is the developer page where you can perform development tasks.")
            st.write("## Developer Command Line Interface")
            cli_command = st.text_area("Enter a command then click Run Command:")
            button_clicked = st.button("Run Command")
            if button_clicked and cli_command:
                opr = DBMOperations()
                sql_query = cli_command
                # Filter between lowercase(select, insert, update, delete)
                command_used = cli_command.split()[0].lower()
                if command_used == "select":
                    flag, res= opr.select(sql_query)
                elif command_used == "insert":
                    flag, res= opr.insert(sql_query)
                elif command_used == "update":
                    flag, res= opr.update(sql_query)
                elif command_used == "delete":
                    flag, res= opr.delete(sql_query)
                else:
                    print("Unknown command used:", command_used)

                if flag == 0:
                    print("Error: Syntax error or database error")
                else:
                    print("Operation Successful")
                print(flag, res)

        else:
            cli_command = 0
            
        return cli_command

    def display(df):
        st.write(df.head())
        
if __name__ == "__main__":
    dev_page = DeveloperPage()
    sql_query = dev_page.run_dev_page()


