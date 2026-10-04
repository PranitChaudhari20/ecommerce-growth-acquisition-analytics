"""
02_clean_partB.py  -  Part B cleaning: campaign-response and discount dataset
=============================================================================
Author: Pranit Ajay Chaudhari

Input : data/raw/marketing_campaign.csv   (tab-separated, 2,240 customer records)
Output: data/cleaned/partB_customers.csv
        data/cleaned/partB_cleaning_log.csv

This dataset is CUSTOMER-LEVEL, not transactional: one row per customer with two years of
behaviour already aggregated. That shapes what it can and cannot answer, which is documented in
docs/METHODOLOGY.md. It is kept entirely separate from Part A - there is no customer, product or
time key shared between the two datasets, so no join exists and none is invented.

Run:  python python/02_clean_partB.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "cleaned"
OUT.mkdir(parents=True, exist_ok=True)

LOG = []


def log(step, rows, note=""):
    LOG.append({"Step": step, "Rows": rows, "Note": note})
    print(f"  {len(LOG):>2}. {step:<60} {rows:>6,}  {note}")


print("PART B - campaign response and discount behaviour\n" + "=" * 80)

df = pd.read_csv(ROOT / "data" / "raw" / "marketing_campaign.csv", sep="\t")
log("Raw records loaded (tab-separated)", len(df), f"{df.shape[1]} columns")

MNT = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
NUM = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
CAMP = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]

# ------------------------------------------------- 1. duplicate customer records
# 182 rows are identical to another row across all 28 non-ID columns. Two customers matching on
# income to the rupee, six spend categories, every purchase count and all five campaign outcomes
# is a duplicated record, not a coincidence. Keeping them would double-count 8% of the base and
# inflate every campaign response rate.
dup_mask = df.drop(columns=["ID"]).duplicated(keep="first")
log("Duplicate customer records removed", len(df) - dup_mask.sum(),
    f"{dup_mask.sum()} rows identical across all 28 non-ID fields")
df = df[~dup_mask].copy()

# ------------------------------------------------------------ 2. constant columns
# Z_CostContact is 3 for every row and Z_Revenue is 11 for every row. A column with no variance
# carries no information and cannot participate in any analysis.
df = df.drop(columns=["Z_CostContact", "Z_Revenue"])
log("Zero-variance columns dropped", len(df), "Z_CostContact (always 3), Z_Revenue (always 11)")

# -------------------------------------------------------------- 3. birth years
# The reference year is the last enrolment date in the file (2014). Birth years of 1893, 1899 and
# 1900 imply ages of 114-121, which is a data-entry error rather than a customer.
df["Dt_Customer"] = pd.to_datetime(df.Dt_Customer, dayfirst=True, errors="coerce")
REF = df.Dt_Customer.max()
df["Age"] = REF.year - df.Year_Birth
bad_age = df.Age > 100
log("Implausible birth years removed", len(df) - bad_age.sum(),
    f"{bad_age.sum()} records with implied age over 100 ({sorted(df.loc[bad_age, 'Year_Birth'].tolist())})")
df = df[~bad_age].copy()

# ------------------------------------------------------------------ 4. income
missing_inc = df.Income.isna().sum()
df = df[df.Income.notna()].copy()
log("Records with missing income removed", len(df),
    f"{missing_inc} dropped rather than imputed - income drives the value segmentation")

# A single record reports 666,666, more than 8x the next highest. Treated as a data-entry
# artefact and removed so it cannot distort income banding or any mean.
inc_outlier = df.Income > 200_000
log("Income outlier removed", len(df) - inc_outlier.sum(),
    f"{inc_outlier.sum()} record at {df.loc[inc_outlier, 'Income'].max():,.0f} "
    f"vs next highest {df.loc[~inc_outlier, 'Income'].max():,.0f}")
df = df[~inc_outlier].copy()

# ------------------------------------------------------- 5. marital status tidy
# 'Absurd' and 'YOLO' are not marital statuses. 'Alone' means Single.
junk = df.Marital_Status.isin(["Absurd", "YOLO"])
log("Non-sensical marital statuses removed", len(df) - junk.sum(),
    f"{junk.sum()} records labelled 'Absurd' or 'YOLO'")
df = df[~junk].copy()
df["Marital_Status"] = df.Marital_Status.replace({"Alone": "Single"})
df["Partnered"] = df.Marital_Status.isin(["Married", "Together"])
log("Marital status harmonised", len(df), "'Alone' merged into 'Single'; Partnered flag added")

# ------------------------------------------------------------ 6. derived measures
df["TotalSpend"] = df[MNT].sum(axis=1)
df["FullPricePurchases"] = df[NUM].sum(axis=1)
# NumDealsPurchases counts discounted purchases; the other three count purchases by channel.
# Total purchases is the sum of both, and deal share is the discounted proportion.
df["TotalPurchases"] = df.FullPricePurchases + df.NumDealsPurchases
df["DealShare"] = np.where(df.TotalPurchases > 0, df.NumDealsPurchases / df.TotalPurchases, np.nan)
df["AvgSpendPerPurchase"] = np.where(df.TotalPurchases > 0, df.TotalSpend / df.TotalPurchases, np.nan)
df["Children"] = df.Kidhome + df.Teenhome
df["HasChildren"] = df.Children > 0
df["TenureDays"] = (REF - df.Dt_Customer).dt.days
df["CampaignsAccepted"] = df[CAMP].sum(axis=1)
df["AnyCampaignAccepted"] = df.CampaignsAccepted > 0
df["WineShare"] = np.where(df.TotalSpend > 0, df.MntWines / df.TotalSpend, np.nan)

zero_purch = (df.TotalPurchases == 0).sum()
log("Derived measures built", len(df),
    f"TotalSpend, TotalPurchases, DealShare, Age, Tenure, CampaignsAccepted "
    f"({zero_purch} customers with 0 purchases)")

df["IncomeBand"] = pd.cut(df.Income, [0, 25_000, 45_000, 65_000, 85_000, np.inf],
                          labels=["Under 25k", "25-45k", "45-65k", "65-85k", "85k+"])
df["AgeBand"] = pd.cut(df.Age, [0, 35, 45, 55, 65, np.inf],
                       labels=["Under 35", "35-44", "45-54", "55-64", "65+"])
log("Income and age bands assigned", len(df), "fixed, documented bands - reproducible in SQL and Excel")

# ------------------------------------------------------------------- 7. write
cols = ["ID", "Age", "AgeBand", "Education", "Marital_Status", "Partnered", "Income", "IncomeBand",
        "Kidhome", "Teenhome", "Children", "HasChildren", "Dt_Customer", "TenureDays", "Recency",
        *MNT, "TotalSpend", "WineShare",
        "NumDealsPurchases", *NUM, "FullPricePurchases", "TotalPurchases", "DealShare",
        "AvgSpendPerPurchase", "NumWebVisitsMonth",
        *CAMP, "CampaignsAccepted", "AnyCampaignAccepted", "Response", "Complain"]
out = df[cols].copy()
out.to_csv(OUT / "partB_customers.csv", index=False)
pd.DataFrame(LOG).to_csv(OUT / "partB_cleaning_log.csv", index=False)

print("\n" + "=" * 80)
print(f"  partB_customers.csv   {len(out):>6,} customers x {out.shape[1]} columns")
print(f"  reference date        {REF.date()} (latest enrolment)")
print(f"  retained              {len(out) / 2240 * 100:.1f}% of raw records")
print(f"  total spend           {out.TotalSpend.sum():>10,.0f}")
print(f"  accepted >=1 campaign {out.AnyCampaignAccepted.sum():>6,} ({out.AnyCampaignAccepted.mean() * 100:.1f}%)")
