"""
05_build_charts.py  -  every chart in the documentation, generated from the result tables
=======================================================================================
Author: Pranit Ajay Chaudhari

Input : outputs/tables/*.csv   (produced by 03_analysis_partA.py and 04_analysis_partB.py)
Output: screenshots/*.png      12 charts

Design rules followed: categorical hues assigned in fixed order and never cycled; a single
y-axis on every chart (no dual axes); ordered tiers use a single-hue ordinal ramp rather than
categorical colours; a legend whenever two or more series are present; and a direct value label
on every mark, which is also the required relief for the palette slots that sit below 3:1
contrast on a light surface. The CSV tables in outputs/tables/ are the table view of every chart.

Run:  python python/05_build_charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "outputs" / "tables"
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)

# categorical slots, fixed order, never cycled
C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
# ordinal single-hue ramp, dark -> light (validated: monotone L, light end 2.06:1)
ORD4 = ["#184f95", "#2a78d6", "#5598e7", "#86b6ef"]
ORD5 = ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"

plt.rcParams.update({
    "figure.dpi": 110, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c3c2b7", "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.titlesize": 12, "axes.titleweight": "600",
    "axes.titlecolor": INK, "axes.labelcolor": INK2, "axes.labelsize": 9.5,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.frameon": False, "legend.fontsize": 9})

made = []


def save(name, note=""):
    plt.tight_layout()
    plt.savefig(SHOTS / name, bbox_inches="tight", facecolor=SURFACE)
    plt.close()
    made.append(name)
    print(f"  {name:<46} {note}")


def label_bars(ax, bars, fmt="{:,.0f}", dy=0.01, size=8.5):
    top = max([b.get_height() for b in bars]) or 1
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + top * dy,
                fmt.format(b.get_height()), ha="center", va="bottom",
                fontsize=size, color=INK2)


print("Charts\n" + "=" * 70)

# ---------------------------------------------------- 1. the headline finding
f = pd.read_csv(T / "partA_frequency_distribution.csv")
f = f[f.Orders <= 6]
fig, ax = plt.subplots(figsize=(7.4, 4.1))
b = ax.bar(f.Orders.astype(str), f.PctOfCustomers, color=C1, width=0.62)
label_bars(ax, b, "{:,.2f}%")
ax.set_title("97% of marketplace customers order exactly once\nOlist, 93,350 customers, Sep 2016 – Aug 2018")
ax.set_xlabel("Orders placed by the customer"); ax.set_ylabel("Share of customers (%)")
ax.set_ylim(0, 108)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
save("01_order_frequency.png", "Part A - the central finding")

# ------------------------------------------- 2. first vs repeat revenue share
s = pd.read_csv(T / "partA_first_vs_repeat_revenue.csv").set_index("OrderType").reindex(["First order", "Repeat order"])
fig, ax = plt.subplots(figsize=(7.0, 2.9))
left = 0
for (name, row), col in zip(s.iterrows(), [C1, C2]):
    ax.barh([""], [row.PctOfRevenue], left=left, color=col, height=0.5, label=name)
    # A label only sits inside its segment when the segment is wide enough to hold it;
    # otherwise it goes above the bar in ink, so it is never clipped by the plot edge.
    if row.PctOfRevenue >= 12:
        ax.text(left + row.PctOfRevenue / 2, 0, f"{row.PctOfRevenue:.2f}%", ha="center",
                va="center", color="white", fontsize=11, fontweight="600")
    else:
        ax.annotate(f"{row.PctOfRevenue:.2f}%", (left + row.PctOfRevenue / 2, 0.27),
                    ha="center", va="bottom", fontsize=10, fontweight="600", color=INK)
    left += row.PctOfRevenue + 0.35          # 2px-equivalent surface gap between fills
ax.set_xlim(0, 103); ax.set_ylim(-0.5, 0.62); ax.set_yticks([]); ax.grid(False)
ax.set_title("Repeat orders contribute 2.97% of revenue\nR$ 15.42M across 96,470 delivered orders", pad=14)
ax.set_xlabel("Share of gross revenue (%)", labelpad=8)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.52), ncol=2)
fig.subplots_adjust(bottom=0.42)
save("02_first_vs_repeat_revenue.png", "Part A")

# ------------------------------------------- 3. where customer value comes from
clv = pd.read_csv(T / "partA_clv_proxy.csv").set_index("Component").Value
first_v = clv["Average first-order value (R$)"]
ret_v = clv["Retention contribution per acquired customer (R$)"]
fig, ax = plt.subplots(figsize=(6.4, 4.0))
b = ax.bar(["First order", "All later orders"], [first_v, ret_v], color=[C1, C2], width=0.5)
label_bars(ax, b, "R$ {:,.2f}")
ax.set_title("A customer is worth R$ 165.17, and R$ 160.26 of it\narrives on the first order")
ax.set_ylabel("Revenue per acquired customer (R$)")
ax.set_ylim(0, first_v * 1.18)
save("03_customer_value_decomposition.png", "Part A")

# ------------------------------------------------------ 4. retention curve
cur = pd.read_csv(T / "partA_retention_curve.csv")
cur = cur[cur.MonthsSinceFirstOrder.between(1, 11)]
fig, ax = plt.subplots(figsize=(7.4, 3.9))
ax.plot(cur.MonthsSinceFirstOrder, cur.WeightedRetentionPct, color=C1, linewidth=2,
        marker="o", markersize=8, markerfacecolor=C1, markeredgecolor=SURFACE, markeredgewidth=2)
for _, r_ in cur.iterrows():
    ax.annotate(f"{r_.WeightedRetentionPct:.2f}%", (r_.MonthsSinceFirstOrder, r_.WeightedRetentionPct),
                textcoords="offset points", xytext=(0, 11), ha="center", fontsize=8.5, color=INK2)
ax.set_title("Retention never recovers: 0.48% of customers order again\nin month 1, then roughly 0.2% a month")
ax.set_xlabel("Months since first order"); ax.set_ylabel("Customers still ordering (%)")
ax.set_ylim(0, 0.75); ax.set_xticks(range(1, 12))
save("04_retention_curve.png", "Part A - customer-weighted")

# -------------------------------------------- 5. monthly new vs returning
m = pd.read_csv(T / "partA_monthly.csv")
m = m[(m.OrderMonth >= "2017-01") & (m.OrderMonth <= "2018-08")]
fig, ax = plt.subplots(figsize=(8.6, 4.0))
x = np.arange(len(m))
ax.bar(x, m.NewCustomers, color=C1, width=0.66, label="New customers")
ax.bar(x, m.ReturningCustomers, bottom=m.NewCustomers + 25, color=C2, width=0.66, label="Returning customers")
ax.set_xticks(x); ax.set_xticklabels(m.OrderMonth, rotation=60, ha="right", fontsize=8)
ax.set_title("Monthly actives are almost entirely new customers\n98.1% of active customers each month are first-time buyers")
ax.set_ylabel("Active customers")
ax.legend(loc="upper left")
save("05_new_vs_returning.png", "Part A")

# ------------------------------------------------- 6. state acquisition economics
st = pd.read_csv(T / "partA_state_summary.csv").head(12)
fig, (axl, axr) = plt.subplots(1, 2, figsize=(10.6, 4.3), sharey=True)
y = np.arange(len(st))[::-1]
b1 = axl.barh(y, st.AOV, color=C1, height=0.62)
for yy, v in zip(y, st.AOV):
    axl.text(v + 2, yy, f"{v:,.0f}", va="center", fontsize=8.5, color=INK2)
axl.set_yticks(y); axl.set_yticklabels(st.State); axl.set_xlabel("Average order value (R$)")
axl.set_title("Average order value", fontsize=11); axl.set_xlim(0, st.AOV.max() * 1.18)
b2 = axr.barh(y, st.FreightShare, color=C2, height=0.62)
for yy, v in zip(y, st.FreightShare):
    axr.text(v + 0.25, yy, f"{v:.1f}%", va="center", fontsize=8.5, color=INK2)
axr.set_xlabel("Freight as a share of revenue (%)"); axr.set_title("Delivery cost burden", fontsize=11)
axr.set_xlim(0, st.FreightShare.max() * 1.22)
fig.suptitle("Distant states order more per basket but cost more to serve\nTop 12 Brazilian states by revenue",
             fontsize=12, fontweight="600", color=INK, y=1.04)
save("06_state_economics.png", "Part A - two panels, one scale each")

# ------------------------------------- 7. delivery speed vs repeat (the null result)
sp = pd.read_csv(T / "partA_delivery_speed_bands.csv")
fig, ax = plt.subplots(figsize=(7.6, 4.0))
b = ax.bar(sp.SpeedBand, sp.RepeatRate, color=C1, width=0.6)
label_bars(ax, b, "{:.2f}%")
base = pd.read_csv(T / "partA_kpis.csv").set_index("Metric").Value["Repeat rate (%)"]
ax.axhline(float(base), color=INK2, linestyle="--", linewidth=1.2)
ax.text(len(sp) - 0.45, float(base) + 0.06, f"overall {float(base):.2f}%", ha="right", fontsize=8.5, color=INK2)
ax.set_title("Faster delivery does not produce repeat customers\nRepeat rate stays within half a point across every delivery-speed band")
ax.set_xlabel("Delivery time on the first order"); ax.set_ylabel("Customers who ordered again (%)")
ax.set_ylim(0, 4.1)
save("07_delivery_vs_repeat.png", "Part A - honest null result")

# ------------------------------------------------ 8. installments vs order value
ins = pd.read_csv(T / "partA_installments.csv")
fig, ax = plt.subplots(figsize=(7.6, 4.0))
b = ax.bar(ins.InstBand, ins.AvgOrderValue, color=ORD5[::-1][:len(ins)], width=0.6)
label_bars(ax, b, "R$ {:,.0f}")
ax.set_title("Instalment plans carry the large baskets\nAverage order value rises 3.4× from single payment to 13+ instalments")
ax.set_xlabel("Instalments on the order"); ax.set_ylabel("Average order value (R$)")
ax.set_ylim(0, ins.AvgOrderValue.max() * 1.16)
save("08_installments_vs_value.png", "Part A")

# ============================================================== PART B
# --------------------------------- 9. value tiers: customers vs spend vs response
tb = pd.read_csv(T / "partB_value_tiers.csv")
fig, ax = plt.subplots(figsize=(8.4, 4.3))
x = np.arange(len(tb)); w = 0.26
b1 = ax.bar(x - w - 0.012, tb.PctOfCustomers, w, color=C1, label="Share of customers (%)")
b2 = ax.bar(x, tb.PctOfSpend, w, color=C2, label="Share of spend (%)")
b3 = ax.bar(x + w + 0.012, tb.ResponseRate, w, color=C3, label="Campaign response rate (%)")
for bars in (b1, b2, b3):
    label_bars(ax, bars, "{:.1f}", size=8)
ax.set_xticks(x); ax.set_xticklabels(tb.ValueTier)
ax.set_title("The Best tier is 14.8% of customers, 32.0% of spend and responds 8× more often than the Marginal tier\nRFM value tiers, 2,026 customers")
ax.set_xlabel("RFM value tier"); ax.set_ylabel("Percent")
ax.set_ylim(0, 58); ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.17))
save("09_value_tiers.png", "Part B - 3 series, slots 1-3")

# ------------------------------------------- 10. campaign response by tier
ct = pd.read_csv(T / "partB_campaign_by_tier.csv")
camps = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
fig, ax = plt.subplots(figsize=(9.0, 4.4))
x = np.arange(len(ct)); w = 0.155
for i, (col, colour) in enumerate(zip(camps, [C1, C2, C3, C4, C5])):
    off = (i - 2) * (w + 0.012)
    bars = ax.bar(x + off, ct[col], w, color=colour, label=f"Campaign {col[-1]}")
    for b_ in bars:
        if b_.get_height() > 0:
            ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height() + 0.3, f"{b_.get_height():.1f}",
                    ha="center", fontsize=7.2, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(ct.ValueTier)
ax.set_title("Campaign 3 is the only campaign that reaches lower tiers\nThe Marginal tier accepted campaigns 1 and 5 zero times")
ax.set_xlabel("RFM value tier"); ax.set_ylabel("Accepted the campaign (%)")
ax.set_ylim(0, 26); ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.16))
save("10_campaign_by_tier.png", "Part B - 5 series, adjacent pairlist")

# ------------------------------------------------- 11. discount dependence
db = pd.read_csv(T / "partB_discount_behaviour.csv").set_index("DiscountBehaviour")
db = db.reindex(["Full-price", "Deal-driven"])
metrics = [("PctOfCustomers", "Share of\ncustomers (%)"), ("PctOfSpend", "Share of\nspend (%)"),
           ("AvgSpendPerPurchase", "Spend per\npurchase (R$)")]
fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.9))
for axx, (col, lab) in zip(axes, metrics):
    bars = axx.bar(db.index, db[col], color=[C1, C2], width=0.52)
    label_bars(axx, bars, "{:,.2f}" if col == "AvgSpendPerPurchase" else "{:.2f}", size=9)
    axx.set_title(lab, fontsize=10.5); axx.set_ylim(0, db[col].max() * 1.2)
    axx.tick_params(axis="x", labelsize=9)
fig.suptitle("Deal-driven customers are a third of the base and a tenth of the spend\n694 customers making 25%+ of their purchases on a deal",
             fontsize=12, fontweight="600", color=INK, y=1.07)
save("11_discount_dependence.png", "Part B - small multiples, one scale each")

# -------------------------------------------- 12. income band vs response
dm = pd.read_csv(T / "partB_demographics.csv")
inc = dm[dm.Dimension == "Income"].copy()
order = ["Under 25k", "25-45k", "45-65k", "65-85k", "85k+"]
inc = inc.set_index("Group").reindex(order).reset_index()
fig, ax = plt.subplots(figsize=(7.8, 4.1))
b = ax.bar(inc.Group, inc.ResponseRate, color=ORD5[::-1], width=0.58)
label_bars(ax, b, "{:.2f}%")
ax.set_title("Campaign response is driven by income more than anything else\n46.2% of customers earning 85k+ responded, against 11.4% under 25k")
ax.set_xlabel("Household income band"); ax.set_ylabel("Responded to the most recent campaign (%)")
ax.set_ylim(0, 54)
save("12_income_vs_response.png", "Part B - ordinal ramp")

print("=" * 70)
print(f"  {len(made)} charts written to screenshots/")
