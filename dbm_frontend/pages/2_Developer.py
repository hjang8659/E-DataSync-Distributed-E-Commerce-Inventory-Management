import streamlit as st
import subprocess
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def authenticate():
    password = st.text_input("Enter Password:", type="password")
    return password == "dsci551"

def run_dev_page():
    st.set_page_config(
        page_title="Developer Page",
        page_icon="🛠️",
    )

    st.write("### Developer Page 🛠️")

    authenticated = authenticate()

    if authenticated:
        st.write("Authentication successful!")
        st.write("This is the developer page where you can perform development tasks.")

        # Add developer-specific content and functionality here

        # Example CLI section
        st.write("## Developer Command Line Interface")

        # Allow the user to input a command
        cli_command = st.text_input("Enter a command:")

        # Execute the command and display the output
        if cli_command:
            st.write("### Command Output:")
            try:
                if cli_command.startswith("SHOW TABLES;"):
                    # Connect to the database using SQLAlchemy
                    engine = create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase2')
                    
                    # Use parameterized query for safety
                    query = text(cli_command)
                    records = pd.read_sql(query, engine)
                    st.write(records)
                else:
                    # For other commands, use subprocess
                    output = subprocess.check_output(cli_command, shell=True, text=True)
                    st.code(output, language='text')
            except (subprocess.CalledProcessError, SQLAlchemyError) as e:
                st.error(f"Error executing command: {e}")
    else:
        st.error("Authentication failed. Please enter the correct password.")

if __name__ == "__main__":
    run_dev_page()
