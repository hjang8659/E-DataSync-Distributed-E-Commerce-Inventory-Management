# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Home",
        page_icon="🏠",
    )

    st.write("### DSCI 551 Project 🚀")

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
    run()