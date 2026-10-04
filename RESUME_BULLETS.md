# Résumé bullets

*Author: Pranit Ajay Chaudhari*

Every number below comes from `outputs/tables/` and reproduces in Python, MySQL and Excel. Nothing
here is rounded in my favour or stated more strongly than the data supports.

---

## The project line

**E-Commerce Growth Analytics — Acquisition Economics & Campaign Response** · Python, MySQL, Excel

---

## Three bullets (recommended set)

- Analysed **96,470 marketplace orders (93,350 customers, R$ 15.4M, 27 Brazilian states)** across a
  **7-table MySQL star schema**, and established that **96.97% of customers never place a second
  order** — demonstrating that RFM segmentation was structurally unsuitable before building a
  first-order-value framework in its place, which showed **97% of a customer's lifetime value
  arrives on their first order**.
- Tested the assumption that customer experience drives loyalty using **two-proportion z-tests**,
  finding late delivery cost only **0.49 percentage points of a 3% repeat rate (p = 0.029)** and
  review score had **no significant effect (p = 0.207)** — redirecting the recommendation from
  retention spend toward **acquisition in the three south-eastern states that produce 62% of revenue
  at the lowest freight cost**.
- Built **RFM segmentation and campaign-response analysis on 2,026 customers across 6 campaigns**,
  identifying a **top tier of 14.8% of customers generating 32% of spend at 2.21× the base response
  rate** and a **deal-dependent third of the base contributing only 10% of spend at 3.6× lower
  basket value**, and converted both into a segment-by-segment targeting and suppression plan.

---

## Shorter two-bullet version

- Analysed **96,470 e-commerce orders and 93,350 customers in Python and MySQL (7-table star
  schema)**, proving **96.97% never reorder** and that **97% of customer value lands on the first
  order** — replacing a planned RFM segmentation with a first-order-value model and redirecting
  budget from retention to acquisition.
- Segmented **2,026 customers across 6 marketing campaigns**, isolating a **top tier worth 32% of
  spend at 2.21× response** and a **deal-dependent 34% of the base worth 10% of spend**, and
  delivered a targeting matrix with suppress/invest recommendations per segment.

---

## One-line version

Built an end-to-end customer and marketing analytics project in **Python, MySQL and Excel** across
**96,470 marketplace orders and 93,350 marketplace customers**, with a separate campaign dataset of
**2,026 customers**, showing that **97% of marketplace customers never return**
and translating RFM, campaign-response and discount analysis into a marketing-budget recommendation.

---

## Interview talking points

**"Tell me about a time your analysis changed the plan."**
I set out to build an RFM customer segmentation. The first thing I checked was whether frequency
actually varied — 97% of the customers had exactly one order. An RFM model would have put almost
everyone in the same frequency bucket and I'd have presented a segmentation that looked rigorous
and told you nothing. So I changed the method: a first-order-value framework, and the real finding,
which is that this business can't be retained into growth and should be managed as an acquisition
business.

**"What surprised you?"**
That delivery speed and review scores barely predicted repeat purchase. I expected a clear
relationship. Late delivery moved the repeat rate by half a percentage point on a 3% base — real
enough to be statistically detectable, far too small to build a business case on. I reported it as
a null result rather than stretching it, and it changed the recommendation: keep fixing delivery,
but justify it by reviews and refunds, not retention.

**"How do you know your numbers are right?"**
I computed everything three times — pandas, SQL and Excel formulas — and wrote a script that
compares all three and fails if they disagree. It caught two real bugs: a SQL repeat rate that
double-counted repeat customers across a join, and a state table mixing two grains. It also caught
a cohort retention figure that was 10× too high because one cohort had a single customer in it.

**"Why two datasets?"**
Because neither alone answered the question. Olist has scale and geography but no campaigns or
discounts; the campaign dataset has those but is small and has no time dimension. I kept them
completely separate — no joins, no shared keys, no combined figures — and used the contrast itself
as the argument: one business where retention marketing can't work, one where it demonstrably does.

---

## Skills this demonstrates

**Business:** acquisition vs retention economics · customer lifetime value reasoning under data
constraints · campaign targeting and suppression · promotional margin risk · market prioritisation
by geography · translating analysis into budget allocation · knowing when a standard method does not
apply.

**Technical:** Python (pandas, numpy, matplotlib, openpyxl) · SQL (star-schema design, foreign keys,
CTEs, window functions, multi-table joins) · relational data modelling · Excel formula modelling ·
RFM segmentation · cohort analysis · hypothesis testing · reproducible pipelines · cross-tool
verification · data provenance documentation.
