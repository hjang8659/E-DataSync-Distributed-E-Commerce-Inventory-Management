from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
 
engine = create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase')

try:
    records = pd.read_sql('show tables', engine)
    # records = pd.read_sql('select * from Products', engine)
    print("connection successful", records.head())

except:
    print("connection unsuccessful")