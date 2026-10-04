# Methodology

*Author: Pranit Ajay Chaudhari*

## 1. Why two datasets, and the rule that governs them

No single public dataset obtainable for this project covers the full question. Olist brings scale,
geography and a relational structure but carries **no campaigns and no discounts**. The marketing
dataset brings campaigns, discounts and demographics but is **2,026 customer-level rows with no
geography and no transaction dates**.

**The rule: the two are never joined, and never combined in a single figure.** They describe
different companies, in different countries, years apart, and share no key of any kind. Concretely:

- the SQL schema has **no foreign key** between `campaign_customers` and any Part A table;
- **no query** in `03_business_queries.sql` references both;
- **no Excel formula** spans a Part A and a Part B range;
- **no chart** plots them on the same axes;
- every table, sheet and figure is labelled Part A or Part B.

Where the two appear together it is as a **comparison of two business situations** — a marketplace
that cannot run retention marketing beside a retailer that can — which is an argument, not a merge.

## 2. Part A — cleaning and modelling decisions

### The customer key
Olist ships two: `customer_id` is unique per **order** (99,441 values) and `customer_unique_id`
identifies the **person** (96,096 values). Joining on `customer_id` makes every customer look like a
one-time buyer by construction and would report a 0% repeat rate. Everything customer-level in this
project keys on `customer_unique_id`.

### Order status
Analysis uses **delivered orders only** (96,478 of 99,441). Cancelled and unavailable orders (1,234)
are set aside because their revenue is not realised. In-flight statuses — shipped, invoiced,
processing, created, approved — are excluded because their delivery outcome is unknown, and delivery
outcome is one of the variables under test. A further 8 delivered orders have no delivery timestamp
and are dropped, leaving **96,470**.

### Revenue
Order value is built from the order lines as `price + freight_value`, summed per order. Freight is
included because it is money the customer pays. Items value and freight are also kept separately so
freight burden can be analysed on its own.

### Payments and reviews
`payment_type` can repeat within an order (part card, part voucher), so the **dominant** type by
value is taken and the **maximum** instalment count. 537 orders carry more than one review row;
these are collapsed to the most recent.

### Geography grain
A customer belongs to **one state** — the state on their first order — and all of their orders are
attributed to it. This single grain is what lets the Python and SQL state tables reconcile; an
earlier version grouped orders by the order's own state while grouping customers by the customer's
state, and the two disagreed for customers who ordered from more than one state.

### The CLV figure is a decomposition, not a forecast
`partA_clv_proxy.csv` multiplies back to observed revenue per customer **by construction**. It is
not a predictive model and is not presented as one. Its value is showing *where* a customer's worth
comes from: R$ 160.26 of R$ 165.17 arrives on the first order.

### Cohort retention is customer-weighted
An unweighted mean of cohort percentages is dominated by tiny cohorts — the December 2016 cohort
holds **one** customer, who ordered again, giving it 100% month-1 retention and lifting an
unweighted average from 0.48% to 5.45%. The published curve weights by customers and excludes
cohorts below 100 customers; both choices are stated on the chart and in the code.

## 3. Part B — cleaning and modelling decisions

182 records are identical to another record across **all 28 non-ID fields** — matching on income to
the rupee, six spend categories, every purchase count and all five campaign outcomes. These are
duplicated records, not coincidences, and keeping them would inflate every response rate; removing
them moves "accepted at least one campaign" from 27.2% to a true **20.98%**.

Also removed: 24 records with missing income (dropped rather than imputed, because income drives the
value segmentation), one income of 666,666 against a next-highest of 162,397, three birth years
implying ages over 100, and four records whose marital status reads `Absurd` or `YOLO`. `Z_CostContact`
and `Z_Revenue` are constant for every row and carry no information, so they are dropped.
**2,026 of 2,240 records (90.4%) are retained**, and every step is logged in
`data/cleaned/partB_cleaning_log.csv`.

### RFM bands
Frequency genuinely varies here (0–32 purchases, median 12, 0.2% with a single purchase), so RFM
applies. The bands are **this dataset's own quintile boundaries, then frozen as fixed integers** so
the identical logic reproduces in MySQL and in Excel:

| Score | Recency (days) | Frequency (purchases) | Monetary (spend) |
|---|---|---|---|
| 5 | 0–19 | 23+ | 1175+ |
| 4 | 20–39 | 18–22 | 637–1174 |
| 3 | 40–58 | 13–17 | 200–636 |
| 2 | 59–79 | 8–12 | 56–199 |
| 1 | 80+ | 0–7 | 0–55 |

Tiers come from the summed score: **Best** 13–15, **Core** 10–12, **Occasional** 7–9, **Marginal** 3–6.

### Deal dependence
`NumDealsPurchases` counts discounted purchases; the three channel counts are full-price purchases.
Deal share is the discounted proportion of all purchases. **Deal-driven** means a deal share at or
above 0.25 — the upper quartile of the distribution.

## 4. Rounding

MySQL's `ROUND()` rounds a half away from zero; NumPy rounds a half to even, so an exact 26.25
becomes 26.3 in SQL and 26.2 in pandas. Every published figure passes through a
`Decimal(ROUND_HALF_UP)` helper so the Python, SQL and Excel numbers are **identical rather than
nearly so**.

## 5. Statistical testing

Where a difference drives a recommendation, it is tested rather than eyeballed. The delivery and
review findings use a **two-proportion z-test**, reported with the difference in percentage points,
the z statistic and a two-sided p-value, and judged on **both** statistical significance and
commercial size. The on-time/late delivery difference is statistically detectable (p = 0.0286) and
commercially negligible (0.49 pp on a 3% base); the review-score difference is neither
(p = 0.2071). Reporting the second as a finding would have been wrong.

## 6. Reproducibility

`run_all.sh` rebuilds everything from the prepared raw files. The pipeline is deterministic —
running it twice produces byte-identical cleaned data and output tables. It then uses
`python/09_recalc_excel.py` with LibreOffice/soffice to populate Excel formula caches; the script
fails clearly if a recalculation engine is unavailable. `python/08_verify.py` then checks the
Python, SQL and Excel figures against each other and exits non-zero if any disagree.
