# Data cleaning

*Author: Pranit Ajay Chaudhari*

Both logs below are **generated from the pipeline itself** (`data/cleaned/partA_cleaning_log.csv`
and `partB_cleaning_log.csv`), so they cannot drift from what the code actually did.

---

## Part A — Olist marketplace

| # | Step | Rows after | Note |
|---|---|---|---|
| 1 | Raw orders loaded | 99,441 |  |
| 2 | Raw customer rows loaded | 99,441 | 99,441 customer_id vs 96,096 customer_unique_id |
| 3 | Raw order items loaded | 112,650 |  |
| 4 | Raw payment rows loaded | 103,886 |  |
| 5 | Raw reviews loaded (parsed, not line-counted) | 100,000 | as published the file has 105,764 lines for these 100,000 records |
| 6 | Raw products / categories / sellers loaded | 32,951 | 71 category translations, 3,095 sellers |
| 7 | Orders keyed to customer_unique_id | 99,441 | 96,096 distinct customers |
| 8 | Cancelled / unavailable orders set aside | 1,234 | kept out of revenue analysis |
| 9 | Delivered orders kept | 96,478 | 2,963 dropped (cancelled, unavailable or still in flight) |
| 10 | Order items joined to product category | 112,650 | 1,603 lines with no category -> 'Unknown' |
| 11 | Order items for delivered orders | 110,197 |  |
| 12 | Order-level revenue built from order lines | 96,478 | R$ 15,419,774 total |
| 13 | Payments aggregated to one row per order | 96,477 | 2,182 orders used more than one method |
| 14 | Reviews reduced to one per order | 96,478 | 537 duplicate order reviews collapsed |
| 15 | Orders joined to revenue (inner) | 96,478 | 0 delivered orders had no order lines |
| 16 | Orders with a usable delivery date | 96,470 | 8 dropped (no delivery timestamp) |
| 17 | Order sequence and first/repeat flags built | 96,470 | 93,350 first orders, 3,120 repeat orders |
| 18 | Customer table built | 93,350 | 2,801 repeat (3.0%), snapshot 2018-08-29 |

### The decisions worth explaining

**The customer key.** Olist ships `customer_id` (one per order, 99,441 values) and
`customer_unique_id` (one per person, 96,096 values). Using the first would have reported a repeat
rate of exactly zero and the entire project would have been built on it. Everything customer-level
keys on `customer_unique_id`.

**Reviews are parsed, not line-counted.** As Olist publishes it,
`olist_order_reviews_dataset.csv` has 105,764 lines but **100,000 records**, because review comments
contain embedded newlines — a `wc -l` would overstate reviews by 5.8%. The copy committed here has
the comment columns removed for privacy reasons (see `data/raw/README.md`), so it no longer has
that property; parsing rather than line-counting is correct either way.

**Delivered orders only.** Cancelled and unavailable orders are set aside; in-flight statuses are
excluded because their delivery outcome is unknown, and delivery outcome is a variable under test.

**1,603 order lines have no product category** and are labelled `Unknown` rather than dropped, so
revenue totals stay complete.

---

## Part B — campaign dataset

| # | Step | Rows after | Note |
|---|---|---|---|
| 1 | Raw records loaded (tab-separated) | 2,240 | 29 columns |
| 2 | Duplicate customer records removed | 2,058 | 182 rows identical across all 28 non-ID fields |
| 3 | Zero-variance columns dropped | 2,058 | Z_CostContact (always 3), Z_Revenue (always 11) |
| 4 | Implausible birth years removed | 2,055 | 3 records with implied age over 100 ([1893, 1899, 1900]) |
| 5 | Records with missing income removed | 2,031 | 24 dropped rather than imputed - income drives the value segmentation |
| 6 | Income outlier removed | 2,030 | 1 record at 666,666 vs next highest 162,397 |
| 7 | Non-sensical marital statuses removed | 2,026 | 4 records labelled 'Absurd' or 'YOLO' |
| 8 | Marital status harmonised | 2,026 | 'Alone' merged into 'Single'; Partnered flag added |
| 9 | Derived measures built | 2,026 | TotalSpend, TotalPurchases, DealShare, Age, Tenure, CampaignsAccepted (4 customers with 0 purchases) |
| 10 | Income and age bands assigned | 2,026 | fixed, documented bands - reproducible in SQL and Excel |

### The decisions worth explaining

**182 duplicate records (8.1% of the file).** Each is identical to another record across all 28
non-ID fields — same income to the rupee, same six category spends, same purchase counts, same five
campaign outcomes. Removing them changes "accepted at least one campaign" from 27.2% to the true
**20.98%**. Leaving them in would have inflated every response rate in Part B.

**Income is dropped, not imputed**, for the 24 records missing it. Income turns out to be the
strongest single predictor of campaign response in this dataset, so inventing it would have
contaminated the headline finding.

**One income of 666,666** against a next-highest of 162,397 — a data-entry artefact, removed so it
cannot distort income banding or any mean.

**Four records with marital status `Absurd` or `YOLO`** are removed; `Alone` (3 records) is merged
into `Single`.

**`Z_CostContact` and `Z_Revenue`** are constant for every row (always 3 and 11), so they carry no
information and are dropped.

**90.4% of records retained.** Every removal is counted above.
