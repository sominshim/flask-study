import pymysql
import csv
from datetime import date, datetime
from models import Book
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Shim5186!!@localhost/users'

db_connection = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "Shim5186!!",
    db = "users"
)

con = db_connection
cur = con.cursor(pymysql.cursors.DictCursor)
cur.execute("desc book")

with open('book_info.csv') as datas :
    records = csv.DictReader(datas)
    result = [ (c['index'], c['book_name'], c['publisher'], c['author'], c['publication_date'], c['pages'], c['isbn'], c['description'], c['link'], c['img_path'], c['stock']) for c in records]
    # print(result)

# csv 파일 MysQL에 삽입
cur.executemany("insert into book(id, book_name, publisher, author, publication_date, pages, isbn, descrip, link, img_path, stock, score) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0);", result)

con.commit()
con.close()
