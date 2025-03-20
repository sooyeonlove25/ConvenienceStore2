from mysql.connector import MySQLConnection, Error
from config import read_config


def connect(config):
    """ Connect to MySQL database """
    conn = None
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**config)

        if conn.is_connected():
            print('Connection is established.')
        else:
            print('Connection is failed.')
    except Error as error:
        print(error)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print('Connection is closed.')


if __name__ == '__main__':
    config = read_config()
    connect(config)
