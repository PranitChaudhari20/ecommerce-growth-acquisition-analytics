-- =============================================================================
-- 02_import_data.sql  -  load the cleaned CSVs into the star schema
-- Author: Pranit Ajay Chaudhari
--
-- Run after 01_create_schema.sql. Paths are repo-relative; python/run_sql.py
-- rewrites them to absolute paths before execution.
-- Requires local_infile=1 on both client and server.
-- Load order follows the foreign keys: dimensions first, then facts.
-- =============================================================================
USE ecommerce_growth;
SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------- staging ------
DROP TEMPORARY TABLE IF EXISTS stg_items;
CREATE TEMPORARY TABLE stg_items (
    order_id      VARCHAR(40),
    order_item_id INT,
    product_id    VARCHAR(40),
    seller_id     VARCHAR(40),
    seller_state  VARCHAR(10),
    category      VARCHAR(60),
    price         DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    line_revenue  DECIMAL(10,2),
    KEY (product_id), KEY (seller_id)
) ENGINE=InnoDB;

LOAD DATA LOCAL INFILE 'data/cleaned/partA_order_items.csv'
INTO TABLE stg_items
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(order_id, order_item_id, product_id, seller_id, seller_state, category, price, freight_value, line_revenue);

-- ---------------------------------------------------------- dimensions ------
LOAD DATA LOCAL INFILE 'data/cleaned/partA_customers.csv'
INTO TABLE dim_customer
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(customer_id, orders, total_revenue, @first_dt, @last_dt, state, city, @items,
 @avg_review, @late_orders, @avg_del, aov, recency_days, tenure_days, @is_repeat,
 first_order_value, value_tier, cohort_month)
SET is_repeat        = IF(@is_repeat = 'True', 1, 0),
    avg_review_score = NULLIF(@avg_review, '');

-- Product and seller dimensions are derived from the order lines: a product that
-- never sold has no place in a sales star schema.
INSERT INTO dim_product (product_id, category)
SELECT product_id, MIN(category) FROM stg_items GROUP BY product_id;

INSERT INTO dim_seller (seller_id, seller_state)
SELECT seller_id, NULLIF(MIN(seller_state), '') FROM stg_items GROUP BY seller_id;

-- dim_date is generated, not loaded: a recursive CTE walks every day across the
-- analysis window so the date dimension is dense even on days with no orders.
INSERT INTO dim_date (date_key, year, quarter, month_num, month_name, month_key, day_of_week)
WITH RECURSIVE cal (d) AS (
    SELECT DATE('2016-09-01')
    UNION ALL
    SELECT d + INTERVAL 1 DAY FROM cal WHERE d < DATE('2018-10-31')
)
SELECT d, YEAR(d), QUARTER(d), MONTH(d), DATE_FORMAT(d, '%b'),
       DATE_FORMAT(d, '%Y-%m'), DAYOFWEEK(d)
FROM cal;

-- ---------------------------------------------------------------- facts -----
LOAD DATA LOCAL INFILE 'data/cleaned/partA_orders.csv'
INTO TABLE fact_orders
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(order_id, customer_id, @state, @city, @order_date, items, distinct_products, distinct_sellers,
 items_value, freight, order_value, @pay_type, @inst, @methods, @review, delivery_days,
 @est_days, days_vs_promise, @late, order_month, @freight_share, order_seq, @is_first, @days_prev)
SET order_date           = STR_TO_DATE(@order_date, '%Y-%m-%d %H:%i:%s'),
    order_day            = DATE(STR_TO_DATE(@order_date, '%Y-%m-%d %H:%i:%s')),
    payment_type         = NULLIF(@pay_type, ''),
    payment_installments = NULLIF(@inst, ''),
    review_score         = NULLIF(@review, ''),
    late_delivery        = IF(@late = 'True', 1, 0),
    is_first_order       = IF(@is_first = 'True', 1, 0);

INSERT INTO fact_order_items (order_id, order_item_id, product_id, seller_id, price, freight_value, line_revenue)
SELECT s.order_id, s.order_item_id, s.product_id, s.seller_id, s.price, s.freight_value, s.line_revenue
FROM stg_items s
JOIN fact_orders o ON o.order_id = s.order_id;

-- ------------------------------------------------------- Part B (separate) --
LOAD DATA LOCAL INFILE 'data/cleaned/partB_customers.csv'
INTO TABLE campaign_customers
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(customer_ref, age, age_band, education, marital_status, @partnered, income, income_band,
 @kid, @teen, children, @has_children, @enrolled, tenure_days, recency,
 mnt_wines, mnt_fruits, mnt_meat, mnt_fish, mnt_sweet, mnt_gold, total_spend, @wine_share,
 num_deals_purchases, num_web_purchases, num_catalog_purchases, num_store_purchases,
 @full_price, total_purchases, @deal_share, @avg_spend_pp, web_visits_month,
 accepted_cmp1, accepted_cmp2, accepted_cmp3, accepted_cmp4, accepted_cmp5,
 campaigns_accepted, @any_campaign, response, complain,
 r_score, f_score, m_score, rfm_score, value_tier, discount_behaviour, @responder)
SET partnered    = IF(@partnered = 'True', 1, 0),
    has_children = IF(@has_children = 'True', 1, 0),
    enrolled_date = STR_TO_DATE(@enrolled, '%Y-%m-%d'),
    deal_share   = NULLIF(@deal_share, '');

-- ------------------------------------------------------------ self-check ----
-- These five numbers must match the Python output exactly. If any differs, the
-- import is wrong and no query result below it can be trusted.
SELECT (SELECT COUNT(*) FROM fact_orders)        AS orders,
       (SELECT COUNT(*) FROM dim_customer)       AS customers,
       (SELECT COUNT(*) FROM fact_order_items)   AS order_lines,
       (SELECT COUNT(*) FROM dim_product)        AS products,
       (SELECT COUNT(*) FROM dim_seller)         AS sellers,
       (SELECT COUNT(*) FROM campaign_customers) AS campaign_customers,
       (SELECT ROUND(SUM(order_value), 2) FROM fact_orders) AS gross_revenue;
