from sqlalchemy import create_engine
import pandas as pd
import argparse

connection_string = 'mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create and populate tables in relevant database')
    parser.add_argument('file', help='csv file path')
    parser.add_argument('db', help='database name')
    parser.add_argument('table', help='table name')
    args = parser.parse_args()

    file_path, db, table = args.file, args.db, args.table

    records = pd.read_csv(file_path)
    engine = create_engine(connection_string + db)

    if 'Unnamed: 0' in records.columns.tolist():
        records = records.iloc[:,1:]

    records.to_sql(table, engine, index=False)
