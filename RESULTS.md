# Results

*Author: Pranit Ajay Chaudhari*

Every table on this page is a direct render of a CSV in `outputs/tables/`, each of which is produced
by the Python pipeline and independently reproduced in MySQL and (for the headline figures) in
Excel. **69 of 69 cross-tool checks pass.**

The two parts are reported separately throughout. They are different companies and are never
combined — see [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

---

# Part A — Olist marketplace

## Headline KPIs

| Metric | Value |
|---|---|
| Orders analysed | 96470 |
| Customers | 93350 |
| Gross revenue (R$) | 15418394.83 |
| Items value (R$) | 13220248.93 |
| Freight (R$) | 2198145.9 |
| Average order value (R$) | 159.83 |
| Median order value (R$) | 105.28 |
| Repeat customers | 2801 |
| Repeat rate (%) | 3.0 |
| Revenue from first orders (%) | 97.03 |
| Average first-order value (R$) | 160.26 |
| CLV proxy per acquired customer (R$) | 165.17 |
| States covered | 27 |
| Cities covered | 4085 |
| Product categories | 74 |
| Sellers | 2970 |
| Average delivery days | 12.09 |
| Late deliveries (%) | 6.77 |
| Average review score | 4.14 |
| Orders paid in installments (%) | 51.47 |
| Revenue from top 20% of customers (%) | 53.53 |
| Analysis window | 2016-09-15 to 2018-08-29 |

## Is RFM segmentation applicable?

| Check | Value |
|---|---|
| Customers | 93,350.00 |
| Customers with exactly 1 order | 90,549.00 |
| Customers with 2+ orders | 2,801.00 |
| Share with exactly 1 order (%) | 97.00 |
| Maximum orders by one customer | 15.00 |
| Distinct frequency values | 9.00 |
| Share of customers in the modal frequency (%) | 97.00 |

**No.** Frequency is a single value for 97% of customers, so an RFM model would place almost
everyone in one bucket on that dimension.

## Order frequency distribution

| Orders | Customers | PctOfCustomers | Revenue | PctOfRevenue |
|---|---|---|---|---|
| 1 | 90,549 | 97.00 | 14,554,207.37 | 94.40 |
| 2 | 2,573 | 2.76 | 748,811.57 | 4.86 |
| 3 | 181 | 0.19 | 78,333.95 | 0.51 |
| 4 | 28 | 0.03 | 22,086.25 | 0.14 |
| 5 | 9 | 0.01 | 6,607.63 | 0.04 |
| 6 | 5 | 0.01 | 3,455.56 | 0.02 |
| 7 | 3 | 0.00 | 2,840.56 | 0.02 |
| 9 | 1 | 0.00 | 1,172.67 | 0.01 |
| 15 | 1 | 0.00 | 879.27 | 0.01 |

## First orders versus repeat orders

| OrderType | Orders | PctOfOrders | Revenue | PctOfRevenue | AOV |
|---|---|---|---|---|---|
| Repeat order | 3,120 | 3.23 | 458,218.16 | 2.97 | 146.86 |
| First order | 93,350 | 96.77 | 14,960,176.67 | 97.03 | 160.26 |

## Where a customer's value comes from

| Component | Value |
|---|---|
| Average first-order value (R$) | 160.26 |
| Probability of a second order (%) | 3.00 |
| Average additional orders, given a repeat | 1.11 |
| Average value of a repeat order (R$) | 146.86 |
| Retention contribution per acquired customer (R$) | 4.91 |
| Total revenue per acquired customer (R$) | 165.17 |
| Share of customer value earned on the first order (%) | 97.03 |

## Customer value tiers

| ValueTier | Customers | PctOfCustomers | Revenue | PctOfRevenue | AvgRevenue | AvgOrders | RepeatRate | AvgReview |
|---|---|---|---|---|---|---|---|---|
| High | 18,671 | 20.00 | 8,253,195.37 | 53.53 | 442.03 | 1.10 | 8.22 | 4.03 |
| Medium | 28,099 | 30.10 | 4,209,066.66 | 27.30 | 149.79 | 1.03 | 3.32 | 4.13 |
| Low | 46,580 | 49.90 | 2,956,132.80 | 19.17 | 63.46 | 1.01 | 0.72 | 4.19 |

## Does delivery performance predict a second order?

| LateBand | FirstOrders | BecameRepeat | AvgDeliveryDays | AvgOrderValue | RepeatRate |
|---|---|---|---|---|---|
| Late | 6,357 | 162 | 33.51 | 176.82 | 2.55 |
| On time or early | 86,993 | 2,639 | 10.54 | 159.05 | 3.03 |

### By delivery speed

| SpeedBand | FirstOrders | BecameRepeat | AvgReview | RepeatRate |
|---|---|---|---|---|
| 0-3 days | 8,316 | 228 | 4.45 | 2.74 |
| 4-7 days | 24,292 | 729 | 4.38 | 3.00 |
| 8-14 days | 35,197 | 1,083 | 4.28 | 3.08 |
| 15-21 days | 14,870 | 465 | 4.09 | 3.13 |
| 22+ days | 10,675 | 296 | 2.98 | 2.77 |

## Does review score predict a second order?

| ReviewScore | FirstOrders | BecameRepeat | AvgOrderValue | LateShare | RepeatRate |
|---|---|---|---|---|---|
| 1 | 9,418 | 270 | 194.73 | 36.61 | 2.87 |
| 2 | 2,900 | 80 | 169.50 | 19.14 | 2.76 |
| 3 | 7,754 | 228 | 150.96 | 8.90 | 2.94 |
| 4 | 18,418 | 517 | 155.32 | 3.46 | 2.81 |
| 5 | 54,860 | 1,706 | 156.83 | 1.87 | 3.11 |

## Significance of the customer-experience findings

| Comparison | GroupA | RepeatRateA_pct | GroupB | RepeatRateB_pct | DifferencePP | Z | P_value | StatisticallySignificant_5pct | CommerciallyMeaningful |
|---|---|---|---|---|---|---|---|---|---|
| On-time vs late first delivery | On time or early | 3.03 | Late | 2.55 | 0.49 | 2.19 | 0.03 | 1 | 0 |
| 5-star vs 1-star first review | 5-star | 3.11 | 1-star | 2.87 | 0.24 | 1.26 | 0.21 | 0 | 0 |

Both effects are small. One is statistically detectable and commercially negligible; the other is
neither. Reported as they are rather than as a retention story.

## Acquisition economics by state

| State | Customers | Orders | Revenue | PctOfRevenue | AOV | FreightShare | AvgDeliveryDays | LateShare | AvgReview | RepeatRate |
|---|---|---|---|---|---|---|---|---|---|---|
| SP | 39,138 | 40,490 | 5,768,852.33 | 37.42 | 142.48 | 12.17 | 8.30 | 4.49 | 4.23 | 3.11 |
| RJ | 11,913 | 12,349 | 2,055,119.40 | 13.33 | 166.42 | 14.39 | 14.85 | 12.11 | 3.95 | 3.27 |
| MG | 10,998 | 11,357 | 1,819,130.86 | 11.80 | 160.18 | 14.65 | 11.55 | 4.59 | 4.18 | 2.95 |
| RS | 5,166 | 5,344 | 861,300.27 | 5.59 | 161.17 | 15.39 | 14.82 | 6.08 | 4.18 | 3.06 |
| PR | 4,768 | 4,925 | 782,091.77 | 5.07 | 158.80 | 14.79 | 11.53 | 4.04 | 4.23 | 2.96 |
| SC | 3,444 | 3,543 | 594,312.16 | 3.85 | 167.74 | 14.80 | 14.47 | 8.21 | 4.12 | 2.67 |
| BA | 3,158 | 3,258 | 591,447.41 | 3.84 | 181.54 | 16.50 | 18.86 | 12.15 | 3.91 | 2.85 |
| DF | 2,018 | 2,082 | 346,223.65 | 2.25 | 166.29 | 14.34 | 12.51 | 5.62 | 4.13 | 2.97 |
| GO | 1,894 | 1,959 | 334,657.15 | 2.17 | 170.83 | 15.38 | 15.16 | 6.53 | 4.09 | 3.12 |
| ES | 1,927 | 1,994 | 317,524.68 | 2.06 | 159.24 | 15.43 | 15.33 | 10.73 | 4.05 | 2.91 |
| PE | 1,548 | 1,594 | 308,839.14 | 2.00 | 193.75 | 18.47 | 17.93 | 9.54 | 4.07 | 2.33 |
| CE | 1,257 | 1,278 | 266,348.96 | 1.73 | 208.41 | 17.51 | 20.82 | 13.77 | 3.94 | 1.59 |
| PA | 922 | 946 | 212,023.57 | 1.38 | 224.13 | 17.71 | 23.32 | 11.21 | 3.89 | 2.39 |
| MT | 855 | 886 | 181,218.56 | 1.18 | 204.54 | 16.01 | 17.61 | 6.09 | 4.13 | 3.39 |
| MA | 698 | 714 | 147,269.27 | 0.96 | 206.26 | 20.85 | 21.10 | 17.37 | 3.81 | 1.86 |
| PB | 504 | 519 | 138,240.69 | 0.90 | 266.36 | 18.32 | 19.94 | 10.40 | 4.06 | 2.38 |
| MS | 681 | 702 | 134,407.80 | 0.87 | 191.46 | 14.10 | 15.18 | 9.69 | 4.16 | 2.64 |
| PI | 464 | 476 | 105,178.19 | 0.68 | 220.96 | 19.45 | 18.99 | 13.87 | 3.98 | 2.16 |
| RN | 464 | 474 | 100,714.78 | 0.65 | 212.48 | 18.48 | 18.82 | 9.28 | 4.13 | 2.16 |
| AL | 387 | 397 | 94,172.49 | 0.61 | 237.21 | 16.26 | 24.04 | 21.41 | 3.83 | 2.58 |
| SE | 327 | 334 | 70,134.10 | 0.45 | 209.98 | 19.51 | 21.00 | 15.27 | 3.90 | 2.14 |
| TO | 267 | 274 | 60,007.37 | 0.39 | 219.01 | 19.34 | 17.23 | 9.85 | 4.16 | 2.62 |
| RO | 230 | 242 | 56,838.10 | 0.37 | 234.87 | 19.77 | 18.89 | 2.89 | 4.17 | 3.91 |
| AM | 140 | 145 | 27,585.47 | 0.18 | 190.24 | 19.68 | 25.99 | 2.76 | 4.23 | 2.14 |
| AC | 76 | 80 | 19,575.33 | 0.13 | 244.69 | 18.62 | 20.64 | 3.75 | 4.09 | 5.26 |
| AP | 66 | 67 | 16,141.81 | 0.10 | 240.92 | 17.14 | 26.73 | 2.99 | 4.22 | 1.52 |
| RR | 40 | 41 | 9,039.52 | 0.06 | 220.48 | 21.93 | 28.98 | 12.20 | 3.90 | 2.50 |

## Product categories (top 15 by revenue)

| Category | Lines | Revenue | PctOfRevenue | AvgPrice | Sellers | RepeatLineShare |
|---|---|---|---|---|---|---|
| Health Beauty | 9,465 | 1,412,089.53 | 9.16 | 130.28 | 479 | 2.97 |
| Watches Gifts | 5,857 | 1,264,016.98 | 8.20 | 199.06 | 95 | 3.14 |
| Bed Bath Table | 10,953 | 1,225,209.26 | 7.95 | 93.44 | 189 | 5.22 |
| Sports Leisure | 8,430 | 1,118,062.91 | 7.25 | 113.25 | 466 | 3.97 |
| Computers Accessories | 7,643 | 1,032,603.65 | 6.70 | 116.27 | 279 | 3.81 |
| Furniture Decor | 8,160 | 880,329.92 | 5.71 | 87.25 | 352 | 4.91 |
| Housewares | 6,795 | 758,392.25 | 4.92 | 90.60 | 452 | 3.34 |
| Cool Stuff | 3,718 | 691,680.89 | 4.49 | 164.12 | 259 | 1.80 |
| Auto | 4,139 | 669,319.92 | 4.34 | 139.85 | 371 | 2.37 |
| Garden Tools | 4,268 | 567,145.68 | 3.68 | 110.24 | 227 | 2.58 |
| Toys | 4,029 | 546,856.44 | 3.55 | 116.93 | 242 | 2.78 |
| Baby | 2,982 | 466,727.65 | 3.03 | 134.28 | 240 | 2.62 |
| Perfumery | 3,340 | 443,171.63 | 2.87 | 116.81 | 173 | 2.75 |
| Telephony | 4,430 | 379,202.62 | 2.46 | 69.95 | 142 | 2.51 |
| Office Furniture | 1,668 | 335,211.36 | 2.17 | 160.76 | 30 | 1.74 |

## Payment instalments and basket size

| InstBand | Orders | AvgOrderValue | MedianOrderValue | Revenue | AvgItems | AvgReview | PctOfOrders |
|---|---|---|---|---|---|---|---|
| 1 (single payment) | 46,813 | 120.21 | 79.24 | 5,627,168.42 | 1.13 | 4.18 | 48.53 |
| 2-3 | 22,157 | 135.40 | 111.82 | 3,000,156.53 | 1.12 | 4.13 | 22.97 |
| 4-6 | 15,736 | 181.82 | 128.20 | 2,861,085.60 | 1.15 | 4.11 | 16.31 |
| 7-12 | 11,584 | 332.85 | 205.70 | 3,855,678.85 | 1.23 | 4.06 | 12.01 |
| 13+ | 179 | 414.31 | 249.70 | 74,161.97 | 1.31 | 3.87 | 0.19 |

## Payment methods

| PaymentType | Orders | Revenue | AvgOrderValue | AvgInstallments | PctOfOrders |
|---|---|---|---|---|---|
| credit_card | 72,818 | 12,098,311.19 | 166.14 | 3.55 | 75.48 |
| boleto | 19,191 | 2,769,932.71 | 144.33 | 1.00 | 19.89 |
| voucher | 2,977 | 341,938.60 | 114.86 | 1.15 | 3.09 |
| debit_card | 1,483 | 208,068.87 | 140.30 | 1.00 | 1.54 |

## Monthly trend and the new-versus-returning split

| OrderMonth | Orders | Revenue | AOV | Customers | NewCustomers | ReturningCustomers | PctNew |
|---|---|---|---|---|---|---|---|
| 2016-09 | 1 | 143.46 | 143.46 | 1 | 1 | 0 | 100.00 |
| 2016-10 | 265 | 46,490.66 | 175.44 | 262 | 262 | 0 | 100.00 |
| 2016-12 | 1 | 19.62 | 19.62 | 1 | 1 | 0 | 100.00 |
| 2017-01 | 750 | 127,482.37 | 169.98 | 718 | 717 | 1 | 99.86 |
| 2017-02 | 1,653 | 271,239.32 | 164.09 | 1,630 | 1,628 | 2 | 99.88 |
| 2017-03 | 2,546 | 414,330.95 | 162.74 | 2,508 | 2,503 | 5 | 99.80 |
| 2017-04 | 2,303 | 390,812.40 | 169.70 | 2,274 | 2,256 | 18 | 99.21 |
| 2017-05 | 3,545 | 566,657.40 | 159.85 | 3,478 | 3,450 | 28 | 99.19 |
| 2017-06 | 3,135 | 490,050.37 | 156.32 | 3,076 | 3,037 | 39 | 98.73 |
| 2017-07 | 3,872 | 566,299.08 | 146.25 | 3,802 | 3,752 | 50 | 98.68 |
| 2017-08 | 4,193 | 645,832.36 | 154.03 | 4,114 | 4,057 | 57 | 98.61 |
| 2017-09 | 4,150 | 701,077.49 | 168.93 | 4,083 | 4,004 | 79 | 98.07 |
| 2017-10 | 4,478 | 751,117.01 | 167.73 | 4,417 | 4,328 | 89 | 97.99 |
| 2017-11 | 7,288 | 1,153,229.37 | 158.24 | 7,182 | 7,059 | 123 | 98.29 |
| 2017-12 | 5,513 | 843,078.29 | 152.93 | 5,450 | 5,338 | 112 | 97.94 |
| 2018-01 | 7,069 | 1,077,887.46 | 152.48 | 6,974 | 6,842 | 132 | 98.11 |
| 2018-02 | 6,555 | 966,168.41 | 147.39 | 6,400 | 6,288 | 112 | 98.25 |
| 2018-03 | 7,003 | 1,120,598.24 | 160.02 | 6,914 | 6,774 | 140 | 97.98 |
| 2018-04 | 6,798 | 1,132,878.93 | 166.65 | 6,744 | 6,582 | 162 | 97.60 |
| 2018-05 | 6,749 | 1,128,774.52 | 167.25 | 6,693 | 6,506 | 187 | 97.21 |
| 2018-06 | 6,096 | 1,011,448.96 | 165.92 | 6,058 | 5,875 | 183 | 96.98 |
| 2018-07 | 6,156 | 1,027,286.52 | 166.88 | 6,097 | 5,946 | 151 | 97.52 |
| 2018-08 | 6,351 | 985,491.64 | 155.17 | 6,310 | 6,144 | 166 | 97.37 |

## Cohort retention — customer-weighted

| MonthsSinceFirstOrder | CohortsUsed | CustomersAtRisk | CustomersActive | WeightedRetentionPct |
|---|---|---|---|---|
| 0 | 21 | 93,348 | 93,348 | 100.00 |
| 1 | 19 | 86,942 | 420 | 0.48 |
| 2 | 18 | 80,996 | 273 | 0.34 |
| 3 | 17 | 75,121 | 192 | 0.26 |
| 4 | 16 | 68,615 | 176 | 0.26 |
| 5 | 15 | 62,033 | 140 | 0.23 |
| 6 | 15 | 55,521 | 129 | 0.23 |
| 7 | 13 | 48,971 | 102 | 0.21 |
| 8 | 12 | 42,129 | 86 | 0.20 |
| 9 | 11 | 36,336 | 60 | 0.17 |
| 10 | 10 | 29,732 | 75 | 0.25 |
| 11 | 10 | 25,666 | 57 | 0.22 |

Cohorts below 100 customers are excluded. An unweighted mean would report 5.45% for month 1 because
one cohort contains a single customer who ordered again.

## Seller concentration

| Measure | Value |
|---|---|
| Sellers | 2,970.00 |
| Top 1% of sellers - share of revenue (%) | 25.48 |
| Top 10% of sellers - share of revenue (%) | 66.29 |
| Sellers needed for 50% of revenue | 133.00 |
| Median seller revenue | 1,038.63 |

---

# Part B — campaign response and discount behaviour

## Headline KPIs

| Metric | Value |
|---|---|
| Customers analysed | 2026 |
| Total spend (2 years) | 1230699.0 |
| Average spend per customer | 607.45 |
| Average purchases per customer | 14.89 |
| Average spend per purchase | 40.79 |
| Median recency (days) | 49.0 |
| Customers accepting at least one campaign | 425 |
| Share accepting at least one campaign (%) | 20.98 |
| Most recent campaign response rate (%) | 15.3 |
| Best single campaign response rate (%) | 7.65 |
| Worst single campaign response rate (%) | 1.28 |
| Deal-driven customers | 694 |
| Share of customers deal-driven (%) | 34.25 |
| Share of all purchases made on a deal (%) | 15.69 |
| Best tier share of customers (%) | 14.76 |
| Best tier share of spend (%) | 32.02 |
| Average income | 52027.21 |
| Customers who complained | 19 |
| Enrolment window | 2012-07-30 to 2014-06-29 |

## RFM bands

| Score | Recency_days | Frequency_purchases | Monetary_spend |
|---|---|---|---|
| 5 | 0-19 | 23+ | 1175+ |
| 4 | 20-39 | 18-22 | 637-1174 |
| 3 | 40-58 | 13-17 | 200-636 |
| 2 | 59-79 | 8-12 | 56-199 |
| 1 | 80+ | 0-7 | 0-55 |

Frozen quintile boundaries, reproduced identically in Python, MySQL and Excel. Excel rebuilds the
scoring independently with nested IFs and disagrees on **0 of 2,026 customers**.

## Value tiers

| ValueTier | Customers | PctOfCustomers | PctOfSpend | AvgSpend | AvgPurchases | AvgRecency | AvgIncome | AvgDealShare | ResponseRate | ResponseLift |
|---|---|---|---|---|---|---|---|---|---|---|
| Best | 299 | 14.76 | 32.02 | 1,317.97 | 23.81 | 21.52 | 72,159.12 | 9.68 | 33.78 | 2.21 |
| Core | 623 | 30.75 | 50.39 | 995.47 | 20.38 | 50.83 | 65,169.67 | 13.05 | 17.82 | 1.16 |
| Occasional | 587 | 28.97 | 14.93 | 313.02 | 11.79 | 46.13 | 44,316.93 | 21.80 | 13.12 | 0.86 |
| Marginal | 517 | 25.52 | 2.66 | 63.26 | 6.64 | 65.53 | 33,301.38 | 24.99 | 4.06 | 0.27 |

## Campaign-by-campaign performance

| Campaign | Accepted | ResponseRate | AvgSpend_Accepted | AvgSpend_Declined | AvgIncome_Accepted | AvgRFM_Accepted | PctWithChildren_Accepted | PctPartnered_Accepted |
|---|---|---|---|---|---|---|---|---|
| Campaign 1 | 132 | 6.52 | 1,492.42 | 545.78 | 78,791.85 | 11.98 | 22.73 | 65.91 |
| Campaign 2 | 26 | 1.28 | 1,323.62 | 598.14 | 71,451.58 | 11.50 | 34.62 | 57.69 |
| Campaign 3 | 151 | 7.45 | 720.66 | 598.34 | 50,797.87 | 9.34 | 70.20 | 61.59 |
| Campaign 4 | 155 | 7.65 | 1,103.63 | 566.35 | 67,973.10 | 10.99 | 60.00 | 63.23 |
| Campaign 5 | 145 | 7.16 | 1,614.70 | 529.81 | 82,487.78 | 11.94 | 15.17 | 66.90 |
| Most recent campaign | 310 | 15.30 | 979.14 | 540.31 | 60,131.45 | 10.85 | 49.35 | 47.42 |

## Campaign acceptance by value tier (%)

| ValueTier | Customers | AcceptedCmp1 | AcceptedCmp2 | AcceptedCmp3 | AcceptedCmp4 | AcceptedCmp5 | Response |
|---|---|---|---|---|---|---|---|
| Best | 299 | 19.06 | 3.01 | 10.03 | 13.71 | 21.07 | 33.78 |
| Core | 623 | 9.79 | 2.09 | 7.54 | 13.00 | 11.40 | 17.82 |
| Occasional | 587 | 2.39 | 0.51 | 6.81 | 4.94 | 1.87 | 13.12 |
| Marginal | 517 | 0.00 | 0.19 | 6.58 | 0.77 | 0.00 | 4.06 |

## Discount dependence

| DiscountBehaviour | Customers | PctOfCustomers | PctOfSpend | AvgDealShare | AvgSpend | AvgSpendPerPurchase | AvgPurchases | AvgIncome | ResponseRate |
|---|---|---|---|---|---|---|---|---|---|
| Deal-driven | 694 | 34.25 | 10.29 | 30.72 | 182.48 | 12.22 | 10.82 | 36,310.37 | 13.26 |
| Full-price | 1,332 | 65.75 | 89.71 | 11.54 | 828.87 | 43.45 | 17.01 | 60,216.02 | 16.37 |

## The campaign-targeting matrix

| ValueTier | Responder | DiscountBehaviour | Customers | PctOfCustomers | PctOfSpend | AvgSpend | ResponseRate | RecommendedAction |
|---|---|---|---|---|---|---|---|---|
| Best | Non-responder | Deal-driven | 13 | 0.64 | 1.04 | 988.54 | 30.77 | High value, campaign-immune - serve well, do not spend campaign budget |
| Best | Non-responder | Full-price | 162 | 8.00 | 15.74 | 1,195.43 | 17.90 | High value, campaign-immune - serve well, do not spend campaign budget |
| Best | Responder | Deal-driven | 6 | 0.30 | 0.41 | 833.83 | 66.67 | Target, but with non-price offers - bundles and loyalty, not discounts |
| Best | Responder | Full-price | 118 | 5.82 | 14.83 | 1,547.12 | 54.24 | Priority target - full-margin campaigns, early access, premium range |
| Core | Non-responder | Deal-driven | 80 | 3.95 | 3.45 | 531.26 | 20.00 | High value, campaign-immune - serve well, do not spend campaign budget |
| Core | Non-responder | Full-price | 366 | 18.07 | 28.71 | 965.51 | 7.65 | High value, campaign-immune - serve well, do not spend campaign budget |
| Core | Responder | Deal-driven | 16 | 0.79 | 0.82 | 634.56 | 50.00 | Target, but with non-price offers - bundles and loyalty, not discounts |
| Core | Responder | Full-price | 161 | 7.95 | 17.40 | 1,330.11 | 36.65 | Priority target - full-margin campaigns, early access, premium range |
| Occasional | Non-responder | Deal-driven | 245 | 12.09 | 2.79 | 140.35 | 12.65 | Low-cost nurture only |
| Occasional | Non-responder | Full-price | 256 | 12.64 | 8.39 | 403.14 | 6.25 | Low-cost nurture only |
| Occasional | Responder | Deal-driven | 26 | 1.28 | 0.39 | 183.04 | 50.00 | Develop - test offers to raise basket size and frequency |
| Occasional | Responder | Full-price | 60 | 2.96 | 3.36 | 689.93 | 28.33 | Develop - test offers to raise basket size and frequency |
| Marginal | Non-responder | Deal-driven | 285 | 14.07 | 1.26 | 54.26 | 3.16 | Suppress - discount-dependent and low value, campaigns erode margin |
| Marginal | Non-responder | Full-price | 194 | 9.58 | 1.16 | 73.64 | 2.06 | Suppress - minimal value, no campaign response |
| Marginal | Responder | Deal-driven | 23 | 1.14 | 0.12 | 66.43 | 30.43 | Suppress - discount-dependent and low value, campaigns erode margin |
| Marginal | Responder | Full-price | 15 | 0.74 | 0.12 | 95.00 | 6.67 | Suppress - minimal value, no campaign response |

## Channel mix by tier (% of purchases)

| ValueTier | WebPct | CatalogPct | StorePct | DealsPct | WebVisits |
|---|---|---|---|---|---|
| Best | 27.26 | 24.20 | 38.23 | 10.31 | 4.10 |
| Core | 27.72 | 20.74 | 38.49 | 13.06 | 4.49 |
| Occasional | 28.89 | 12.32 | 37.82 | 20.97 | 5.87 |
| Marginal | 24.67 | 5.77 | 43.64 | 25.92 | 6.42 |

## Demographics versus spend and response

| Dimension | Group | Customers | AvgSpend | ResponseRate | AvgDealShare | AvgRFM | ResponseLift |
|---|---|---|---|---|---|---|---|
| Income | 25-45k | 598 | 136.24 | 11.71 | 25.14 | 6.66 | 0.77 |
| Income | 45-65k | 594 | 574.58 | 11.45 | 18.32 | 9.57 | 0.75 |
| Income | 65-85k | 523 | 1,248.07 | 20.08 | 8.04 | 11.55 | 1.31 |
| Income | 85k+ | 91 | 1,527.65 | 46.15 | 4.97 | 11.66 | 3.02 |
| Income | Under 25k | 220 | 73.50 | 11.36 | 27.86 | 5.95 | 0.74 |
| Age | 35-44 | 690 | 539.07 | 14.64 | 19.71 | 8.65 | 0.96 |
| Age | 45-54 | 437 | 634.87 | 12.59 | 18.34 | 9.18 | 0.82 |
| Age | 55-64 | 402 | 693.25 | 15.17 | 16.65 | 9.46 | 0.99 |
| Age | 65+ | 67 | 977.66 | 17.91 | 9.84 | 10.48 | 1.17 |
| Age | Under 35 | 430 | 551.42 | 18.84 | 18.01 | 8.35 | 1.23 |
| Education | 2n Cycle | 183 | 500.51 | 12.02 | 19.30 | 8.58 | 0.79 |
| Education | Basic | 49 | 83.92 | 4.08 | 25.26 | 6.00 | 0.27 |
| Education | Graduation | 1,017 | 623.37 | 13.86 | 17.93 | 8.98 | 0.91 |
| Education | Master | 335 | 616.58 | 15.82 | 18.00 | 8.99 | 1.03 |
| Education | PhD | 442 | 666.23 | 20.81 | 17.36 | 9.22 | 1.36 |
| Marital status | Divorced | 215 | 608.27 | 20.00 | 18.78 | 8.99 | 1.31 |
| Marital status | Married | 788 | 594.61 | 11.68 | 18.30 | 8.95 | 0.76 |
| Marital status | Single | 441 | 608.76 | 23.13 | 17.91 | 8.82 | 1.51 |
| Marital status | Together | 512 | 606.22 | 10.74 | 18.07 | 8.83 | 0.70 |
| Marital status | Widow | 70 | 750.29 | 25.71 | 15.79 | 9.71 | 1.68 |
| Has children | False | 569 | 1,118.47 | 27.59 | 7.97 | 10.60 | 1.80 |
| Has children | True | 1,457 | 407.88 | 10.50 | 22.07 | 8.27 | 0.69 |

## Category spend

| Category | TotalSpend | AvgSpend | CustomersBuying | PctOfSpend | PctBuying |
|---|---|---|---|---|---|
| Wines | 618,596 | 305.33 | 2,014 | 50.26 | 99.41 |
| Meat | 339,913 | 167.78 | 2,025 | 27.62 | 99.95 |
| Gold | 88,354 | 43.61 | 1,969 | 7.18 | 97.19 |
| Fish | 75,627 | 37.33 | 1,672 | 6.15 | 82.53 |
| Sweet | 55,069 | 27.18 | 1,648 | 4.47 | 81.34 |
| Fruits | 53,140 | 26.23 | 1,664 | 4.32 | 82.13 |

---

*Figures reproduce in Python, MySQL and Excel. Verification: [`docs/VERIFICATION.md`](docs/VERIFICATION.md).
Limitations: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).*
