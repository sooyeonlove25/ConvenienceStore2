-- 1. products 테이블: 다른 테이블들이 참조함
DROP TABLE IF EXISTS `products`;

CREATE TABLE `products` (
	`product_id` INT NOT NULL PRIMARY KEY,  -- 수동 생성
	`name` VARCHAR(255) NOT NULL,
	`price` DECIMAL(10,2) NOT NULL,
	`expiration_date` DATE NOT NULL,
	`quantity` INT NOT NULL
);

-- 2. sales 테이블: products 참조
DROP TABLE IF EXISTS `sales`;

CREATE TABLE `sales` (
	`sale_id` INT NOT NULL AUTO_INCREMENT,
	`quantity_sold` INT NOT NULL,
	`total_price` DECIMAL(10,2) NOT NULL,
	`sale_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`product_id` INT NOT NULL,
	PRIMARY KEY (`sale_id`),
	FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
);

-- 3. stock_logs 테이블: products 참조
DROP TABLE IF EXISTS `stock_logs`;

CREATE TABLE `stock_logs` (
	`log_id` INT NOT NULL AUTO_INCREMENT,
	`change_type` ENUM('입고', '판매') NOT NULL,
	`quantity_change` INT NOT NULL,
	`change_time` TIMESTAMP NULL,
	`product_id` INT NOT NULL,
	PRIMARY KEY (`log_id`),
	FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
);

-- 4. suppliers 테이블: products 참조
DROP TABLE IF EXISTS `suppliers`;

CREATE TABLE `suppliers` (
	`supplier_id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL,
	`contact` VARCHAR(50) NULL,
	`address` TEXT NULL,
	`product_id` INT NOT NULL,
	PRIMARY KEY (`supplier_id`),
	FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
);

select * from products;
select * from suppliers;
select * from sales;
select * from stock_logs;
DELETE FROM products;
DELETE FROM sales;
DELETE FROM stock_logs;
DELETE FROM suppliers;



-- 가짜 공급업체 정보 생성
INSERT INTO suppliers (supplier_id, name, contact, address,product_id)
VALUES
(1, '회사_ABCDE', '010-1000-1234', '서울시 강남구 1번길',129653),
(2, '회사_BCDFA', '010-1000-5678', '부산시 해운대구 2번길',134057),
(3, '회사_CDEFH', '010-1000-4321', '대구시 수성구 3번길',138647),
(4, '회사_DEFGH', '010-1000-8765', '인천시 연수구 4번길',133784),
(5, '회사_EFGHI', '010-1000-1357', '광주시 북구 5번길',142369);

-- 가짜 상품 정보 생성
INSERT INTO products (product_id, name, price, expiration_date, quantity)
VALUES
(129653, '아이스크림', 2000, '2025-06-30', 100),
(134057, '음료수', 1500, '2025-12-31', 50),
(138647, '스낵', 1200, '2025-09-15', 80),
(133784, '초콜릿', 2500, '2025-07-22', 40),
(142369, '과자', 1500, '2025-08-10', 60);

-- 가짜 입고/판매 기록 생성 (출고 대신 판매로 변경)
INSERT INTO stock_logs (log_id, change_type, quantity_change, change_time, product_id)
VALUES
(1, '입고', 50, '2025-03-01 10:00:00', 129653),
(2, '판매', 20, '2025-03-02 14:30:00', 129653),
(3, '입고', 30, '2025-03-03 09:00:00', 134057),
(4, '판매', 10, '2025-03-04 11:15:00', 134057),
(5, '입고', 40, '2025-03-05 13:30:00', 138647);

-- 가짜 판매 기록 생성
INSERT INTO sales (sale_id, quantity_sold, total_price, sale_date, product_id)
VALUES
(1, 10, 20000, '2025-03-02 14:00:00', 129653),
(2, 5, 7500, '2025-03-03 16:00:00', 134057),
(3, 15, 18000, '2025-03-04 18:30:00', 138647),
(4, 8, 20000, '2025-03-05 17:00:00', 133784),
(5, 12, 18000, '2025-03-06 14:30:00', 142369);

