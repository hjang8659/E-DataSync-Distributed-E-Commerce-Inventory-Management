from sqlalchemy import create_engine, MetaData
import argparse

connection_string = 'mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='delete table in a database')
    parser.add_argument('table', help='table name')
    parser.add_argument('db', help='database name')
    args = parser.parse_args()

    engine = create_engine(connection_string+args.db)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    table_to_delete = metadata.tables[args.table]
    table_to_delete.drop(engine)
