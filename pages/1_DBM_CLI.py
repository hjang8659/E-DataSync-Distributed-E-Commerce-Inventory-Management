import streamlit as st
from backend.dbm_ui_operations import DBMOperations

class DeveloperPage:
    def __init__(self):
        st.set_page_config(
            page_title="Developer Page",
            layout="wide",  # Set layout to wide
        )

    def authenticate(self):
        password = st.text_input("Enter Password:", type="password")
        return password == "dsci551"

    def run_dev_page(self):
        st.markdown(
            """
            <style>
                body {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .dataframe {
                    width: 100% !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.title("Database Manager CLI UI")
        st.image('frontend/ERD.png')

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
                    flag, res = opr.select(sql_query)
                    if flag == 0:
                        st.error("Error: Syntax error or database error")
                    else:
                        st.dataframe(res, height=400, width=2300)
                        st.success("Operation Successful. Displaying records across both databases.")
                elif command_used == "insert":
                    flag = opr.insert(sql_query)
                    if flag == 0:
                        st.error("Error: Syntax error or database error")
                    else:
                        st.success("Operation Successful")
                elif command_used == "update":
                    flag = opr.update(sql_query)
                    if flag == 0:
                        st.error("Error: Syntax error or database error")
                    else:
                        st.success("Operation Successful")
                elif command_used == "delete":
                    flag = opr.delete(sql_query)
                    if flag == 0:
                        st.error("Error: Syntax error or database error")
                    else:
                        st.success("Operation Successful")
                else:
                    st.error(f"Unknown command used: {command_used}")

        else:
            st.error("Authentication failed.")

if __name__ == "__main__":
    dev_page = DeveloperPage()
    dev_page.run_dev_page()