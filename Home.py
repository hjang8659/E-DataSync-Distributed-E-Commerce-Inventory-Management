import pandas as pd
from backend.dbm_ui_operations import DBMOperations
from frontend.main import DSCI551Project
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

if __name__ == '__main__':
    proj = DSCI551Project()
    proj.run()