import streamlit as st
import subprocess
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
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
            st.button("Run Command")
            
        return cli_command

    def display(df):
        st.write(df.head())
        
if __name__ == "__main__":
    dev_page = DeveloperPage()
    dev_page.run_dev_page()
