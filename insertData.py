from mysql.connector import MySQLConnection, Error
from config import read_config

def insert_book(title, isbn):
    query = "INSERT INTO books(title,isbn) " \
            "VALUES(%s,%s)"

    args = (title, isbn)
    book_id = None
    try:
        config = read_config()
        with MySQLConnection(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                book_id =  cursor.lastrowid
            conn.commit()
        return book_id
    except Error as error:
        print(error)

if __name__ == '__main__':
    insert_book('A Sudden Light', '9781439187036')
