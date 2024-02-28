import streamlit as st
from streamlit.logger import get_logger
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
pages_dir = os.path.join(current_dir, 'pages')
sys.path.append(pages_dir)

class DSCI551Project:
    def __init__(self):
        self.logger = get_logger(__name__)

    def run(self):
        st.set_page_config(
            page_title="Home",
        )

        st.write("### DSCI 551 Project")

        st.write("# E-DataSync: Distributed E-Commerce Inventory Management")

        st.markdown(
            """
            E-DataSync is an innovative E-commerce inventory management system designed
            to enhance communication and interaction between database
            managers and end users across distributed databases. 
            The system focuses on three crucial relational tables: products, suppliers, and orders.
            The initial implementation involves data for the products table, and we are actively
            working on generating synthetic datasets for suppliers and orders tables, ensuring
            a comprehensive inventory management solution.
        """
        )

        st.write('### Team Members:')
        st.write('Christopher Apton (apton@usc.edu)')
        st.write('Daniel Jang (hyundong@usc.edu)')
        st.write('Shahzaib Saqib Warraich (warraich@usc.edu)')

if __name__ == "__main__":
    dsci_project = DSCI551Project()
    dsci_project.run()
