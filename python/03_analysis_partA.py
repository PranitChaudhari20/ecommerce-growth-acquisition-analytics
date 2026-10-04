"""
03_analysis_partA.py  -  Part A analysis: acquisition economics of a marketplace
===============================================================================
Author: Pranit Ajay Chaudhari

Input : data/cleaned/partA_*.csv
Output: outputs/tables/partA_*.csv   every table quoted in the documentation

THE QUESTION THIS PART ANSWERS: where should a marketplace put its marketing money when almost
nobody comes back? It starts by TESTING whether RFM segmentation is even applicable, rather than
assuming it, and reports the answer either way.

Run:  python python/03_analysis_partA.py
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "cleaned"
TABLES = ROOT / "outputs" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

# MySQL ROUND() rounds a half away from zero; numpy rounds a half to even, so an exact 26.25
# becomes 26.3 in SQL and 26.2 in pandas. Every published figure goes through r() so the Python,
# SQL and Excel numbers are identical rather than nearly so.
def r(x, dp=2):
    if pd.isna(x):
        return x
    return float(Decimal(str(float(x))).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def rs(s, dp=2):
    return s.map(lambda v: r(v, dp))


o = pd.read_csv(CLEAN / "partA_orders.csv", parse_dates=["OrderDate"])
c = pd.read_csv(CLEAN / "partA_customers.csv", parse_dates=["FirstOrderDate", "LastOrderDate"])
it = pd.read_csv(CLEAN / "partA_order_items.csv")

print("PART A ANALYSIS\n" + "=" * 90)

# ============================================================ 1. the central test
print("\n1. IS RFM SEGMENTATION APPLICABLE HERE?\n" + "-" * 90)
freq = c.Orders.value_counts().sort_index()
single = int((c.Orders == 1).sum())
viability = pd.DataFrame({
    "Check": ["Customers", "Customers with exactly 1 order", "Customers with 2+ orders",
              "Share with exactly 1 order (%)", "Maximum orders by one customer",
              "Distinct frequency values", "Share of customers in the modal frequency (%)"],
    "Value": [len(c), single, int((c.Orders >= 2).sum()), r(single / len(c) * 100, 2),
              int(c.Orders.max()), int(c.Orders.nunique()), r(single / len(c) * 100, 2)]})
viability.to_csv(TABLES / "partA_rfm_viability.csv", index=False)
print(viability.to_string(index=False))
print(f"\n   VERDICT: Frequency is {r(single / len(c) * 100, 1)}% a single value. An RFM model scoring F"
      f"\n   1-5 would place {r(single / len(c) * 100, 1)}% of customers in one bucket, so the F dimension"
      f"\n   carries almost no information. Classical RFM is NOT the right tool for this business.")

freq_dist = (freq.rename_axis("Orders").reset_index(name="Customers"))
freq_dist["PctOfCustomers"] = rs(freq_dist.Customers / len(c) * 100, 2)
rev_by_freq = o.groupby(o.CustomerID.map(c.set_index("CustomerID").Orders)).OrderValue.sum()
freq_dist["Revenue"] = freq_dist.Orders.map(rev_by_freq).round(2)
freq_dist["PctOfRevenue"] = rs(freq_dist.Revenue / o.OrderValue.sum() * 100, 2)
freq_dist.to_csv(TABLES / "partA_frequency_distribution.csv", index=False)

# ====================================================== 2. first vs repeat revenue
print("\n2. WHERE DOES REVENUE COME FROM?\n" + "-" * 90)
split = o.groupby("IsFirstOrder").agg(Orders=("order_id", "count"),
                                      Revenue=("OrderValue", "sum"),
                                      AOV=("OrderValue", "mean")).reset_index()
split["OrderType"] = np.where(split.IsFirstOrder, "First order", "Repeat order")
split["PctOfOrders"] = rs(split.Orders / len(o) * 100, 2)
split["PctOfRevenue"] = rs(split.Revenue / o.OrderValue.sum() * 100, 2)
split["Revenue"] = split.Revenue.round(2)
split["AOV"] = rs(split.AOV, 2)
split = split[["OrderType", "Orders", "PctOfOrders", "Revenue", "PctOfRevenue", "AOV"]]
split.to_csv(TABLES / "partA_first_vs_repeat_revenue.csv", index=False)
print(split.to_string(index=False))

# ============================================== 3. customer value and a CLV proxy
print("\n3. CUSTOMER VALUE AND CLV PROXY\n" + "-" * 90)
repeat_rate = c.IsRepeat.mean()
avg_first = c.FirstOrderValue.mean()
avg_repeat_orders = c.loc[c.IsRepeat, "Orders"].mean() - 1
avg_repeat_val = o.loc[~o.IsFirstOrder, "OrderValue"].mean()
clv_proxy = avg_first + repeat_rate * avg_repeat_orders * avg_repeat_val
# This is a DECOMPOSITION of observed revenue per customer, not a forward-looking model: the
# components multiply back to the observed mean by construction. Its value is showing WHERE a
# customer's worth comes from, which is the decision-relevant part.
clv = pd.DataFrame({
    "Component": ["Average first-order value (R$)", "Probability of a second order (%)",
                  "Average additional orders, given a repeat", "Average value of a repeat order (R$)",
                  "Retention contribution per acquired customer (R$)",
                  "Total revenue per acquired customer (R$)",
                  "Share of customer value earned on the first order (%)"],
    "Value": [r(avg_first, 2), r(repeat_rate * 100, 2), r(avg_repeat_orders, 2), r(avg_repeat_val, 2),
              r(clv_proxy - avg_first, 2), r(clv_proxy, 2), r(avg_first / clv_proxy * 100, 2)]})
clv.to_csv(TABLES / "partA_clv_proxy.csv", index=False)
print(clv.to_string(index=False))
print(f"\n   Because only {r(repeat_rate * 100, 1)}% of customers ever return, the expected value of an"
      f"\n   acquired customer is almost entirely their FIRST order. Retention contributes"
      f"\n   R$ {r(clv_proxy - avg_first, 2)} of the R$ {r(clv_proxy, 2)} total - {r((clv_proxy - avg_first) / clv_proxy * 100, 1)}%.")

# value tiers on total revenue
q = c.TotalRevenue.quantile([0.5, 0.8]).to_dict()
c["ValueTier"] = np.where(c.TotalRevenue >= q[0.8], "High",
                          np.where(c.TotalRevenue >= q[0.5], "Medium", "Low"))
tier = c.groupby("ValueTier").agg(Customers=("CustomerID", "count"),
                                  Revenue=("TotalRevenue", "sum"),
                                  AvgRevenue=("TotalRevenue", "mean"),
                                  AvgOrders=("Orders", "mean"),
                                  RepeatRate=("IsRepeat", "mean"),
                                  AvgReview=("AvgReviewScore", "mean")).reset_index()
tier["PctOfCustomers"] = rs(tier.Customers / len(c) * 100, 2)
tier["PctOfRevenue"] = rs(tier.Revenue / c.TotalRevenue.sum() * 100, 2)
tier["Revenue"] = tier.Revenue.round(2)
for col in ["AvgRevenue", "AvgOrders", "AvgReview"]:
    tier[col] = rs(tier[col], 2)
tier["RepeatRate"] = rs(tier.RepeatRate * 100, 2)
tier = tier.set_index("ValueTier").reindex(["High", "Medium", "Low"]).reset_index()
tier.to_csv(TABLES / "partA_value_tiers.csv", index=False)
print("\n   Value tiers (top 20% / next 30% / bottom 50% by total revenue):")
print(tier.to_string(index=False))

# ========================= 4. does the customer experience drive a second order?
print("\n4. DOES DELIVERY PERFORMANCE PREDICT A SECOND ORDER?\n" + "-" * 90)
first = o[o.IsFirstOrder].copy()
first["BecameRepeat"] = first.CustomerID.map(c.set_index("CustomerID").IsRepeat)
_rv_tmp = first[first.ReviewScore.notna()].groupby("ReviewScore").agg(
    FirstOrders=("order_id", "count"), BecameRepeat=("BecameRepeat", "sum")).reset_index()
_rv_tmp["RepeatRate"] = rs(_rv_tmp.BecameRepeat / _rv_tmp.FirstOrders * 100, 2)
_rv_tmp["ReviewScore"] = _rv_tmp.ReviewScore.astype(int)
rv = _rv_tmp
first["LateBand"] = np.where(first.DaysVsPromise > 0, "Late", "On time or early")
deliv = first.groupby("LateBand").agg(FirstOrders=("order_id", "count"),
                                       BecameRepeat=("BecameRepeat", "sum"),
                                       AvgDeliveryDays=("DeliveryDays", "mean"),
                                       AvgOrderValue=("OrderValue", "mean")).reset_index()
deliv["RepeatRate"] = rs(deliv.BecameRepeat / deliv.FirstOrders * 100, 2)
deliv["AvgDeliveryDays"] = rs(deliv.AvgDeliveryDays, 2)
deliv["AvgOrderValue"] = rs(deliv.AvgOrderValue, 2)
deliv.to_csv(TABLES / "partA_delivery_vs_repeat.csv", index=False)
print(deliv.to_string(index=False))
ontime = deliv.loc[deliv.LateBand == "On time or early", "RepeatRate"].iloc[0]
late = deliv.loc[deliv.LateBand == "Late", "RepeatRate"].iloc[0]


def ztest(s1, n1, s2, n2):
    """Two-proportion z-test. Returns (difference in pp, z, two-sided p)."""
    from math import sqrt, erfc
    p1, p2 = s1 / n1, s2 / n2
    pp = (s1 + s2) / (n1 + n2)
    se = sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se else 0.0
    return (p1 - p2) * 100, z, erfc(abs(z) / sqrt(2))


dL = deliv.set_index("LateBand")
dpp, dz, dp = ztest(int(dL.loc["Late", "BecameRepeat"]), int(dL.loc["Late", "FirstOrders"]),
                    int(dL.loc["On time or early", "BecameRepeat"]), int(dL.loc["On time or early", "FirstOrders"]))
print(f"\n   Late first delivery -> repeat rate {late}% vs {ontime}% on time.")
print(f"   Difference {r(dpp, 2)} pp | z = {r(dz, 2)} | p = {r(dp, 4)} "
      f"-> {'statistically detectable' if dp < 0.05 else 'NOT statistically significant'}, "
      f"and {r(abs(dpp), 2)} pp on a {r(first.BecameRepeat.mean() * 100, 2)}% base is commercially negligible.")

r5 = rv.set_index("ReviewScore")
rpp, rz, rp = ztest(int(r5.loc[5, "BecameRepeat"]), int(r5.loc[5, "FirstOrders"]),
                    int(r5.loc[1, "BecameRepeat"]), int(r5.loc[1, "FirstOrders"]))
sig = pd.DataFrame({
    "Comparison": ["On-time vs late first delivery", "5-star vs 1-star first review"],
    "GroupA": ["On time or early", "5-star"],
    "RepeatRateA_pct": [ontime, r5.loc[5, "RepeatRate"]],
    "GroupB": ["Late", "1-star"],
    "RepeatRateB_pct": [late, r5.loc[1, "RepeatRate"]],
    "DifferencePP": [r(-dpp, 2), r(rpp, 2)],
    "Z": [r(-dz, 2), r(rz, 2)],
    "P_value": [r(dp, 4), r(rp, 4)],
    "StatisticallySignificant_5pct": [dp < 0.05, rp < 0.05],
    "CommerciallyMeaningful": [False, False]})
sig.to_csv(TABLES / "partA_cx_significance.csv", index=False)

# delivery speed bands
first["SpeedBand"] = pd.cut(first.DeliveryDays, [-1, 3, 7, 14, 21, np.inf],
                            labels=["0-3 days", "4-7 days", "8-14 days", "15-21 days", "22+ days"])
speed = first.groupby("SpeedBand", observed=True).agg(
    FirstOrders=("order_id", "count"), BecameRepeat=("BecameRepeat", "sum"),
    AvgReview=("ReviewScore", "mean")).reset_index()
speed["RepeatRate"] = rs(speed.BecameRepeat / speed.FirstOrders * 100, 2)
speed["AvgReview"] = rs(speed.AvgReview, 2)
speed.to_csv(TABLES / "partA_delivery_speed_bands.csv", index=False)
print("\n   By delivery speed:")
print(speed.to_string(index=False))

# ==================================================== 5. does review score drive repeat?
print("\n5. DOES REVIEW SCORE PREDICT A SECOND ORDER?\n" + "-" * 90)
rv = first[first.ReviewScore.notna()].groupby("ReviewScore").agg(
    FirstOrders=("order_id", "count"), BecameRepeat=("BecameRepeat", "sum"),
    AvgOrderValue=("OrderValue", "mean"), LateShare=("LateDelivery", "mean")).reset_index()
rv["RepeatRate"] = rs(rv.BecameRepeat / rv.FirstOrders * 100, 2)
rv["AvgOrderValue"] = rs(rv.AvgOrderValue, 2)
rv["LateShare"] = rs(rv.LateShare * 100, 2)
rv["ReviewScore"] = rv.ReviewScore.astype(int)
rv.to_csv(TABLES / "partA_review_vs_repeat.csv", index=False)
print(rv.to_string(index=False))

# ============================================================ 6. state economics
print("\n6. WHICH STATES ARE WORTH ACQUIRING IN?\n" + "-" * 90)
# One grain for the whole state table: geography is an attribute of the CUSTOMER (their first
# order's state), and every order is attributed to that customer's state. Previously orders were
# grouped by the state on the order while customers were grouped by the state on the customer, so
# the two disagreed for the few customers who ordered from more than one state - and the SQL
# version, which only has the customer's state, could never reproduce it.
o = o.drop(columns=["State"]).merge(c[["CustomerID", "State"]], on="CustomerID", how="left")
st = o.groupby("State").agg(Orders=("order_id", "count"), Revenue=("OrderValue", "sum"),
                            AOV=("OrderValue", "mean"), Freight=("Freight", "sum"),
                            ItemsValue=("ItemsValue", "sum"),
                            AvgDeliveryDays=("DeliveryDays", "mean"),
                            LateShare=("LateDelivery", "mean"),
                            AvgReview=("ReviewScore", "mean")).reset_index()
st["Customers"] = st.State.map(c.groupby("State").CustomerID.nunique())
st["RepeatRate"] = rs(st.State.map(c.groupby("State").IsRepeat.mean()) * 100, 2)
st["FreightShare"] = rs(st.Freight / st.Revenue * 100, 2)
st["PctOfRevenue"] = rs(st.Revenue / st.Revenue.sum() * 100, 2)
st["Revenue"] = st.Revenue.round(2)
for col in ["AOV", "AvgDeliveryDays", "AvgReview"]:
    st[col] = rs(st[col], 2)
st["LateShare"] = rs(st.LateShare * 100, 2)
st = st[["State", "Customers", "Orders", "Revenue", "PctOfRevenue", "AOV", "FreightShare",
         "AvgDeliveryDays", "LateShare", "AvgReview", "RepeatRate"]].sort_values("Revenue", ascending=False)
st.to_csv(TABLES / "partA_state_summary.csv", index=False)
print(st.head(12).to_string(index=False))
print(f"\n   {len(st)} states. Top 3 = {r(st.PctOfRevenue.head(3).sum(), 2)}% of revenue.")

# ============================================================ 7. category analysis
print("\n7. WHICH CATEGORIES BRING CUSTOMERS IN, AND WHICH BRING THEM BACK?\n" + "-" * 90)
it2 = it.merge(o[["order_id", "IsFirstOrder", "CustomerID"]], on="order_id", how="left")
cat = it2.groupby("Category").agg(Lines=("order_item_id", "count"), Revenue=("LineRevenue", "sum"),
                                  AvgPrice=("price", "mean"), Orders=("order_id", "nunique"),
                                  Sellers=("seller_id", "nunique")).reset_index()
cat["PctOfRevenue"] = rs(cat.Revenue / cat.Revenue.sum() * 100, 2)
first_lines = it2[it2.IsFirstOrder].groupby("Category").order_item_id.count()
rep_lines = it2[~it2.IsFirstOrder].groupby("Category").order_item_id.count()
cat["FirstOrderLines"] = cat.Category.map(first_lines).fillna(0).astype(int)
cat["RepeatOrderLines"] = cat.Category.map(rep_lines).fillna(0).astype(int)
cat["RepeatLineShare"] = rs(cat.RepeatOrderLines / cat.Lines * 100, 2)
cat["Revenue"] = cat.Revenue.round(2)
cat["AvgPrice"] = rs(cat.AvgPrice, 2)
cat = cat.sort_values("Revenue", ascending=False)
cat.to_csv(TABLES / "partA_category_summary.csv", index=False)
print(cat.head(12).to_string(index=False))
print(f"\n   {len(cat)} categories. Top 10 = {r(cat.PctOfRevenue.head(10).sum(), 2)}% of revenue.")

# ======================================================= 8. payment installments
print("\n8. DO INSTALLMENTS SIGNAL PRICE SENSITIVITY?\n" + "-" * 90)
o["InstBand"] = pd.cut(o.PaymentInstallments, [-1, 1, 3, 6, 12, np.inf],
                       labels=["1 (single payment)", "2-3", "4-6", "7-12", "13+"])
inst = o.groupby("InstBand", observed=True).agg(
    Orders=("order_id", "count"), AvgOrderValue=("OrderValue", "mean"),
    MedianOrderValue=("OrderValue", "median"), Revenue=("OrderValue", "sum"),
    AvgItems=("Items", "mean"), AvgReview=("ReviewScore", "mean")).reset_index()
inst["PctOfOrders"] = rs(inst.Orders / len(o) * 100, 2)
inst["Revenue"] = inst.Revenue.round(2)
for col in ["AvgOrderValue", "MedianOrderValue", "AvgItems", "AvgReview"]:
    inst[col] = rs(inst[col], 2)
inst.to_csv(TABLES / "partA_installments.csv", index=False)
print(inst.to_string(index=False))

pt = o.groupby("PaymentType").agg(Orders=("order_id", "count"), Revenue=("OrderValue", "sum"),
                                   AvgOrderValue=("OrderValue", "mean"),
                                   AvgInstallments=("PaymentInstallments", "mean")).reset_index()
pt["PctOfOrders"] = rs(pt.Orders / len(o) * 100, 2)
pt["Revenue"] = pt.Revenue.round(2)
pt["AvgOrderValue"] = rs(pt.AvgOrderValue, 2)
pt["AvgInstallments"] = rs(pt.AvgInstallments, 2)
pt = pt.sort_values("Orders", ascending=False)
pt.to_csv(TABLES / "partA_payment_types.csv", index=False)
print("\n   By payment method:")
print(pt.to_string(index=False))

# =================================================== 9. monthly new vs returning
print("\n9. IS GROWTH COMING FROM NEW CUSTOMERS OR ORDER VALUE?\n" + "-" * 90)
mon = o.groupby("OrderMonth").agg(Orders=("order_id", "count"), Revenue=("OrderValue", "sum"),
                                   AOV=("OrderValue", "mean"),
                                   Customers=("CustomerID", "nunique")).reset_index()
newc = o[o.IsFirstOrder].groupby("OrderMonth").CustomerID.nunique()
mon["NewCustomers"] = mon.OrderMonth.map(newc).fillna(0).astype(int)
mon["ReturningCustomers"] = mon.Customers - mon.NewCustomers
mon["PctNew"] = rs(mon.NewCustomers / mon.Customers * 100, 2)
mon["Revenue"] = mon.Revenue.round(2)
mon["AOV"] = rs(mon.AOV, 2)
mon.to_csv(TABLES / "partA_monthly.csv", index=False)
print(mon.tail(14).to_string(index=False))
full = mon[(mon.OrderMonth >= "2017-01") & (mon.OrderMonth <= "2018-07")]
print(f"\n   Over the {len(full)} complete months Jan 2017 - Jul 2018, new customers made up "
      f"{r(full.NewCustomers.sum() / full.Customers.sum() * 100, 1)}% of monthly actives.")

# ========================================================= 10. cohort retention
print("\n10. COHORT RETENTION\n" + "-" * 90)
c["CohortMonth"] = c.FirstOrderDate.dt.to_period("M").astype(str)
oc = o.merge(c[["CustomerID", "CohortMonth"]], on="CustomerID", how="left")
oc["MonthsSince"] = ((oc.OrderDate.dt.to_period("M").astype("int64") -
                      pd.PeriodIndex(oc.CohortMonth, freq="M").astype("int64")))
size = c.groupby("CohortMonth").CustomerID.nunique()
piv = (oc[oc.MonthsSince.between(0, 11)]
       .pivot_table(index="CohortMonth", columns="MonthsSince", values="CustomerID", aggfunc="nunique"))
retn = piv.div(piv[0], axis=0).mul(100).round(2)
retn.insert(0, "CohortSize", size)
retn.to_csv(TABLES / "partA_cohort_retention.csv")

# The retention curve is CUSTOMER-WEIGHTED, not a plain mean of cohort percentages. An unweighted
# mean lets a tiny cohort dominate: the December 2016 cohort contains ONE customer who happened to
# order again, so its month-1 retention is 100%, which alone lifted an unweighted month-1 average
# from 0.45% to 5.45%. Cohorts below 100 customers are excluded as well, and both choices are
# stated here rather than left for a reader to discover.
MIN_COHORT = 100
big = size[size >= MIN_COHORT].index
excluded = size[size < MIN_COHORT]
rows = []
for m in range(0, 12):
    if m not in piv.columns:
        rows.append({"MonthsSinceFirstOrder": m, "CohortsUsed": 0, "CustomersAtRisk": 0,
                     "CustomersActive": 0, "WeightedRetentionPct": np.nan})
        continue
    cols = [0] if m == 0 else [0, m]          # [0, 0] would select the same column twice
    sub = piv.loc[piv.index.isin(big), cols].dropna(subset=[m])
    at_risk = float(sub[0].sum())
    active = float(sub[m].sum())
    rows.append({"MonthsSinceFirstOrder": m, "CohortsUsed": int(len(sub)),
                 "CustomersAtRisk": int(at_risk), "CustomersActive": int(active),
                 "WeightedRetentionPct": r(active / at_risk * 100, 2) if at_risk else np.nan})
curve = pd.DataFrame(rows)
curve.to_csv(TABLES / "partA_retention_curve.csv", index=False)
print(f"   customer-weighted; {len(excluded)} cohorts under {MIN_COHORT} customers excluded "
      f"({dict(excluded)})")
print(curve.to_string(index=False))

# ============================================================ 11. seller concentration
sel = it.groupby("seller_id").agg(Lines=("order_item_id", "count"),
                                   Revenue=("LineRevenue", "sum"),
                                   Orders=("order_id", "nunique")).reset_index()
sel = sel.sort_values("Revenue", ascending=False)
sel["CumPctRevenue"] = rs(sel.Revenue.cumsum() / sel.Revenue.sum() * 100, 2)
top10 = int(np.ceil(len(sel) * 0.10))
seller_conc = pd.DataFrame({
    "Measure": ["Sellers", "Top 1% of sellers - share of revenue (%)",
                "Top 10% of sellers - share of revenue (%)",
                "Sellers needed for 50% of revenue", "Median seller revenue"],
    "Value": [len(sel), r(sel.Revenue.head(max(1, int(np.ceil(len(sel) * 0.01)))).sum() / sel.Revenue.sum() * 100, 2),
              r(sel.Revenue.head(top10).sum() / sel.Revenue.sum() * 100, 2),
              int((sel.CumPctRevenue <= 50).sum() + 1), r(sel.Revenue.median(), 2)]})
seller_conc.to_csv(TABLES / "partA_seller_concentration.csv", index=False)
print("\n11. SELLER CONCENTRATION\n" + "-" * 90)
print(seller_conc.to_string(index=False))

# =============================================================== 12. headline KPIs
kpi = pd.DataFrame({"Metric": [
    "Orders analysed", "Customers", "Gross revenue (R$)", "Items value (R$)", "Freight (R$)",
    "Average order value (R$)", "Median order value (R$)", "Repeat customers",
    "Repeat rate (%)", "Revenue from first orders (%)", "Average first-order value (R$)",
    "CLV proxy per acquired customer (R$)", "States covered", "Cities covered",
    "Product categories", "Sellers", "Average delivery days", "Late deliveries (%)",
    "Average review score", "Orders paid in installments (%)",
    "Revenue from top 20% of customers (%)", "Analysis window"],
    "Value": [
    len(o), len(c), r(o.OrderValue.sum(), 2), r(o.ItemsValue.sum(), 2), r(o.Freight.sum(), 2),
    r(o.OrderValue.mean(), 2), r(o.OrderValue.median(), 2), int(c.IsRepeat.sum()),
    r(c.IsRepeat.mean() * 100, 2), r(split.loc[split.OrderType == "First order", "PctOfRevenue"].iloc[0], 2),
    r(c.FirstOrderValue.mean(), 2), r(clv_proxy, 2), int(o.State.nunique()), int(o.City.nunique()),
    int(it.Category.nunique()), int(it.seller_id.nunique()), r(o.DeliveryDays.mean(), 2),
    r(o.LateDelivery.mean() * 100, 2), r(o.ReviewScore.mean(), 2),
    r((o.PaymentInstallments > 1).mean() * 100, 2),
    r(tier.loc[tier.ValueTier == "High", "PctOfRevenue"].iloc[0], 2),
    f"{o.OrderDate.min().date()} to {o.OrderDate.max().date()}"]})
kpi.to_csv(TABLES / "partA_kpis.csv", index=False)
print("\n12. HEADLINE KPIs\n" + "-" * 90)
print(kpi.to_string(index=False))
c.to_csv(CLEAN / "partA_customers.csv", index=False)   # now carries ValueTier + CohortMonth
print("\nPart A analysis complete.")
