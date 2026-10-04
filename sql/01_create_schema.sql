-- =============================================================================
-- 01_create_schema.sql  -  star schema for E-Commerce Growth Analytics
-- Author: Pranit Ajay Chaudhari
-- Engine: MySQL 8 / MariaDB 10.5+
--
-- PART A (Olist marketplace) is a star schema: two fact tables surrounded by
-- customer, product, seller and date dimensions.
-- PART B (campaign dataset) is ONE separate table. The two datasets share no
-- customer, product, date or geography key, so no foreign key joins them and no
-- query in 03_business_queries.sql joins across them. Keeping them apart is a
-- deliberate modelling decision, not an omission - see docs/METHODOLOGY.md.
-- =============================================================================

DROP DATABASE IF EXISTS ecommerce_growth;
CREATE DATABASE ecommerce_growth
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_growth;

-- ------------------------------------------------------------ DIMENSIONS ----
CREATE TABLE dim_customer (
    customer_id        VARCHAR(40)   NOT NULL,
    state              CHAR(2)       NOT NULL,
    city               VARCHAR(80)   NOT NULL,
    cohort_month       CHAR(7)       NOT NULL,   -- YYYY-MM of the first order
    orders             INT           NOT NULL,
    total_revenue      DECIMAL(12,2) NOT NULL,
    first_order_value  DECIMAL(10,2) NOT NULL,
    aov                DECIMAL(10,2) NOT NULL,
    recency_days       INT           NOT NULL,
    tenure_days        INT           NOT NULL,
    is_repeat          TINYINT(1)    NOT NULL,
    value_tier         VARCHAR(10)   NOT NULL,
    avg_review_score   DECIMAL(4,2)  NULL,
    PRIMARY KEY (customer_id),
    KEY ix_cust_state  (state),
    KEY ix_cust_tier   (value_tier),
    KEY ix_cust_cohort (cohort_month),
    KEY ix_cust_repeat (is_repeat)
) ENGINE=InnoDB;

CREATE TABLE dim_product (
    product_id   VARCHAR(40) NOT NULL,
    category     VARCHAR(60) NOT NULL,
    PRIMARY KEY (product_id),
    KEY ix_prod_cat (category)
) ENGINE=InnoDB;

CREATE TABLE dim_seller (
    seller_id    VARCHAR(40) NOT NULL,
    seller_state CHAR(2)     NULL,
    PRIMARY KEY (seller_id),
    KEY ix_sell_state (seller_state)
) ENGINE=InnoDB;

CREATE TABLE dim_date (
    date_key     DATE    NOT NULL,
    year         INT     NOT NULL,
    quarter      INT     NOT NULL,
    month_num    INT     NOT NULL,
    month_name   CHAR(3) NOT NULL,
    month_key   CHAR(7) NOT NULL,
    day_of_week  INT     NOT NULL,
    PRIMARY KEY (date_key),
    KEY ix_date_ym (month_key)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------- FACTS ----
CREATE TABLE fact_orders (
    order_id             VARCHAR(40)   NOT NULL,
    customer_id          VARCHAR(40)   NOT NULL,
    order_date           DATETIME      NOT NULL,
    order_day            DATE          NOT NULL,
    order_month          CHAR(7)       NOT NULL,
    items                INT           NOT NULL,
    distinct_products    INT           NOT NULL,
    distinct_sellers     INT           NOT NULL,
    items_value          DECIMAL(10,2) NOT NULL,
    freight              DECIMAL(10,2) NOT NULL,
    order_value          DECIMAL(10,2) NOT NULL,
    payment_type         VARCHAR(20)   NULL,
    payment_installments INT           NULL,
    review_score         INT           NULL,
    delivery_days        INT           NOT NULL,
    days_vs_promise      INT           NOT NULL,
    late_delivery        TINYINT(1)    NOT NULL,
    order_seq            INT           NOT NULL,
    is_first_order       TINYINT(1)    NOT NULL,
    PRIMARY KEY (order_id),
    KEY ix_ord_cust  (customer_id),
    KEY ix_ord_day   (order_day),
    KEY ix_ord_month (order_month),
    KEY ix_ord_first (is_first_order),
    KEY ix_ord_late  (late_delivery),
    CONSTRAINT fk_ord_cust FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    CONSTRAINT fk_ord_date FOREIGN KEY (order_day)   REFERENCES dim_date (date_key)
) ENGINE=InnoDB;

CREATE TABLE fact_order_items (
    order_id      VARCHAR(40)   NOT NULL,
    order_item_id INT           NOT NULL,
    product_id    VARCHAR(40)   NOT NULL,
    seller_id     VARCHAR(40)   NOT NULL,
    price         DECIMAL(10,2) NOT NULL,
    freight_value DECIMAL(10,2) NOT NULL,
    line_revenue  DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    KEY ix_itm_prod (product_id),
    KEY ix_itm_sell (seller_id),
    CONSTRAINT fk_itm_ord  FOREIGN KEY (order_id)   REFERENCES fact_orders (order_id),
    CONSTRAINT fk_itm_prod FOREIGN KEY (product_id) REFERENCES dim_product (product_id),
    CONSTRAINT fk_itm_sell FOREIGN KEY (seller_id)  REFERENCES dim_seller (seller_id)
) ENGINE=InnoDB;

-- --------------------------------------------- PART B (standalone, no FKs) ---
CREATE TABLE campaign_customers (
    customer_ref        INT           NOT NULL,
    age                 INT           NOT NULL,
    age_band            VARCHAR(10)   NOT NULL,
    education           VARCHAR(20)   NOT NULL,
    marital_status      VARCHAR(20)   NOT NULL,
    partnered           TINYINT(1)    NOT NULL,
    income              DECIMAL(10,2) NOT NULL,
    income_band         VARCHAR(12)   NOT NULL,
    children            INT           NOT NULL,
    has_children        TINYINT(1)    NOT NULL,
    enrolled_date       DATE          NOT NULL,
    tenure_days         INT           NOT NULL,
    recency             INT           NOT NULL,
    mnt_wines           INT           NOT NULL,
    mnt_fruits          INT           NOT NULL,
    mnt_meat            INT           NOT NULL,
    mnt_fish            INT           NOT NULL,
    mnt_sweet           INT           NOT NULL,
    mnt_gold            INT           NOT NULL,
    total_spend         INT           NOT NULL,
    num_deals_purchases INT           NOT NULL,
    num_web_purchases   INT           NOT NULL,
    num_catalog_purchases INT         NOT NULL,
    num_store_purchases INT           NOT NULL,
    total_purchases     INT           NOT NULL,
    deal_share          DECIMAL(6,4)  NULL,
    web_visits_month    INT           NOT NULL,
    accepted_cmp1       TINYINT(1)    NOT NULL,
    accepted_cmp2       TINYINT(1)    NOT NULL,
    accepted_cmp3       TINYINT(1)    NOT NULL,
    accepted_cmp4       TINYINT(1)    NOT NULL,
    accepted_cmp5       TINYINT(1)    NOT NULL,
    campaigns_accepted  INT           NOT NULL,
    response            TINYINT(1)    NOT NULL,
    complain            TINYINT(1)    NOT NULL,
    r_score             INT           NOT NULL,
    f_score             INT           NOT NULL,
    m_score             INT           NOT NULL,
    rfm_score           INT           NOT NULL,
    value_tier          VARCHAR(12)   NOT NULL,
    discount_behaviour  VARCHAR(12)   NOT NULL,
    PRIMARY KEY (customer_ref),
    KEY ix_cc_tier     (value_tier),
    KEY ix_cc_discount (discount_behaviour),
    KEY ix_cc_income   (income_band)
) ENGINE=InnoDB;
