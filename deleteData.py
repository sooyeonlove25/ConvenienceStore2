from mysql.connector import MySQLConnection, Error
from config import read_config

def delete_book(book_id):
    # read database configuration
    config = read_config()

    # prepare query and data
    query = "DELETE FROM books WHERE id = %s"

    data = (book_id, ) 

    affected_rows = 0  # Initialize the variable to store the number of affected rows

    try:
        # connect to the database
        with MySQLConnection(**config) as conn:
            # update book title
            with conn.cursor() as cursor:
                cursor.execute(query, data)

                # get the number of affected rows
                affected_rows = cursor.rowcount

            # accept the changes
            conn.commit()

    except Error as error:
        print(error)

    return affected_rows  # Return the number of affected rows

if __name__ == '__main__':
    affected_rows = delete_book(84)
    print(f'Number of affected rows: {affected_rows}')

