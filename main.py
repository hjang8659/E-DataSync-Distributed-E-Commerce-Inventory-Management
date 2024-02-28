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