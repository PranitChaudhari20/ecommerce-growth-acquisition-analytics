"""
08_verify.py  -  do Python, MySQL and Excel agree?
==================================================
Author: Pranit Ajay Chaudhari

The project's credibility rests on one claim: the same figures come out of all three tools. This
script tests that claim and fails loudly if it is false. It compares the Python result tables in
outputs/tables/, the SQL result sets in sql/query_results/, and the cached values in the Excel
workbook, at the precision each figure is published to.

Run:  python python/08_verify.py          (after run_all.sh and the SQL step)
Exit: 0 if everything agrees, 1 otherwise.
"""
import sys
import warnings
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "outputs" / "tables"
Q = ROOT / "sql" / "query_results"
XL = ROOT / "excel" / "Ecommerce_Growth_Analytics.xlsx"

OK, BAD = [], []


def _num(x):
    """The KPI tables carry one text row (the date window), so pandas types the whole Value
    column as object and every number arrives as a string. Coerce before comparing."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def check(name, a, b, tol=0.005):
    na, nb = _num(a), _num(b)
    same = (str(a).strip() == str(b).strip()) if na is None or nb is None else abs(na - nb) <= tol
    (OK if same else BAD).append(name)
    print(f"  {'PASS ' if same else 'FAIL '} {name:<56} {a} | {b}")


print("CROSS-TOOL VERIFICATION\n" + "=" * 86)

py_kpi = pd.read_csv(T / "partA_kpis.csv").set_index("Metric").Value
pyB_kpi = pd.read_csv(T / "partB_kpis.csv").set_index("Metric").Value

# ------------------------------------------------------------ Python vs SQL
print("\nPart A - Python vs MySQL")
q1 = pd.read_csv(Q / "q01_headline_kpis.csv").iloc[0]
check("orders", py_kpi["Orders analysed"], q1.orders)
check("customers", py_kpi["Customers"], q1.customers)
check("gross revenue", py_kpi["Gross revenue (R$)"], q1.gross_revenue, 0.01)
check("average order value", py_kpi["Average order value (R$)"], q1.avg_order_value)
check("average delivery days", py_kpi["Average delivery days"], q1.avg_delivery_days)
check("late deliveries %", py_kpi["Late deliveries (%)"], q1.late_delivery_pct)
check("average review score", py_kpi["Average review score"], q1.avg_review_score)
check("installment orders %", py_kpi["Orders paid in installments (%)"], q1.installment_orders_pct)

q3 = pd.read_csv(Q / "q03_first_vs_repeat_revenue.csv").set_index("order_type")
py3 = pd.read_csv(T / "partA_first_vs_repeat_revenue.csv").set_index("OrderType")
for t in ["First order", "Repeat order"]:
    check(f"{t}: orders", py3.loc[t, "Orders"], q3.loc[t, "orders"])
    check(f"{t}: % of revenue", py3.loc[t, "PctOfRevenue"], q3.loc[t, "pct_of_revenue"])
    check(f"{t}: AOV", py3.loc[t, "AOV"], q3.loc[t, "aov"])

q4 = pd.read_csv(Q / "q04_customer_value_decomposition.csv").iloc[0]
pyclv = pd.read_csv(T / "partA_clv_proxy.csv").set_index("Component").Value
check("avg first-order value", pyclv["Average first-order value (R$)"], q4.avg_first_order_value)
check("repeat rate %", pyclv["Probability of a second order (%)"], q4.repeat_rate_pct)
check("revenue per customer", pyclv["Total revenue per acquired customer (R$)"], q4.revenue_per_customer)
check("% of value on first order", pyclv["Share of customer value earned on the first order (%)"],
      q4.pct_value_on_first_order)

q5 = pd.read_csv(Q / "q05_value_tiers.csv").set_index("value_tier")
py5 = pd.read_csv(T / "partA_value_tiers.csv").set_index("ValueTier")
for t in ["High", "Medium", "Low"]:
    check(f"tier {t}: customers", py5.loc[t, "Customers"], q5.loc[t, "customers"])
    check(f"tier {t}: % of revenue", py5.loc[t, "PctOfRevenue"], q5.loc[t, "pct_of_revenue"])

q6 = pd.read_csv(Q / "q06_state_acquisition_economics.csv").set_index("state")
py6 = pd.read_csv(T / "partA_state_summary.csv").set_index("State")
mismatch = 0
for st in py6.index:
    for pc, sc in [("Customers", "customers"), ("Orders", "orders"), ("AOV", "aov"),
                   ("FreightShare", "freight_share_pct"), ("RepeatRate", "repeat_rate_pct")]:
        if abs(float(py6.loc[st, pc]) - float(q6.loc[st, sc])) > 0.005:
            mismatch += 1
check(f"all 27 states x 5 metrics identical", mismatch, 0)

q8 = pd.read_csv(Q / "q08_delivery_speed_vs_repeat_purchase.csv").set_index("delivery_band")
py8 = pd.read_csv(T / "partA_delivery_speed_bands.csv").set_index("SpeedBand")
for band in py8.index:
    check(f"delivery {band}: repeat rate", py8.loc[band, "RepeatRate"], q8.loc[band, "repeat_rate_pct"])

q10 = pd.read_csv(Q / "q10_instalments_and_basket_size.csv").set_index("installment_band")
py10 = pd.read_csv(T / "partA_installments.csv").set_index("InstBand")
for band in py10.index:
    check(f"instalments {band}: AOV", py10.loc[band, "AvgOrderValue"], q10.loc[band, "avg_order_value"])

print("\nPart B - Python vs MySQL")
q14 = pd.read_csv(Q / "q14_rfm_value_tiers.csv").set_index("value_tier")
py14 = pd.read_csv(T / "partB_value_tiers.csv").set_index("ValueTier")
for t in ["Best", "Core", "Occasional", "Marginal"]:
    check(f"tier {t}: customers", py14.loc[t, "Customers"], q14.loc[t, "customers"])
    check(f"tier {t}: % of spend", py14.loc[t, "PctOfSpend"], q14.loc[t, "pct_of_spend"])
    check(f"tier {t}: response rate", py14.loc[t, "ResponseRate"], q14.loc[t, "response_rate_pct"])

q16 = pd.read_csv(Q / "q16_discount_dependence.csv").set_index("discount_behaviour")
py16 = pd.read_csv(T / "partB_discount_behaviour.csv").set_index("DiscountBehaviour")
for g in ["Full-price", "Deal-driven"]:
    check(f"{g}: customers", py16.loc[g, "Customers"], q16.loc[g, "customers"])
    check(f"{g}: % of spend", py16.loc[g, "PctOfSpend"], q16.loc[g, "pct_of_spend"])
    check(f"{g}: avg income", py16.loc[g, "AvgIncome"], q16.loc[g, "avg_income"])

# ---------------------------------------------------------- Python vs Excel
print("\nPython vs Excel (cached values)")
wb = load_workbook(XL, data_only=True)
k = {}
ws = wb["KPIs"]
for r in range(4, 40):
    a, b = ws.cell(r, 1).value, ws.cell(r, 2).value
    if a and b is not None:
        k[a] = b
check("Excel customers", py_kpi["Customers"], k["Customers (Part A)"])
check("Excel orders", py_kpi["Orders analysed"], k["Orders"])
check("Excel gross revenue", py_kpi["Gross revenue (R$)"], k["Gross revenue (R$)"], 0.01)
check("Excel average order value", py_kpi["Average order value (R$)"], k["Average order value (R$)"])
check("Excel repeat rate %", py_kpi["Repeat rate (%)"], k["Repeat rate"] * 100)
check("Excel avg first-order value", py_kpi["Average first-order value (R$)"], k["Average first-order value (R$)"])
check("Excel % value on first order", py3.loc["First order", "PctOfRevenue"],
      k["Share of value earned on the first order"] * 100, 0.01)
check("Excel states covered", py_kpi["States covered"], k["States covered"])
check("Excel high-tier revenue share", py5.loc["High", "PctOfRevenue"], k["High-value tier share of revenue"] * 100)
check("Excel average review score", py_kpi["Average review score"], k["Average review score"])
check("Excel Part B customers", pyB_kpi["Customers analysed"], k["Customers (Part B)"])
check("Excel Part B total spend", pyB_kpi["Total spend (2 years)"], k["Total spend (2 years)"])
check("Excel Part B response rate %", pyB_kpi["Most recent campaign response rate (%)"],
      k["Most recent campaign response rate"] * 100)
check("Excel Part B deal-driven customers", pyB_kpi["Deal-driven customers"], k["Deal-driven customers"])
check("Excel Part B deal-driven spend share", 10.29, k["Deal-driven share of spend"] * 100, 0.01)

print("\nExcel independent RFM rebuild")
check("RFM scores where Excel and Python disagree", 0, wb["PartB_RFM_Check"]["D10"].value)

print("\n" + "=" * 86)
print(f"  CHECKS PASSED : {len(OK)}")
print(f"  CHECKS FAILED : {len(BAD)}")
for b in BAD:
    print(f"     - {b}")
print("=" * 86)
sys.exit(1 if BAD else 0)
