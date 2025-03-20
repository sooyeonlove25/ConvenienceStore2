from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser
from datetime import datetime


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


def generate_product_id(pd_name, price, ex_date):
    # pd_name을 ASCII 값의 합으로 변환
    name_sum = sum(ord(c) for c in pd_name)

    # price를 정수형으로 변환
    price_int = int(price)

    # ex_date를 날짜로 변환하고, 연도-월-일을 숫자로 결합
    ex_date_obj = datetime.strptime(ex_date, "%Y-%m-%d")
    ex_date_number = (
        ex_date_obj.year * 10000 + ex_date_obj.month * 100 + ex_date_obj.day
    )

    # 세 값을 조합하여 product_id 생성
    product_id = name_sum + price_int + ex_date_number

    return product_id


def insert_or_update_product(conn, product_id, pd_name, price, ex_date, num):
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
            existing_id = result[0]
            update_query = """
            UPDATE products
            SET quantity = quantity + %s
            WHERE product_id = %s
            """
            cursor.execute(update_query, (num, existing_id))
            product_id = existing_id  # 실제 사용된 product_id
        else:
            # 신규 상품 등록
            insert_query = """
            INSERT INTO products (product_id, name, price, expiration_date, quantity)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (product_id, pd_name, price, ex_date, num))

            # ------ supplier 자동 생성 및 등록 ------
            sup_name = generate_fake_supplier_name(product_id)
            sup_contact = generate_fake_phone(product_id)
            sup_address = generate_fake_address(product_id)

            supplier_insert = """
            INSERT INTO suppliers (name, contact, address, product_id)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                supplier_insert, (sup_name, sup_contact, sup_address, product_id)
            )
            # ----------------------------------------

    conn.commit()


def query_with_fetchall(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    print("총 상품 개수:", cursor.rowcount)
    print()

    for idx, row in enumerate(rows, start=1):
        product_id, name, price, ex_date, quantity = row
        print(f"[{idx}] 상품 ID: {product_id}")
        print(f"    상품명: {name}")
        print(f"    가격: {price}원")
        print(f"    유통기한: {ex_date}")
        print(f"    수량: {quantity}개")
        print("-" * 40)

    return rows


# 가짜 회사명명
def generate_fake_supplier_name(product_id):
    # 임의로 알파벳을 섞어서 "회사 이름"처럼 구성
    base = "ABCDEFHIJKLMNOPQRSTUVWXYZ"
    code = ""

    # 숫자를 알파벳으로 매핑 (바코드 느낌)
    for digit in str(product_id):
        index = int(digit) % len(base)
        code += base[index]

    # 앞에 "회사_" 접두사 붙이기
    supplier_name = f"회사_{code[:5]}"  # 예: 회사_BCADE
    return supplier_name


# 가짜 전화번호
def generate_fake_phone(product_id):
    base_number = 10000000 + (product_id % 90000000)
    return f"010-{str(base_number)[:4]}-{str(base_number)[4:]}"


# 가짜 주소
def generate_fake_address(product_id):
    region_code = product_id % 10
    regions = [
        "서울시 강남구",
        "부산시 해운대구",
        "대구시 수성구",
        "인천시 연수구",
        "광주시 북구",
        "대전시 서구",
        "울산시 남구",
        "경기도 성남시",
        "경기도 수원시",
        "제주도 제주시",
    ]
    return f"{regions[region_code]} {product_id % 100}번길"


# 메뉴3번
def get_supplier_and_product_info(conn):
    # 커서 생성
    cursor = conn.cursor()
    
    # 공급업체와 제품 정보를 JOIN하여 조회하는 쿼리
    query = """
    SELECT 
        s.supplier_id, 
        s.name AS supplier_name, 
        s.contact AS supplier_contact, 
        s.address AS supplier_address, 
        p.product_id, 
        p.name AS product_name, 
        p.price AS product_price, 
        p.expiration_date AS product_expiration, 
        p.quantity AS product_quantity
    FROM 
        suppliers s
    JOIN 
        products p ON s.product_id = p.product_id;
    """
    
    # 쿼리 실행
    cursor.execute(query)
    rows = cursor.fetchall()

    # 결과 출력
    print("공급업체 및 제품 정보:")
    for row in rows:
        print(f"공급업체 ID: {row[0]}, 공급업체 이름: {row[1]}, 연락처: {row[2]}, 주소: {row[3]}")
        print(f"상품 ID: {row[4]}, 상품명: {row[5]}, 가격: {row[6]}, 유통기한: {row[7]}, 수량: {row[8]}")
        print("-" * 40)
