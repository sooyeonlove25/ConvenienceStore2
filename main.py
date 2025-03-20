import sys
import con_fuc as cf

# 메뉴
display = """
-------------------------------------------------------------
1. 상품 정보 등록           | 2. 전체 재고 현황 조회
3. 공급 업체 검색           | 4. 판매 (재고 정보 수정 및 삭제)
5. 이력 조회                | 6. 프로그램 종료
-------------------------------------------------------------
메뉴를 선택하세요 >>> """

conn = cf.connect()


while True:
    menu = input(display).strip()

    # 상품 정보 등록
    if menu == "1":
        pd_name = input("상품명을 입력하세요: ")
        price = input("가격을 입력하세요: ")
        ex_date = input("유통기한을 입력하세요 (YYYY-MM-DD 형식): ")
        num = input("수량을 입력하세요: ")

        product_id = cf.generate_product_id(pd_name, price, ex_date)

        cf.insert_or_update_product(conn, product_id, pd_name, price, ex_date, num)

    # 전체 재고 현황 조회
    elif menu == "2":
        cf.query_with_fetchall(conn)

    # 공급 업체 검색
    elif menu == "3":
        cf.get_supplier_and_product_info(conn)

    # 판매
    elif menu == "4":
        cf.sell_list(conn)

        # 2. 사용자 입력 받기 (상품코드와 수량)
        product_id_input = int(input("판매할 상품 코드를 입력하세요: "))

        cf.sell_product(conn, product_id_input)

    # 이력 조회
    elif menu == "5":
        cf.view_stock_logs(conn)

    elif menu == "6":
        print("프로그램 종료")
        conn.close()
        sys.exit()

    # 잘못된 입력 처리
    else:
        print("메뉴 선택을 잘못하셨습니다.")
