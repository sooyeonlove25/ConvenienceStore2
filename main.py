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
        

    elif menu == "4":
        action = input("수정하려면 1을, 삭제하려면 2를 입력하세요: ").strip()

        if action == "1":  # 수량 수정
            name = input("수정할 상품명을 입력하세요: ")
            num = input("새로운 수량을 입력하세요: ")

            updated_rows = csf.update_Product(conn, name, num)
            if updated_rows > 0:
                print(f"'{name}'의 수량이 {num}으로 변경되었습니다.")
            else:
                print("해당 상품을 찾을 수 없습니다.")

        elif action == "2":  # 삭제 기능 추가
            name = input("삭제할 상품명을 입력하세요: ")
            deleted_rows = csf.delete_Product(conn, name)

            if deleted_rows > 0:
                print(f"'{name}' 상품이 삭제되었습니다.")
            else:
                print("해당 상품을 찾을 수 없습니다.")

        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

    elif menu == "5":
        csf.show_product_logs(conn)

    elif menu == "6":
        print("프로그램 종료")
        conn.close()
        sys.exit()

    # 잘못된 입력 처리
    else:
        print("메뉴 선택을 잘못하셨습니다.")
