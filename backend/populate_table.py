from sqlalchemy import create_engine, text
import pandas as pd
from hashing import hash_prod
from tqdm import tqdm


engine = create_engine('mysql+pymysql://myuser3:Dsc!5602023@104.32.175.9:3306/mydatabase2')

df = pd.read_csv('../dataset/suppliers_1.csv')
if 'Unnamed: 0' in df.columns.tolist():
    df= df.iloc[:,1:]

df = df.drop_duplicates(subset=['brand'], keep='first')

rows = df.to_dict(orient='records')

for row in tqdm(rows):
    with engine.connect() as con:
        insert_query = text("INSERT INTO Suppliers VALUES (:brand, :address, :description, :founding_year, :num_of_products)")
        con.execute(insert_query, row)
        con.commit()


df = pd.read_csv('../dataset/products_1.csv')
if 'Unnamed: 0' in df.columns.tolist():
    df = df.iloc[:,1:]

df = df.drop_duplicates(subset=['product'], keep='first')

rows = df.to_dict(orient='records')

for row in tqdm(rows):
    with engine.connect() as con:
        insert_query = text("INSERT INTO Products VALUES (:product, :category, :sub_category, :brand, :sale_price, :market_price, :type, :rating, :description)")
        con.execute(insert_query, row)
        con.commit()