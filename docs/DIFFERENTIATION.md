# How Project 3 differs from Projects 1 and 2

*Author: Pranit Ajay Chaudhari*

This page exists because **Project 1 is also a customer-segmentation project**. Rather than hope a
reader does not notice, here is the comparison in full, written after reading Project 1's actual
files rather than from memory.

---

## Against Project 1 — *Customer Segmentation & Marketing Analytics*

Project 1 analyses the UCI **Online Retail II** dataset: a UK online gift-ware wholesaler,
1,067,371 raw transaction lines → 770,612 clean lines, 5,839 customers, 36,411 orders, £16.53M,
segmented with RFM into 11 segments across 4 tiers, in Python, MySQL and Excel with an interactive
web dashboard.

### The datasets have opposite shapes, and that drives everything

| | Project 1 | Project 3, Part A |
|---|---|---|
| Business | UK gift-ware wholesaler, single seller | Brazilian marketplace, 2,970 sellers |
| Customers | 5,839 | 93,350 |
| **Repeat rate** | **72.4%** | **3.0%** |
| Median orders per customer | 3 | 1 |
| Source shape | one flat transaction table | 8 related tables |
| Revenue concentration | top 10% of customers = 63.2% | top 20% of customers = 53.5% |

Project 1 describes a business that **runs on returning customers** — 87% of its monthly actives
were returning by the end of the period. Project 3 describes one where **98.1% of monthly actives
are first-time buyers**. They are mirror images.

### The analytical conclusion is the opposite

| | Project 1 | Project 3 |
|---|---|---|
| Central question | *Which of our loyal customers matter, and what do we send them?* | *We have no loyal customers — should we run loyalty marketing at all?* |
| Role of RFM | the spine of the project; 11 segments built on it | **tested and rejected for Part A**, then applied properly in Part B where frequency varies |
| Headline recommendation | retention, win-back and cross-sell by segment | **do not fund retention**; spend on acquisition, logistics and seller supply |
| What "at risk" means | 729 customers holding £1.39M of historical spend, worth winning back | meaningless — there is no base to be at risk of losing |

**Running the Project 1 method on the Project 3 data would have produced a confident, wrong
answer**: an 11-segment RFM grid where 97% of customers fall into one frequency band, dressed up as
insight. Demonstrating that a standard method does not fit, and saying so, is the point of Part A.

### Analyses in Project 3 that do not exist in Project 1

Project 1's own README names its limits: *"The dataset does not contain margins, demographics or
campaign-response history, so profitability and campaign response cannot be directly measured."*
Project 3 answers several of those questions on data that contains them:

| Analysis | Project 1 | Project 3 |
|---|---|---|
| Delivery performance → repeat purchase | no delivery data | yes, with a significance test |
| Review score → repeat purchase | no reviews | yes, 100,000 reviews |
| Payment method and instalments | not in the data | yes, 51.5% of orders in instalments |
| Seller / marketplace concentration | single seller | yes, 2,970 sellers |
| Sub-national geography | country-level, 83.6% one country | 27 states, 4,085 cities, with freight economics |
| **Campaign response** | explicitly impossible | **6 campaigns, 2,026 customers** |
| **Discount dependence** | discount codes were removed in cleaning | **deal share per customer** |
| **Demographics** | explicitly impossible | income, age, education, marital status, children |
| First-order-value framework | not needed | the core of Part A |
| Statistical significance testing | not used | two-proportion z-tests on the CX findings |

### Query-by-query overlap, measured rather than asserted

Comparing the two projects' SQL business questions directly:

| Project 1 query | Does Project 3 have an equivalent? |
|---|---|
| Headline KPIs | Yes — but of a different business |
| Monthly revenue trend / New vs returning | Yes — and the answer inverts: 98.1% new here, 13% there |
| Purchase frequency distribution | Yes — and it is the finding that ends the RFM approach |
| Cohort retention | Yes — 0.48% month-1 here against a healthy curve there |
| Revenue concentration · Top 10 customers · Segment summary · At-risk high-value customers · Top products per segment · **Products bought together** · Order timing · Champions vs Lost | **No equivalent.** These assume a loyal, repeat-purchasing base that does not exist in Part A |

**Twelve of Project 3's seventeen queries have no Project 1 counterpart at all:** customer value
decomposition, state acquisition economics, category entry vs return, delivery speed vs repeat,
review score vs repeat, instalments and basket size, seller concentration, RFM value tiers (Part B),
campaign performance by tier, discount dependence, and the targeting matrix.

Of Project 3's 28 result tables, these have no Project 1 analogue: `partA_rfm_viability`,
`partA_clv_proxy`, `partA_first_vs_repeat_revenue`, `partA_delivery_vs_repeat`,
`partA_delivery_speed_bands`, `partA_review_vs_repeat`, `partA_cx_significance`,
`partA_installments`, `partA_payment_types`, `partA_seller_concentration`, `partA_state_summary`,
and every `partB_*` table.

### Deliberate differences in form

- **No interactive web dashboard.** Project 1 has one; repeating it would make the two projects look
  like the same template. Project 3's outputs are charts, an Excel workbook and the SQL layer.
- **A different segmentation shape.** Project 1 uses the classic 11-segment recency × frequency
  grid. Project 3 uses four value tiers crossed with **responsiveness** and **discount dependence**,
  because the deliverable is a campaign-targeting matrix rather than a customer map.
- **A star schema.** Project 1's SQL runs on 3 tables; Project 3's runs on a 7-table star schema
  with foreign keys, a generated date dimension and multi-hop joins.

---

## Against Project 2 — *Fast-Food Product & Nutrition Analytics*

Project 2 analyses 713 menu items from McDonald's, Burger King and KFC: nutrition attributes by
product and category, in Python, MySQL and Excel.

The two share only the toolchain, which is the point of a portfolio.

| | Project 2 | Project 3 |
|---|---|---|
| Unit of analysis | a **product** | a **customer** |
| Does it contain customers? | no | yes — 93,350 marketplace customers + 2,026 campaign customers, kept separate |
| Does it contain transactions? | no | yes, 96,470 orders |
| Does it contain money? | no — nutrition only, and no prices were ever collected | yes, R$ 15.42M plus R$ 1.23M |
| Time dimension | none | 24 months, with cohorts and monthly trend |
| Core methods | menu composition, nutrient ratios per 100 kcal | segmentation, cohort retention, response rates, significance testing |
| Business question | how is each brand's menu positioned? | where should the marketing budget go? |

There is no overlap in data, unit of analysis, methods or conclusions.

---

## Summary

| | Project 1 | Project 2 | Project 3 |
|---|---|---|---|
| Subject | UK wholesaler's customers | fast-food menus | marketplace customers + campaign responders |
| Unit | customer | product | customer |
| Signature method | RFM segmentation | nutrition ratios | **testing whether RFM applies**, then campaign targeting |
| Signature finding | 18% of customers = 60% of revenue | McDonald's carries 184 products vs 113–123 | **97% never return; retention is worth R$ 4.91 a customer** |
| Tools | Python, SQL, Excel, dashboard | Python, SQL, Excel | Python, SQL, Excel |
