from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser
from datetime import datetime
from tabulate import tabulate


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

            # 입고 이력 기록 (stock_logs에 추가)
            stock_log_query = """
            INSERT INTO stock_logs (change_type, quantity_change, change_time, product_id)
            VALUES ('입고', %s, NOW(), %s)
            """
            cursor.execute(stock_log_query, (num, product_id))

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

            # 신규 입고 이력 기록 (stock_logs에 추가)
            stock_log_query = """
            INSERT INTO stock_logs (change_type, quantity_change, change_time, product_id)
            VALUES ('입고', %s, NOW(), %s)
            """
            cursor.execute(stock_log_query, (num, product_id))

    conn.commit()



def query_with_fetchall(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    # 총 상품 개수 출력
    print(f"총 상품 개수: {cursor.rowcount}")
    print()

    if rows:
        # 표 형식으로 출력할 컬럼 헤더
        headers = ["상품 ID", "상품명", "가격", "유통기한", "수량"]

        # 결과 데이터를 표 형식으로 변환
        table = [
            (row[0], row[1], row[2], row[3], row[4]) for row in rows
        ]

        # 표 형식으로 출력
        print(tabulate(table, headers=headers, tablefmt="grid", numalign="center"))
    else:
        print("상품 목록이 없습니다.")


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


# 메뉴3번(공급업체랑 상품과 join 출력력)
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
    if rows:
        # 표 형식으로 출력할 컬럼 헤더
        headers = [
            "공급업체 ID", "공급업체 이름", "연락처", "주소", 
            "상품 ID", "상품명", "가격", "유통기한", "수량"
        ]
        
        # 결과 데이터를 표 형식으로 변환
        table = [(
            row[0],  # supplier_id
            row[1],  # supplier_name
            row[2],  # supplier_contact
            row[3],  # supplier_address
            row[4],  # product_id
            row[5],  # product_name
            row[6],  # product_price
            row[7],  # product_expiration
            row[8]   # product_quantity
        ) for row in rows]

        # 표 형식으로 출력
        print(tabulate(table, headers=headers, tablefmt="grid", numalign="center"))
    else:
        print("공급업체 및 제품 정보가 없습니다.")

# 메뉴4번(초기목록생성)
def sell_list(conn):
    cursor = conn.cursor()

    # 1. 상품 목록 출력
    print("판매할 상품 목록:")
    cursor.execute("SELECT product_id, name, quantity, price FROM products")
    products = cursor.fetchall()

    if not products:
        print("등록된 상품이 없습니다.")
        return

    for product in products:
        product_id, name, quantity, price = product
        print(f"상품 코드: {product_id}, 상품명: {name}, 수량: {quantity}, 가격: {price}원")

    print("-" * 40)


# 메뉴4번(판매)
def sell_product(conn, product_id_input):
    cursor = conn.cursor()

    # 3. 입력한 상품이 존재하는지 확인
    cursor.execute(
        "SELECT product_id, name, quantity, price FROM products WHERE product_id = %s",
        (product_id_input,),
    )
    product = cursor.fetchone()

    if not product:
        print("해당 상품은 존재하지 않습니다.")
        return

    product_id, name, available_quantity, price = product  # 가격을 추가로 가져옴

    # 4. 판매할 수량 입력받기
    quantity_to_sell = int(input("판매할 수량을 입력하세요: "))

    # 5. 판매 수량이 재고보다 많은지 확인
    if quantity_to_sell > available_quantity:
        print("판매 수량이 재고보다 많습니다.")
        return

    # 6. 수량 업데이트
    new_quantity = available_quantity - quantity_to_sell
    cursor.execute(
        """
        UPDATE products
        SET quantity = %s
        WHERE product_id = %s
    """,
        (new_quantity, product_id),
    )

    # 7. 판매 이력 기록 (sales 테이블에 저장)
    total_price = quantity_to_sell * price  # 가격을 테이블에서 가져온 값으로 계산
    cursor.execute(
        """
        INSERT INTO sales (quantity_sold, total_price, sale_date, product_id)
        VALUES (%s, %s, NOW(), %s)
    """,
        (quantity_to_sell, total_price, product_id),
    )

    # 8. 판매 이력 기록 (stock_logs 테이블에 저장)
    cursor.execute(
        """
        INSERT INTO stock_logs (change_type, quantity_change, change_time, product_id)
        VALUES ('판매', %s, NOW(), %s)
    """,
        (quantity_to_sell, product_id),
    )

    # 변경사항 커밋
    conn.commit()

    print(f"{name} 상품의 수량이 {quantity_to_sell}개 판매되었습니다.")
    print(f"판매 금액: {total_price}원")

# 메뉴5번(이력 조회)
def view_stock_logs(conn):
    cursor = conn.cursor()

    # stock_logs와 products 테이블을 JOIN하여 필요한 데이터 조회
    cursor.execute("""
        SELECT 
            sl.change_type,
            sl.quantity_change,
            sl.change_time,
            p.product_id,
            p.name
        FROM 
            stock_logs sl
        JOIN 
            products p ON sl.product_id = p.product_id;
    """)

    # 결과 가져오기
    records = cursor.fetchall()

    # 결과 출력
    if records:
        # 표 형식으로 출력
        headers = ["상품명", "상품번호", "변경 유형", "수량 변화", "변경 시간"]
        table = [(
            record[4],  # name
            record[3],  # product_id
            record[0],  # change_type
            record[1],  # quantity_change
            record[2]   # change_time
        ) for record in records]
        
        print(tabulate(table, headers=headers, tablefmt="grid", numalign="center"))
    else:
        print("판매/입고 이력이 없습니다.")
