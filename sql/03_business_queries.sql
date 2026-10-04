-- =============================================================================
-- 03_business_queries.sql  -  the business questions, answered in SQL
-- Author: Pranit Ajay Chaudhari
--
-- Queries 1-13 run on the Part A star schema (Olist marketplace).
-- Queries 14-17 run on the Part B table (campaign dataset).
-- No query joins the two: they describe different companies and share no key.
--
-- Every figure produced here is cross-checked against the Python output by
-- python/07_verify.py. Where the two disagreed during development, the cause was
-- found and fixed in code rather than reconciled by hand.
-- =============================================================================
USE ecommerce_growth;

-- QUERY 01 | Headline KPIs | What is the size and shape of this marketplace?
SELECT COUNT(*)                                             AS orders,
       COUNT(DISTINCT customer_id)                          AS customers,
       ROUND(SUM(order_value), 2)                           AS gross_revenue,
       ROUND(AVG(order_value), 2)                           AS avg_order_value,
       ROUND(SUM(freight) / SUM(order_value) * 100, 2)      AS freight_pct_of_revenue,
       ROUND(AVG(delivery_days), 2)                         AS avg_delivery_days,
       ROUND(AVG(late_delivery) * 100, 2)                   AS late_delivery_pct,
       ROUND(AVG(review_score), 2)                          AS avg_review_score,
       ROUND(AVG(payment_installments > 1) * 100, 2)        AS installment_orders_pct
FROM fact_orders;

-- QUERY 02 | Order frequency distribution | Is RFM segmentation even applicable here?
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS orders, SUM(order_value) AS revenue
    FROM fact_orders GROUP BY customer_id
)
SELECT orders                                                         AS orders_placed,
       COUNT(*)                                                       AS customers,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)               AS pct_of_customers,
       ROUND(SUM(revenue), 2)                                         AS revenue,
       ROUND(SUM(revenue) / SUM(SUM(revenue)) OVER () * 100, 2)       AS pct_of_revenue
FROM per_customer
GROUP BY orders
ORDER BY orders;

-- QUERY 03 | First vs repeat revenue | How much of the business is repeat custom?
SELECT CASE WHEN is_first_order = 1 THEN 'First order' ELSE 'Repeat order' END AS order_type,
       COUNT(*)                                                   AS orders,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)           AS pct_of_orders,
       ROUND(SUM(order_value), 2)                                 AS revenue,
       ROUND(SUM(order_value) / SUM(SUM(order_value)) OVER () * 100, 2) AS pct_of_revenue,
       ROUND(AVG(order_value), 2)                                 AS aov
FROM fact_orders
GROUP BY is_first_order
ORDER BY is_first_order DESC;

-- QUERY 04 | Customer value decomposition | Where does a customer's value come from?
WITH firsts AS (
    SELECT AVG(order_value) AS avg_first FROM fact_orders WHERE is_first_order = 1
), repeats AS (
    SELECT AVG(order_value) AS avg_repeat, COUNT(*) AS repeat_orders
    FROM fact_orders WHERE is_first_order = 0
), base AS (
    SELECT COUNT(*) AS customers, AVG(is_repeat) AS repeat_rate FROM dim_customer
)
SELECT ROUND(f.avg_first, 2)                                  AS avg_first_order_value,
       ROUND(b.repeat_rate * 100, 2)                          AS repeat_rate_pct,
       ROUND(r.avg_repeat, 2)                                 AS avg_repeat_order_value,
       ROUND(r.avg_repeat * r.repeat_orders / b.customers, 2) AS retention_contribution,
       ROUND(f.avg_first + r.avg_repeat * r.repeat_orders / b.customers, 2) AS revenue_per_customer,
       ROUND(f.avg_first / (f.avg_first + r.avg_repeat * r.repeat_orders / b.customers) * 100, 2)
                                                              AS pct_value_on_first_order
FROM firsts f CROSS JOIN repeats r CROSS JOIN base b;

-- QUERY 05 | Value tiers | Who are the high, medium and low value customers?
SELECT value_tier,
       COUNT(*)                                                  AS customers,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)          AS pct_of_customers,
       ROUND(SUM(total_revenue), 2)                              AS revenue,
       ROUND(SUM(total_revenue) / SUM(SUM(total_revenue)) OVER () * 100, 2) AS pct_of_revenue,
       ROUND(AVG(total_revenue), 2)                              AS avg_revenue,
       ROUND(AVG(orders), 2)                                     AS avg_orders,
       ROUND(AVG(is_repeat) * 100, 2)                            AS repeat_rate_pct,
       ROUND(AVG(avg_review_score), 2)                           AS avg_review_score
FROM dim_customer
GROUP BY value_tier
ORDER BY revenue DESC;

-- QUERY 06 | State acquisition economics | Which states are worth acquiring in?
SELECT c.state,
       COUNT(DISTINCT c.customer_id)                     AS customers,
       COUNT(o.order_id)                                 AS orders,
       ROUND(SUM(o.order_value), 2)                      AS revenue,
       ROUND(SUM(o.order_value) / SUM(SUM(o.order_value)) OVER () * 100, 2) AS pct_of_revenue,
       ROUND(AVG(o.order_value), 2)                      AS aov,
       ROUND(SUM(o.freight) / SUM(o.order_value) * 100, 2) AS freight_share_pct,
       ROUND(AVG(o.delivery_days), 2)                    AS avg_delivery_days,
       ROUND(AVG(o.late_delivery) * 100, 2)              AS late_pct,
       ROUND(AVG(o.review_score), 2)                     AS avg_review,
       -- Measured over DISTINCT customers. AVG(c.is_repeat) across this join would weight each
       -- repeat customer by their order count and roughly double the rate.
       ROUND(COUNT(DISTINCT CASE WHEN c.is_repeat = 1 THEN c.customer_id END)
             / COUNT(DISTINCT c.customer_id) * 100, 2)   AS repeat_rate_pct
FROM dim_customer c
JOIN fact_orders o ON o.customer_id = c.customer_id
GROUP BY c.state
ORDER BY revenue DESC;

-- QUERY 07 | Category entry vs return | Which categories bring customers in, and back?
SELECT p.category,
       COUNT(*)                                                     AS line_count,
       ROUND(SUM(i.line_revenue), 2)                                AS revenue,
       ROUND(SUM(i.line_revenue) / SUM(SUM(i.line_revenue)) OVER () * 100, 2) AS pct_of_revenue,
       ROUND(AVG(i.price), 2)                                       AS avg_price,
       COUNT(DISTINCT i.seller_id)                                  AS sellers,
       SUM(o.is_first_order)                                        AS first_order_lines,
       SUM(1 - o.is_first_order)                                    AS repeat_order_lines,
       ROUND(SUM(1 - o.is_first_order) / COUNT(*) * 100, 2)         AS repeat_line_share_pct
FROM fact_order_items i
JOIN dim_product p ON p.product_id = i.product_id
JOIN fact_orders  o ON o.order_id  = i.order_id
GROUP BY p.category
HAVING line_count >= 200
ORDER BY revenue DESC;

-- QUERY 08 | Delivery speed vs repeat purchase | Does fast delivery buy loyalty?
WITH first_orders AS (
    SELECT o.order_id, o.delivery_days, o.late_delivery, o.review_score, c.is_repeat
    FROM fact_orders o
    JOIN dim_customer c ON c.customer_id = o.customer_id
    WHERE o.is_first_order = 1
)
SELECT CASE WHEN delivery_days <=  3 THEN '0-3 days'
            WHEN delivery_days <=  7 THEN '4-7 days'
            WHEN delivery_days <= 14 THEN '8-14 days'
            WHEN delivery_days <= 21 THEN '15-21 days'
            ELSE '22+ days' END                        AS delivery_band,
       COUNT(*)                                        AS first_orders,
       SUM(is_repeat)                                  AS became_repeat,
       ROUND(SUM(is_repeat) / COUNT(*) * 100, 2)       AS repeat_rate_pct,
       ROUND(AVG(review_score), 2)                     AS avg_review_score
FROM first_orders
GROUP BY delivery_band
ORDER BY MIN(delivery_days);

-- QUERY 09 | Review score vs repeat purchase | Does satisfaction buy loyalty?
WITH first_orders AS (
    SELECT o.review_score, o.order_value, o.late_delivery, c.is_repeat
    FROM fact_orders o
    JOIN dim_customer c ON c.customer_id = o.customer_id
    WHERE o.is_first_order = 1 AND o.review_score IS NOT NULL
)
SELECT review_score,
       COUNT(*)                                   AS first_orders,
       SUM(is_repeat)                             AS became_repeat,
       ROUND(SUM(is_repeat) / COUNT(*) * 100, 2)  AS repeat_rate_pct,
       ROUND(AVG(order_value), 2)                 AS avg_order_value,
       ROUND(AVG(late_delivery) * 100, 2)         AS late_share_pct
FROM first_orders
GROUP BY review_score
ORDER BY review_score;

-- QUERY 10 | Instalments and basket size | Do instalment plans signal price sensitivity?
SELECT CASE WHEN payment_installments <=  1 THEN '1 (single payment)'
            WHEN payment_installments <=  3 THEN '2-3'
            WHEN payment_installments <=  6 THEN '4-6'
            WHEN payment_installments <= 12 THEN '7-12'
            ELSE '13+' END                                   AS installment_band,
       COUNT(*)                                              AS orders,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)      AS pct_of_orders,
       ROUND(AVG(order_value), 2)                            AS avg_order_value,
       ROUND(SUM(order_value), 2)                            AS revenue,
       ROUND(AVG(items), 2)                                  AS avg_items,
       ROUND(AVG(review_score), 2)                           AS avg_review_score
FROM fact_orders
WHERE payment_installments IS NOT NULL
GROUP BY installment_band
ORDER BY MIN(payment_installments);

-- QUERY 11 | Monthly new vs returning | Is growth acquisition or order value?
SELECT d.month_key                                            AS order_month,
       COUNT(o.order_id)                                       AS orders,
       ROUND(SUM(o.order_value), 2)                            AS revenue,
       ROUND(AVG(o.order_value), 2)                            AS aov,
       COUNT(DISTINCT o.customer_id)                           AS active_customers,
       COUNT(DISTINCT CASE WHEN o.is_first_order = 1 THEN o.customer_id END) AS new_customers,
       COUNT(DISTINCT CASE WHEN o.is_first_order = 0 THEN o.customer_id END) AS returning_customers,
       ROUND(COUNT(DISTINCT CASE WHEN o.is_first_order = 1 THEN o.customer_id END)
             / COUNT(DISTINCT o.customer_id) * 100, 2)         AS pct_new
FROM fact_orders o
JOIN dim_date d ON d.date_key = o.order_day
GROUP BY d.month_key
ORDER BY d.month_key;

-- QUERY 12 | Cohort retention | How fast do acquired customers disappear?
WITH cohort_orders AS (
    SELECT c.cohort_month,
           c.customer_id,
           TIMESTAMPDIFF(MONTH, STR_TO_DATE(CONCAT(c.cohort_month, '-01'), '%Y-%m-%d'),
                                o.order_day)                   AS months_since
    FROM dim_customer c
    JOIN fact_orders o ON o.customer_id = c.customer_id
), sized AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM cohort_orders WHERE months_since = 0 GROUP BY cohort_month
)
SELECT co.months_since,
       COUNT(DISTINCT co.cohort_month)                                AS cohorts_used,
       SUM(s.cohort_size) / COUNT(DISTINCT co.cohort_month)           AS avg_cohort_size,
       COUNT(DISTINCT co.customer_id)                                 AS customers_active,
       ROUND(COUNT(DISTINCT co.customer_id)
             / (SELECT SUM(cohort_size) FROM sized WHERE cohort_size >= 100) * 100, 4) AS pct_of_all_cohorts
FROM cohort_orders co
JOIN sized s ON s.cohort_month = co.cohort_month
WHERE s.cohort_size >= 100 AND co.months_since BETWEEN 0 AND 11
GROUP BY co.months_since
ORDER BY co.months_since;

-- QUERY 13 | Seller concentration | How much of the marketplace do a few sellers carry?
WITH seller_rev AS (
    SELECT s.seller_id, SUM(i.line_revenue) AS revenue
    FROM fact_order_items i
    JOIN dim_seller s ON s.seller_id = i.seller_id
    GROUP BY s.seller_id
), ranked AS (
    SELECT seller_id, revenue,
           ROW_NUMBER() OVER (ORDER BY revenue DESC)                     AS rn,
           SUM(revenue) OVER (ORDER BY revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_revenue,
           SUM(revenue) OVER ()                                          AS total_revenue,
           COUNT(*)    OVER ()                                           AS seller_count
    FROM seller_rev
)
SELECT seller_count                                           AS sellers,
       ROUND(MAX(CASE WHEN rn <= CEIL(seller_count * 0.01) THEN cum_revenue END)
             / MAX(total_revenue) * 100, 2)                   AS top_1pct_revenue_share,
       ROUND(MAX(CASE WHEN rn <= CEIL(seller_count * 0.10) THEN cum_revenue END)
             / MAX(total_revenue) * 100, 2)                   AS top_10pct_revenue_share,
       MIN(CASE WHEN cum_revenue >= total_revenue * 0.5 THEN rn END) AS sellers_for_half_revenue
FROM ranked
GROUP BY seller_count;

-- =========================== PART B - campaign dataset (separate company) ====

-- QUERY 14 | RFM value tiers | Who are the best customers and do they respond?
SELECT value_tier,
       COUNT(*)                                                   AS customers,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)           AS pct_of_customers,
       ROUND(SUM(total_spend), 2)                                 AS total_spend,
       ROUND(SUM(total_spend) / SUM(SUM(total_spend)) OVER () * 100, 2) AS pct_of_spend,
       ROUND(AVG(total_spend), 2)                                 AS avg_spend,
       ROUND(AVG(total_purchases), 2)                             AS avg_purchases,
       ROUND(AVG(recency), 2)                                     AS avg_recency,
       ROUND(AVG(income), 2)                                      AS avg_income,
       ROUND(AVG(deal_share) * 100, 2)                            AS avg_deal_share_pct,
       ROUND(AVG(response) * 100, 2)                              AS response_rate_pct,
       ROUND(AVG(response) / (SELECT AVG(response) FROM campaign_customers), 2) AS response_lift
FROM campaign_customers
GROUP BY value_tier
ORDER BY FIELD(value_tier, 'Best', 'Core', 'Occasional', 'Marginal');

-- QUERY 15 | Campaign performance by tier | Which campaign worked on whom?
SELECT value_tier,
       COUNT(*)                            AS customers,
       ROUND(AVG(accepted_cmp1) * 100, 2)  AS cmp1_pct,
       ROUND(AVG(accepted_cmp2) * 100, 2)  AS cmp2_pct,
       ROUND(AVG(accepted_cmp3) * 100, 2)  AS cmp3_pct,
       ROUND(AVG(accepted_cmp4) * 100, 2)  AS cmp4_pct,
       ROUND(AVG(accepted_cmp5) * 100, 2)  AS cmp5_pct,
       ROUND(AVG(response)      * 100, 2)  AS latest_campaign_pct
FROM campaign_customers
GROUP BY value_tier
ORDER BY FIELD(value_tier, 'Best', 'Core', 'Occasional', 'Marginal');

-- QUERY 16 | Discount dependence | Are deal-driven customers worth campaigning to?
SELECT discount_behaviour,
       COUNT(*)                                                   AS customers,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)           AS pct_of_customers,
       ROUND(SUM(total_spend) / SUM(SUM(total_spend)) OVER () * 100, 2) AS pct_of_spend,
       ROUND(AVG(deal_share) * 100, 2)                            AS avg_deal_share_pct,
       ROUND(AVG(total_spend), 2)                                 AS avg_spend,
       ROUND(AVG(total_purchases), 2)                             AS avg_purchases,
       ROUND(AVG(total_spend / NULLIF(total_purchases, 0)), 2)    AS avg_spend_per_purchase,
       ROUND(AVG(income), 2)                                      AS avg_income,
       ROUND(AVG(response) * 100, 2)                              AS response_rate_pct
FROM campaign_customers
GROUP BY discount_behaviour
ORDER BY pct_of_spend DESC;

-- QUERY 17 | Targeting matrix | The cell-by-cell campaign plan
SELECT value_tier,
       CASE WHEN campaigns_accepted > 0 THEN 'Responder' ELSE 'Non-responder' END AS responder,
       discount_behaviour,
       COUNT(*)                                                   AS customers,
       ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 2)           AS pct_of_customers,
       ROUND(SUM(total_spend) / SUM(SUM(total_spend)) OVER () * 100, 2) AS pct_of_spend,
       ROUND(AVG(total_spend), 2)                                 AS avg_spend,
       ROUND(AVG(income), 2)                                      AS avg_income,
       ROUND(AVG(response) * 100, 2)                              AS response_rate_pct
FROM campaign_customers
GROUP BY value_tier, responder, discount_behaviour
ORDER BY FIELD(value_tier, 'Best', 'Core', 'Occasional', 'Marginal'), responder, discount_behaviour;
