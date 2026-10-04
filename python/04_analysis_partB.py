"""
04_analysis_partB.py  -  Part B analysis: RFM, campaign response, discount behaviour
===================================================================================
Author: Pranit Ajay Chaudhari

Input : data/cleaned/partB_customers.csv
Output: outputs/tables/partB_*.csv

WHY RFM IS USED HERE AND NOT IN PART A: this customer base has real frequency variance
(0-32 purchases, median 12, only 0.2% with a single purchase), so the F dimension carries
information. Part A's marketplace does not, which is why Part A uses a first-order-value
framework instead. The same method is applied where it works and withheld where it does not.

Run:  python python/04_analysis_partB.py
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "cleaned"
TABLES = ROOT / "outputs" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def r(x, dp=2):
    if pd.isna(x):
        return x
    return float(Decimal(str(float(x))).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP))


def rs(s, dp=2):
    return s.map(lambda v: r(v, dp))


d = pd.read_csv(CLEAN / "partB_customers.csv", parse_dates=["Dt_Customer"])
CAMP = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
MNT = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]

print("PART B ANALYSIS\n" + "=" * 92)

# ============================================================== 1. RFM scoring
# Bands are the empirical quintile boundaries of THIS dataset, then FROZEN as fixed integers so
# the identical CASE expression reproduces in MySQL and in Excel. Recency is reversed: fewer days
# since the last purchase is better.
R_BANDS = [19, 39, 58, 79]        # R=5: 0-19, 4: 20-39, 3: 40-58, 2: 59-79, 1: 80+
F_BANDS = [7, 12, 17, 22]         # F=1: 0-7,  2: 8-12,  3: 13-17, 4: 18-22, 5: 23+
M_BANDS = [55, 199, 636, 1174]    # M=1: 0-55, 2: 56-199, 3: 200-636, 4: 637-1174, 5: 1175+

d["R"] = np.select([d.Recency <= R_BANDS[0], d.Recency <= R_BANDS[1],
                    d.Recency <= R_BANDS[2], d.Recency <= R_BANDS[3]], [5, 4, 3, 2], default=1)
d["F"] = np.select([d.TotalPurchases <= F_BANDS[0], d.TotalPurchases <= F_BANDS[1],
                    d.TotalPurchases <= F_BANDS[2], d.TotalPurchases <= F_BANDS[3]], [1, 2, 3, 4], default=5)
d["M"] = np.select([d.TotalSpend <= M_BANDS[0], d.TotalSpend <= M_BANDS[1],
                    d.TotalSpend <= M_BANDS[2], d.TotalSpend <= M_BANDS[3]], [1, 2, 3, 4], default=5)
d["RFMScore"] = d.R + d.F + d.M

# Four value tiers from the combined score. Deliberately NOT the 11-segment recency x frequency
# grid used elsewhere in this portfolio - this project's segmentation feeds a campaign-targeting
# matrix, so it is built on value, responsiveness and discount dependence instead.
d["ValueTier"] = np.select([d.RFMScore >= 13, d.RFMScore >= 10, d.RFMScore >= 7],
                           ["Best", "Core", "Occasional"], default="Marginal")
TIER_ORDER = ["Best", "Core", "Occasional", "Marginal"]

bands = pd.DataFrame({
    "Score": [5, 4, 3, 2, 1],
    "Recency_days": ["0-19", "20-39", "40-58", "59-79", "80+"],
    "Frequency_purchases": ["23+", "18-22", "13-17", "8-12", "0-7"],
    "Monetary_spend": ["1175+", "637-1174", "200-636", "56-199", "0-55"]})
bands.to_csv(TABLES / "partB_rfm_bands.csv", index=False)
print("\n1. RFM BANDS (frozen quintile boundaries, identical in Python, SQL and Excel)\n" + "-" * 92)
print(bands.to_string(index=False))

# ================================================= 2. value tiers and responsiveness
BASE = d.Response.mean()
tier = d.groupby("ValueTier").agg(
    Customers=("ID", "count"), AvgRFM=("RFMScore", "mean"), AvgRecency=("Recency", "mean"),
    AvgPurchases=("TotalPurchases", "mean"), AvgSpend=("TotalSpend", "mean"),
    TotalSpend=("TotalSpend", "sum"), AvgIncome=("Income", "mean"),
    AvgDealShare=("DealShare", "mean"), CampaignsAccepted=("CampaignsAccepted", "sum"),
    RespondedLast=("Response", "sum"), AvgWebVisits=("NumWebVisitsMonth", "mean")).reset_index()
tier["PctOfCustomers"] = rs(tier.Customers / len(d) * 100, 2)
tier["PctOfSpend"] = rs(tier.TotalSpend / d.TotalSpend.sum() * 100, 2)
tier["ResponseRate"] = rs(tier.RespondedLast / tier.Customers * 100, 2)
tier["ResponseLift"] = rs((tier.RespondedLast / tier.Customers) / BASE, 2)
for col in ["AvgRFM", "AvgRecency", "AvgPurchases", "AvgSpend", "AvgIncome", "AvgWebVisits"]:
    tier[col] = rs(tier[col], 2)
tier["AvgDealShare"] = rs(tier.AvgDealShare * 100, 2)
tier["TotalSpend"] = tier.TotalSpend.round(2)
tier = tier.set_index("ValueTier").reindex(TIER_ORDER).reset_index()
tier.to_csv(TABLES / "partB_value_tiers.csv", index=False)
print(f"\n2. VALUE TIERS AND CAMPAIGN RESPONSIVENESS (base response rate {r(BASE * 100, 2)}%)\n" + "-" * 92)
print(tier[["ValueTier", "Customers", "PctOfCustomers", "PctOfSpend", "AvgSpend", "AvgPurchases",
            "AvgRecency", "AvgIncome", "AvgDealShare", "ResponseRate", "ResponseLift"]].to_string(index=False))

# ================================================== 3. campaign-by-campaign response
camp_rows = []
for i, col in enumerate(CAMP + ["Response"], start=1):
    name = f"Campaign {col[-1]}" if col.startswith("AcceptedCmp") else "Most recent campaign"
    acc = int(d[col].sum())
    sub = d[d[col] == 1]
    camp_rows.append({
        "Campaign": name, "Accepted": acc, "ResponseRate": r(acc / len(d) * 100, 2),
        "AvgSpend_Accepted": r(sub.TotalSpend.mean(), 2) if acc else np.nan,
        "AvgSpend_Declined": r(d[d[col] == 0].TotalSpend.mean(), 2),
        "AvgIncome_Accepted": r(sub.Income.mean(), 2) if acc else np.nan,
        "AvgRFM_Accepted": r(sub.RFMScore.mean(), 2) if acc else np.nan,
        "PctWithChildren_Accepted": r(sub.HasChildren.mean() * 100, 2) if acc else np.nan,
        "PctPartnered_Accepted": r(sub.Partnered.mean() * 100, 2) if acc else np.nan})
camp = pd.DataFrame(camp_rows)
camp.to_csv(TABLES / "partB_campaign_performance.csv", index=False)
print("\n3. CAMPAIGN-BY-CAMPAIGN PERFORMANCE\n" + "-" * 92)
print(camp.to_string(index=False))

# campaign response by tier
ct = d.pivot_table(index="ValueTier", values=CAMP + ["Response"], aggfunc="mean").mul(100).round(2)
ct = ct.reindex(TIER_ORDER)
ct.insert(0, "Customers", d.ValueTier.value_counts().reindex(TIER_ORDER))
ct.to_csv(TABLES / "partB_campaign_by_tier.csv")
print("\n   Response rate (%) by value tier:")
print(ct.to_string())

# ===================================================== 4. discount dependence
# Deal-driven = upper quartile of deal share (>= 25% of purchases made on a deal).
DEAL_CUT = 0.25
d["DiscountBehaviour"] = np.where(d.DealShare >= DEAL_CUT, "Deal-driven", "Full-price")
disc = d.groupby("DiscountBehaviour").agg(
    Customers=("ID", "count"), AvgDealShare=("DealShare", "mean"),
    AvgSpend=("TotalSpend", "mean"), TotalSpend=("TotalSpend", "sum"),
    AvgPurchases=("TotalPurchases", "mean"), AvgSpendPerPurchase=("AvgSpendPerPurchase", "mean"),
    AvgIncome=("Income", "mean"), AvgRFM=("RFMScore", "mean"),
    ResponseRate=("Response", "mean"), AvgCampaigns=("CampaignsAccepted", "mean"),
    AvgWebVisits=("NumWebVisitsMonth", "mean")).reset_index()
disc["PctOfCustomers"] = rs(disc.Customers / len(d) * 100, 2)
disc["PctOfSpend"] = rs(disc.TotalSpend / d.TotalSpend.sum() * 100, 2)
disc["AvgDealShare"] = rs(disc.AvgDealShare * 100, 2)
disc["ResponseRate"] = rs(disc.ResponseRate * 100, 2)
for col in ["AvgSpend", "AvgPurchases", "AvgSpendPerPurchase", "AvgIncome", "AvgRFM", "AvgCampaigns", "AvgWebVisits"]:
    disc[col] = rs(disc[col], 2)
disc["TotalSpend"] = disc.TotalSpend.round(2)
disc.to_csv(TABLES / "partB_discount_behaviour.csv", index=False)
print(f"\n4. DISCOUNT DEPENDENCE (deal-driven = {int(DEAL_CUT * 100)}%+ of purchases on a deal)\n" + "-" * 92)
print(disc[["DiscountBehaviour", "Customers", "PctOfCustomers", "PctOfSpend", "AvgDealShare",
            "AvgSpend", "AvgSpendPerPurchase", "AvgPurchases", "AvgIncome", "ResponseRate"]].to_string(index=False))

# ============================================ 5. the campaign-targeting matrix
# The deliverable of Part B: value tier x responsiveness x discount dependence, each cell with a
# recommended action. This is what a marketing team would actually work from.
d["Responder"] = np.where(d.AnyCampaignAccepted, "Responder", "Non-responder")
mat = d.groupby(["ValueTier", "Responder", "DiscountBehaviour"]).agg(
    Customers=("ID", "count"), AvgSpend=("TotalSpend", "mean"), TotalSpend=("TotalSpend", "sum"),
    AvgDealShare=("DealShare", "mean"), ResponseRate=("Response", "mean"),
    AvgIncome=("Income", "mean")).reset_index()
mat["PctOfCustomers"] = rs(mat.Customers / len(d) * 100, 2)
mat["PctOfSpend"] = rs(mat.TotalSpend / d.TotalSpend.sum() * 100, 2)
mat["AvgDealShare"] = rs(mat.AvgDealShare * 100, 2)
mat["ResponseRate"] = rs(mat.ResponseRate * 100, 2)
mat["AvgSpend"] = rs(mat.AvgSpend, 2)
mat["AvgIncome"] = rs(mat.AvgIncome, 2)
mat["TotalSpend"] = mat.TotalSpend.round(2)


def action(row):
    t, resp, disc_b = row.ValueTier, row.Responder, row.DiscountBehaviour
    if t in ("Best", "Core") and resp == "Responder" and disc_b == "Full-price":
        return "Priority target - full-margin campaigns, early access, premium range"
    if t in ("Best", "Core") and resp == "Responder" and disc_b == "Deal-driven":
        return "Target, but with non-price offers - bundles and loyalty, not discounts"
    if t in ("Best", "Core") and resp == "Non-responder":
        return "High value, campaign-immune - serve well, do not spend campaign budget"
    if t == "Occasional" and resp == "Responder":
        return "Develop - test offers to raise basket size and frequency"
    if t == "Occasional":
        return "Low-cost nurture only"
    if disc_b == "Deal-driven":
        return "Suppress - discount-dependent and low value, campaigns erode margin"
    return "Suppress - minimal value, no campaign response"


mat["RecommendedAction"] = mat.apply(action, axis=1)
mat["ValueTier"] = pd.Categorical(mat.ValueTier, TIER_ORDER, ordered=True)
mat = mat.sort_values(["ValueTier", "Responder", "DiscountBehaviour"])
mat.to_csv(TABLES / "partB_targeting_matrix.csv", index=False)
print("\n5. CAMPAIGN-TARGETING MATRIX\n" + "-" * 92)
print(mat[["ValueTier", "Responder", "DiscountBehaviour", "Customers", "PctOfCustomers",
           "PctOfSpend", "AvgSpend", "ResponseRate"]].to_string(index=False))

# ==================================================== 6. channel mix by tier
ch = d.groupby("ValueTier").agg(Web=("NumWebPurchases", "sum"), Catalog=("NumCatalogPurchases", "sum"),
                                 Store=("NumStorePurchases", "sum"), Deals=("NumDealsPurchases", "sum"),
                                 WebVisits=("NumWebVisitsMonth", "mean")).reset_index()
ch["Total"] = ch.Web + ch.Catalog + ch.Store + ch.Deals
for col in ["Web", "Catalog", "Store", "Deals"]:
    ch[col + "Pct"] = rs(ch[col] / ch.Total * 100, 2)
ch["WebVisits"] = rs(ch.WebVisits, 2)
ch = ch.set_index("ValueTier").reindex(TIER_ORDER).reset_index()
ch.to_csv(TABLES / "partB_channel_mix.csv", index=False)
print("\n6. CHANNEL MIX BY TIER (% of purchases)\n" + "-" * 92)
print(ch[["ValueTier", "WebPct", "CatalogPct", "StorePct", "DealsPct", "WebVisits"]].to_string(index=False))

# =============================================== 7. demographics vs response
demo_rows = []
for dim, label in [("IncomeBand", "Income"), ("AgeBand", "Age"), ("Education", "Education"),
                   ("Marital_Status", "Marital status"), ("HasChildren", "Has children")]:
    g = d.groupby(dim, observed=True).agg(Customers=("ID", "count"), AvgSpend=("TotalSpend", "mean"),
                                           ResponseRate=("Response", "mean"),
                                           AvgDealShare=("DealShare", "mean"),
                                           AvgRFM=("RFMScore", "mean")).reset_index()
    g.columns = ["Group", "Customers", "AvgSpend", "ResponseRate", "AvgDealShare", "AvgRFM"]
    g.insert(0, "Dimension", label)
    g["Group"] = g.Group.astype(str)
    g["AvgSpend"] = rs(g.AvgSpend, 2)
    g["ResponseRate"] = rs(g.ResponseRate * 100, 2)
    g["AvgDealShare"] = rs(g.AvgDealShare * 100, 2)
    g["AvgRFM"] = rs(g.AvgRFM, 2)
    g["ResponseLift"] = rs(g.ResponseRate / (BASE * 100), 2)
    demo_rows.append(g)
demo = pd.concat(demo_rows, ignore_index=True)
demo.to_csv(TABLES / "partB_demographics.csv", index=False)
print("\n7. DEMOGRAPHICS VS SPEND AND RESPONSE\n" + "-" * 92)
print(demo.to_string(index=False))

# ======================================================== 8. category spend
cat = pd.DataFrame({
    "Category": [c.replace("Mnt", "").replace("Products", "").replace("Prods", "")
                 for c in MNT],
    "TotalSpend": [d[c].sum() for c in MNT],
    "AvgSpend": [r(d[c].mean(), 2) for c in MNT],
    "CustomersBuying": [int((d[c] > 0).sum()) for c in MNT]})
cat["PctOfSpend"] = rs(cat.TotalSpend / cat.TotalSpend.sum() * 100, 2)
cat["PctBuying"] = rs(cat.CustomersBuying / len(d) * 100, 2)
cat = cat.sort_values("TotalSpend", ascending=False)
cat.to_csv(TABLES / "partB_category_spend.csv", index=False)
print("\n8. CATEGORY SPEND\n" + "-" * 92)
print(cat.to_string(index=False))

# ============================================================== 9. headline KPIs
kpi = pd.DataFrame({"Metric": [
    "Customers analysed", "Total spend (2 years)", "Average spend per customer",
    "Average purchases per customer", "Average spend per purchase", "Median recency (days)",
    "Customers accepting at least one campaign", "Share accepting at least one campaign (%)",
    "Most recent campaign response rate (%)", "Best single campaign response rate (%)",
    "Worst single campaign response rate (%)", "Deal-driven customers",
    "Share of customers deal-driven (%)", "Share of all purchases made on a deal (%)",
    "Best tier share of customers (%)", "Best tier share of spend (%)",
    "Average income", "Customers who complained", "Enrolment window"],
    "Value": [
    len(d), r(d.TotalSpend.sum(), 2), r(d.TotalSpend.mean(), 2), r(d.TotalPurchases.mean(), 2),
    r(d.TotalSpend.sum() / d.TotalPurchases.sum(), 2), r(d.Recency.median(), 2),
    int(d.AnyCampaignAccepted.sum()), r(d.AnyCampaignAccepted.mean() * 100, 2),
    r(d.Response.mean() * 100, 2), r(camp[camp.Campaign != "Most recent campaign"].ResponseRate.max(), 2),
    r(camp[camp.Campaign != "Most recent campaign"].ResponseRate.min(), 2),
    int((d.DiscountBehaviour == "Deal-driven").sum()),
    r((d.DiscountBehaviour == "Deal-driven").mean() * 100, 2),
    r(d.NumDealsPurchases.sum() / d.TotalPurchases.sum() * 100, 2),
    r(tier.loc[tier.ValueTier == "Best", "PctOfCustomers"].iloc[0], 2),
    r(tier.loc[tier.ValueTier == "Best", "PctOfSpend"].iloc[0], 2),
    r(d.Income.mean(), 2), int(d.Complain.sum()),
    f"{d.Dt_Customer.min().date()} to {d.Dt_Customer.max().date()}"]})
kpi.to_csv(TABLES / "partB_kpis.csv", index=False)
print("\n9. HEADLINE KPIs\n" + "-" * 92)
print(kpi.to_string(index=False))

d.to_csv(CLEAN / "partB_customers.csv", index=False)   # now carries R, F, M, tiers, flags
print("\nPart B analysis complete.")
