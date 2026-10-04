# Limitations

*Author: Pranit Ajay Chaudhari*

An honest list. None of these is a defect in the work; each is a real boundary on what the data can
support, and each is stated because a recommendation built past it would be guesswork.

## The two datasets cannot be combined

They describe different companies, in different countries, years apart, and share no customer,
product, date or geography key. The synthesis in this project is a **comparison of two business
situations**, not an integrated view of one business. Anyone wanting a single end-to-end funnel
would need a dataset carrying transactions *and* campaign history for the same customers — which is
exactly what neither public dataset provides.

## Neither dataset contains margin

Every recommendation here is framed in **revenue and contact cost**, never profit. "Deal-driven
customers buy at a margin the basket does not support" is an inference from a 3.6× lower spend per
purchase, not a margin calculation — the data contains no cost of goods. A real decision would need
the P&L.

## Part A

- **No marketing data at all.** Olist carries no campaigns, no discounts, no channel attribution and
  no acquisition cost. So Part A can say *where* the valuable customers are and *what* they are
  worth, but not *what it cost to get them*. The conclusion "spend on acquisition" would need
  customer-acquisition cost to be turned into a budget.
- **Reviews cover delivered orders only.** The angriest customers — those whose orders were
  cancelled or never arrived — are excluded by construction, so the 4.14 average review score is
  flattering.
- **Two years, one marketplace, 2016–2018.** Olist was growing rapidly through the window, which is
  part of why the repeat rate is so low: a large share of customers simply had not had time to
  return. The 3.0% figure is a fact about this window, not a permanent property of the business.
- **The 15-order maximum** suggests the dataset may not capture every order for every person, or
  that `customer_unique_id` resolution is imperfect. The repeat rate should be read as a lower
  bound.
- **No product-level cost, stock or margin**, so category recommendations are about revenue mix
  only.

## Part B

- **Customer-level, not transactional.** One row per customer with two years already aggregated. So
  there is **no cohort analysis, no monthly trend, no new-versus-returning split and no basket
  analysis** — those questions cannot be asked of this file at all.
- **2,026 customers is small.** Campaign 2 was accepted by 26 people; a response rate built on 26
  observations moves a lot on small changes. Findings resting on the smallest cells are the least
  reliable, and the campaign-by-tier table has cells in single digits.
- **The company is not named** and the currency is not stated in the file. Spend figures are treated
  as currency units and the project does not claim to know which currency.
- **"Recency" is given, not derived.** The file supplies days since last purchase with no purchase
  dates, so it cannot be recomputed or audited.
- **Campaign content is unknown.** The data records *that* a campaign was accepted, never what was
  offered. So the project can say Campaign 3 reached families and Campaign 5 reached affluent
  childless customers, but not *why* — the creative, the offer and the channel are all absent.

## Method

- **The CLV figure is a decomposition, not a forecast.** Its components multiply back to observed
  revenue per customer by construction. It shows where value comes from; it does not predict
  anything.
- **Correlation, not causation.** Late delivery is associated with a 0.49 pp lower repeat rate. The
  project does not claim it causes it — slow-delivering regions differ in many ways at once.
- **The value tiers are quantile cuts**, not a clustering model. They are reproducible in three
  tools, which is what mattered here; a k-means segmentation would be a reasonable extension.
- **No Power BI.** Power BI Desktop is Windows-only and could not be verified in the environment
  this was built in, so rather than ship unverified files and screenshots, it is not part of this
  project.
