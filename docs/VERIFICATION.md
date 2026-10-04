# Verification — do the three tools agree?

*Author: Pranit Ajay Chaudhari*

The project's credibility rests on one claim: Python, MySQL and Excel compute the **same** figures
from the same cleaned data. This page records the checks that were actually run, and the defects
they caught.

Run it yourself: `python python/08_verify.py` — it exits non-zero if any figure disagrees.

## Result

**69 of 69 checks pass.**

| Group | Checks | Result |
|---|---|---|
| Part A headline KPIs, Python vs MySQL | 8 | all identical |
| First vs repeat revenue split | 6 | all identical |
| Customer value decomposition | 4 | all identical |
| Value tiers | 6 | all identical |
| **All 27 states × 5 metrics** | 1 (135 comparisons) | all identical |
| Delivery speed bands | 5 | all identical |
| Instalment bands | 5 | all identical |
| Part B value tiers | 12 | all identical |
| Part B discount behaviour | 6 | all identical |
| Python vs Excel cached values | 15 | all identical |
| **Excel's independent RFM rebuild** | 1 (2,026 customers) | **0 disagreements** |

## The import self-check

`02_import_data.sql` ends with a query whose numbers must match the Python output exactly before
any result below it can be trusted:

| | |
|---|---|
| orders | 96,470 |
| customers | 93,350 |
| order lines | 110,189 |
| products | 32,214 |
| sellers | 2,970 |
| campaign customers | 2,026 |
| gross revenue | 15,418,394.83 |

## Excel rebuilds the RFM scoring independently

`PartB_RFM_Check` does not read Python's scores and reformat them. It **recomputes** R, F and M from
raw recency, purchase count and spend, using nested `IF`s with the same frozen bands, and compares
the result to Python's scores for every one of the 2,026 customers. Three whole-column `SUMPRODUCT`
tests cover the full population; a 100-row worked sample is shown so the logic is readable.

**Disagreements: 0.**

## Two real defects this process caught

Both were fixed **in the code**, not reconciled by editing the documentation.

### 1. SQL double-counted repeat customers in the state table

Query 06 joins `dim_customer` to `fact_orders`, so a customer with 4 orders appears on 4 rows.
`AVG(c.is_repeat)` over that join weights each repeat customer by their order count, roughly
**doubling** every state's repeat rate — SP read 6.35% against Python's 3.11%.

Fixed by measuring over distinct customers:
```sql
ROUND(COUNT(DISTINCT CASE WHEN c.is_repeat = 1 THEN c.customer_id END)
      / COUNT(DISTINCT c.customer_id) * 100, 2) AS repeat_rate_pct
```

### 2. The state table mixed two grains

Python grouped **orders** by the state recorded on the order, but grouped **customers** by the state
recorded on the customer. For the handful of customers who ordered from more than one state the two
disagree, which is why per-state order counts differed from SQL by 1–4 orders. SQL could never
reproduce the Python version, because `fact_orders` carries no state of its own.

Fixed by adopting one grain: a customer belongs to one state (their first order's), and all of their
orders are attributed to it.

## Earlier defects, caught before the final pass

- **Cohort retention was 10× too high.** The unweighted mean of cohort percentages reported 5.45%
  month-1 retention; the December 2016 cohort contains **one** customer who ordered again, scoring
  100%. The published curve is customer-weighted and excludes cohorts under 100 customers:
  true month-1 retention is **0.48%**.
- **A chart label was clipped.** The repeat-order segment of chart 02 is too narrow to hold its own
  label, which was being cut off at the plot edge; narrow segments now label outside the bar.
- **Business_Insights referenced the wrong cells.** Two statements pointed at `KPIs!B8` and
  `KPIs!B12` after the KPI list had been edited, so a claim about repeat rate was showing average
  order value. The sheet now resolves KPI rows by label, so the references cannot drift again.
- **Two different KPIs were both labelled "Customers"** (93,350 for Part A, 2,026 for Part B). Now
  labelled "Customers (Part A)" and "Customers (Part B)".

## Rounding

MySQL's `ROUND()` rounds a half away from zero while NumPy rounds a half to even, so an exact 26.25
becomes 26.3 in one and 26.2 in the other. Every published figure passes through a
`Decimal(ROUND_HALF_UP)` helper, so the three tools agree exactly rather than nearly.

## Determinism

Running the pipeline twice produces **byte-identical** cleaned data and output tables.
