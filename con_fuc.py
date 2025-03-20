from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser
import datetime


def read_config(filename="app.ini", section="mysql"):
    # Create a ConfigParser object to handle INI file parsing
    config = ConfigParser()

    # Read the specified INI configuration file
    config.read(filename)

    # Initialize an empty dictionary to store configuration data
    data = {}

    # Check if the specified section exists in the INI file
    if config.has_section(section):
        # Retrieve all key-value pairs within the specified section
        items = config.items(section)

        # Populate the data dictionary with the key-value pairs
        for item in items:
            data[item[0]] = item[1]
    else:
        # Raise an exception if the specified section is not found
        raise Exception(f"{section} section not found in the {filename} file")

    # Return the populated data dictionary
    return data


def connect():
    conn = None
    try:
        print("Connecting to MySQL database...")
        config = read_config()
        conn = MySQLConnection(**config)
    except Error as error:
        print(error)
    return conn


def insert_or_update_product(conn, pd_name, price, ex_date, num):
    with conn.cursor() as cursor:
        # 1. 동일한 상품이 있는지 확인
        check_query = """
        SELECT product_id FROM products
        WHERE name = %s AND price = %s AND expiration_date = %s
        """
        cursor.execute(check_query, (pd_name, price, ex_date))
        result = cursor.fetchone()

        if result:
            # 기존 상품 수량 업데이트
            product_id = result[0]
            update_query = """
            UPDATE products
            SET quantity = quantity + %s
            WHERE product_id = %s
            """
            cursor.execute(update_query, (num, product_id))
        else:
            # 신규 상품 추가
            insert_query = """
            INSERT INTO products (name, price, expiration_date, quantity)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (pd_name, price, ex_date, num))

            # 새로 생성된 product_id 조회
            cursor.execute("SELECT LAST_INSERT_ID()")
            product_id = cursor.fetchone()[0]

        # 2. product_id로 supplier 존재 여부 확인
        supplier_check_query = """
        SELECT supplier_id FROM suppliers
        WHERE product_id = %s
        """
        cursor.execute(supplier_check_query, (product_id,))
        supplier_result = cursor.fetchone()

        if not supplier_result:
            print(f"[경고] 상품 ID {product_id}는 공급업체 정보가 등록되어 있지 않습니다.")
            # 또는 필요한 경우: return product_id 해서 이후 supplier 추가 함수로 넘길 수도 있음

    conn.commit()
