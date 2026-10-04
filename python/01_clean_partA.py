"""
01_clean_partA.py  -  Part A cleaning: Olist Brazilian e-commerce marketplace
=============================================================================
Author: Pranit Ajay Chaudhari

Input : data/raw/olist_*.csv  (8 files)
Output: data/cleaned/partA_orders.csv       one row per order, customer-keyed, with revenue,
                                            delivery performance, payment and review attributes
        data/cleaned/partA_order_items.csv  one row per order line, with product category
        data/cleaned/partA_customers.csv    one row per customer_unique_id
        data/cleaned/partA_cleaning_log.csv every step and the row count after it

THE DECISION THAT DRIVES EVERYTHING: Olist ships TWO customer keys.
  - customer_id        = one value per ORDER (99,441 of them). Joining on this makes every
                         customer look like a one-time buyer by construction.
  - customer_unique_id = the actual person (96,096 of them).
Using customer_id would silently destroy all repeat-purchase analysis and report a 0% repeat
rate. Everything customer-level in this project keys on customer_unique_id.

Run:  python python/01_clean_partA.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "cleaned"
OUT.mkdir(parents=True, exist_ok=True)

LOG = []


def log(step, rows, note=""):
    LOG.append({"Step": step, "Rows": rows, "Note": note})
    print(f"  {len(LOG):>2}. {step:<58} {rows:>9,}  {note}")


print("PART A - Olist marketplace\n" + "=" * 78)

# ----------------------------------------------------------------- 1. load
orders = pd.read_csv(RAW / "olist_orders_dataset.csv",
                     parse_dates=["order_purchase_timestamp", "order_approved_at",
                                  "order_delivered_carrier_date", "order_delivered_customer_date",
                                  "order_estimated_delivery_date"])
log("Raw orders loaded", len(orders))

customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
log("Raw customer rows loaded", len(customers),
    f"{customers.customer_id.nunique():,} customer_id vs {customers.customer_unique_id.nunique():,} customer_unique_id")

items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
log("Raw order items loaded", len(items))

payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
log("Raw payment rows loaded", len(payments))

# As Olist publishes it, this file has 105,764 LINES but 100,000 records, because review comments
# contain embedded newlines - counting lines would overstate reviews by 5.8%. The committed copy
# has the comment columns removed (see python/00_prepare_raw.py and data/raw/README.md), so it no
# longer has that property, but parsing rather than line-counting is correct either way.
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
log("Raw reviews loaded (parsed, not line-counted)", len(reviews),
    "as published the file has 105,764 lines for these 100,000 records")

products = pd.read_csv(RAW / "olist_products_dataset.csv")
trans = pd.read_csv(RAW / "product_category_name_translation.csv")
sellers = pd.read_csv(RAW / "olist_sellers_dataset.csv")
log("Raw products / categories / sellers loaded", len(products),
    f"{len(trans)} category translations, {len(sellers):,} sellers")

# ------------------------------------------------- 2. attach the real customer key
orders = orders.merge(customers[["customer_id", "customer_unique_id",
                                 "customer_city", "customer_state"]],
                      on="customer_id", how="left", validate="one_to_one")
assert orders.customer_unique_id.notna().all(), "every order must resolve to a customer"
log("Orders keyed to customer_unique_id", len(orders),
    f"{orders.customer_unique_id.nunique():,} distinct customers")

# ------------------------------------------------------------- 3. order status
status_mix = orders.order_status.value_counts().to_dict()
print(f"\n  order status mix: {status_mix}\n")
cancelled = orders[orders.order_status.isin(["canceled", "unavailable"])].copy()
log("Cancelled / unavailable orders set aside", len(cancelled), "kept out of revenue analysis")

# Behaviour and revenue analysis uses DELIVERED orders only: an order that never reached the
# customer cannot be a satisfaction signal and its revenue is not realised. In-flight statuses
# (shipped/invoiced/processing/created/approved) are excluded too because their delivery
# outcome is unknown, which is the variable half this analysis turns on.
delivered = orders[orders.order_status == "delivered"].copy()
log("Delivered orders kept", len(delivered),
    f"{len(orders) - len(delivered):,} dropped (cancelled, unavailable or still in flight)")

# --------------------------------------------------------- 4. order line revenue
items = items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
items = items.merge(trans, on="product_category_name", how="left")
items["Category"] = (items.product_category_name_english
                     .fillna(items.product_category_name)
                     .fillna("unknown")
                     .str.replace("_", " ").str.strip().str.title())
n_unknown = (items.Category == "Unknown").sum()
log("Order items joined to product category", len(items),
    f"{n_unknown:,} lines with no category -> 'Unknown'")

items = items.merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")
items["LineRevenue"] = items.price + items.freight_value

items_d = items[items.order_id.isin(set(delivered.order_id))].copy()
log("Order items for delivered orders", len(items_d))

order_rev = items_d.groupby("order_id").agg(
    Items=("order_item_id", "count"),
    DistinctProducts=("product_id", "nunique"),
    DistinctSellers=("seller_id", "nunique"),
    ItemsValue=("price", "sum"),
    Freight=("freight_value", "sum"),
    OrderValue=("LineRevenue", "sum")).reset_index()
log("Order-level revenue built from order lines", len(order_rev),
    f"R$ {order_rev.OrderValue.sum():,.0f} total")

# ------------------------------------------------------------------ 5. payments
# payment_type can repeat per order (part card, part voucher). Take the type carrying the
# largest share of the order's value as the dominant method, and the max installments.
pay = payments[payments.order_id.isin(set(delivered.order_id))].copy()
dom = (pay.sort_values("payment_value", ascending=False)
       .drop_duplicates("order_id")[["order_id", "payment_type"]]
       .rename(columns={"payment_type": "PaymentType"}))
agg = pay.groupby("order_id").agg(PaymentInstallments=("payment_installments", "max"),
                                  PaymentMethods=("payment_type", "nunique")).reset_index()
pay_o = dom.merge(agg, on="order_id", how="outer")
log("Payments aggregated to one row per order", len(pay_o),
    f"{(pay_o.PaymentMethods > 1).sum():,} orders used more than one method")

# ------------------------------------------------------------------- 6. reviews
rev = reviews[reviews.order_id.isin(set(delivered.order_id))].copy()
dupe_rev = rev.order_id.duplicated().sum()
rev = (rev.sort_values("review_creation_date")
       .drop_duplicates("order_id", keep="last")[["order_id", "review_score"]]
       .rename(columns={"review_score": "ReviewScore"}))
log("Reviews reduced to one per order", len(rev), f"{dupe_rev:,} duplicate order reviews collapsed")

# ------------------------------------------------------- 7. assemble order table
o = delivered[["order_id", "customer_unique_id", "customer_state", "customer_city",
               "order_purchase_timestamp", "order_delivered_customer_date",
               "order_estimated_delivery_date"]].copy()
o = o.rename(columns={"customer_unique_id": "CustomerID", "customer_state": "State",
                      "customer_city": "City", "order_purchase_timestamp": "OrderDate"})
o = o.merge(order_rev, on="order_id", how="inner")
log("Orders joined to revenue (inner)", len(o),
    f"{len(delivered) - len(o):,} delivered orders had no order lines")

o = o.merge(pay_o, on="order_id", how="left").merge(rev, on="order_id", how="left")

o["DeliveryDays"] = (o.order_delivered_customer_date - o.OrderDate).dt.days
o["EstimatedDays"] = (o.order_estimated_delivery_date - o.OrderDate).dt.days
o["DaysVsPromise"] = (o.order_delivered_customer_date - o.order_estimated_delivery_date).dt.days
o["LateDelivery"] = o.DaysVsPromise > 0
missing_dd = o.DeliveryDays.isna().sum()
o = o[o.DeliveryDays.notna()].copy()
log("Orders with a usable delivery date", len(o), f"{missing_dd:,} dropped (no delivery timestamp)")

o["OrderMonth"] = o.OrderDate.dt.to_period("M").astype(str)
o["FreightShare"] = o.Freight / o.OrderValue

# order sequence per customer -> first vs repeat
o = o.sort_values(["CustomerID", "OrderDate"]).reset_index(drop=True)
o["OrderSeq"] = o.groupby("CustomerID").cumcount() + 1
o["IsFirstOrder"] = o.OrderSeq == 1
o["DaysSincePrevOrder"] = (o.OrderDate - o.groupby("CustomerID").OrderDate.shift()).dt.days
log("Order sequence and first/repeat flags built", len(o),
    f"{o.IsFirstOrder.sum():,} first orders, {(~o.IsFirstOrder).sum():,} repeat orders")

# ----------------------------------------------------------- 8. customer table
snapshot = o.OrderDate.max()
cust = o.groupby("CustomerID").agg(
    Orders=("order_id", "nunique"),
    TotalRevenue=("OrderValue", "sum"),
    FirstOrderDate=("OrderDate", "min"),
    LastOrderDate=("OrderDate", "max"),
    State=("State", "first"),
    City=("City", "first"),
    TotalItems=("Items", "sum"),
    AvgReviewScore=("ReviewScore", "mean"),
    LateOrders=("LateDelivery", "sum"),
    AvgDeliveryDays=("DeliveryDays", "mean")).reset_index()
cust["AOV"] = cust.TotalRevenue / cust.Orders
cust["RecencyDays"] = (snapshot - cust.LastOrderDate).dt.days
cust["TenureDays"] = (snapshot - cust.FirstOrderDate).dt.days
cust["IsRepeat"] = cust.Orders >= 2
first_val = o[o.IsFirstOrder].set_index("CustomerID").OrderValue
cust["FirstOrderValue"] = cust.CustomerID.map(first_val)

# Round the derived float columns before writing. Without this, a reduction can land one row's
# value a single bit apart between runs (observed: one customer's AOV wrote as 209.5433333333333
# on one run and 209.54333333333335 on the next), which makes the output file non-reproducible for
# no analytical benefit. Six decimal places is far more precision than any published figure uses.
for _col in ["TotalRevenue", "AOV", "AvgDeliveryDays", "AvgReviewScore", "FirstOrderValue"]:
    cust[_col] = cust[_col].round(6)
log("Customer table built", len(cust),
    f"{cust.IsRepeat.sum():,} repeat ({cust.IsRepeat.mean() * 100:.1f}%), snapshot {snapshot.date()}")

# ------------------------------------------------------------------- 9. write
o_out = o.drop(columns=["order_delivered_customer_date", "order_estimated_delivery_date"])
o_out.to_csv(OUT / "partA_orders.csv", index=False)
items_d.loc[items_d.order_id.isin(set(o.order_id)),
            ["order_id", "order_item_id", "product_id", "seller_id", "seller_state",
             "Category", "price", "freight_value", "LineRevenue"]].to_csv(
    OUT / "partA_order_items.csv", index=False)
cust.to_csv(OUT / "partA_customers.csv", index=False)
pd.DataFrame(LOG).to_csv(OUT / "partA_cleaning_log.csv", index=False)

print("\n" + "=" * 78)
print(f"  partA_orders.csv       {len(o_out):>8,} orders")
print(f"  partA_order_items.csv  {items_d.order_id.isin(set(o.order_id)).sum():>8,} lines")
print(f"  partA_customers.csv    {len(cust):>8,} customers")
print(f"  revenue                R$ {o.OrderValue.sum():>14,.2f}")
print(f"  repeat rate            {cust.IsRepeat.mean() * 100:>8.2f}%")
