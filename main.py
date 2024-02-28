import pandas as pd
from dbm_backend.dbm_operations import DBMOperations
from dbm_frontend.Home import DSCI551Project
import sys
import os

# Ensure that the dbm_frontend can be imported
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

if __name__ == '__main__':
    proj = DSCI551Project()
    proj.run()
    opr = DBMOperations()

    # Filter between lowercase(select, insert, update, delete)
    sql_query = "select * from Products limit 10"
    command_used = sql_query.split()[0].lower()
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