from mysql.connector import MySQLConnection, Error
from config import read_config

def query_with_fetchall():
    try:
        config = read_config()
        # Establish a connection to the MySQL database using the provided configuration
        conn = MySQLConnection(**config)
        
        # Create a cursor to interact with the database
        cursor = conn.cursor()
        
        # Execute a SELECT query to retrieve all rows from the 'books' table
        cursor.execute("SELECT * FROM books")
        
        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Print the total number of rows returned by the query
        print('Total Row(s):', cursor.rowcount)
        
        # Loop through all rows and print them
        for row in rows:
            print(row)
        return rows

    except Error as e:
        # Print an error message if an error occurs during the execution of the query
        print(e)

    finally:
        # Close the cursor and connection in the 'finally' block to ensure it happens
        cursor.close()
        conn.close()

if __name__ == '__main__':
    config = read_config()
    # Call the function with the obtained configuration to execute the query
    query_with_fetchall(config)

