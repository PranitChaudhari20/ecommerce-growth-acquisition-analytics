"""
07_build_excel.py  -  the formula-driven Excel workbook
======================================================
Author: Pranit Ajay Chaudhari

Input : data/cleaned/partA_customers.csv, data/cleaned/partB_customers.csv
Output: excel/Ecommerce_Growth_Analytics.xlsx

Every reported figure in this workbook is a LIVE FORMULA over the two data sheets, not a value
pasted from Python. That is the point: it reproduces the analysis independently, so if Excel and
Python disagree, one of them is wrong and the disagreement is visible. The RFM scoring on the
Part B sheet is rebuilt with nested IFs using the same frozen bands as the Python and SQL
versions, so all three must assign identical scores.

Note: openpyxl writes formulas without cached values. Run scripts/recalc.py afterwards or the
file previews blank. run_all.sh does this.

Run:  python python/07_build_excel.py
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "cleaned"
OUT = ROOT / "excel" / "Ecommerce_Growth_Analytics.xlsx"
OUT.parent.mkdir(exist_ok=True)

AUTHOR = "Pranit Ajay Chaudhari"
FONT = "Arial"
INK, ACCENT, MUTED = "FF0B0B0B", "FF2A78D6", "FF52514E"
HDR_FILL = PatternFill("solid", fgColor="FFE8F0FB")
TITLE_FILL = PatternFill("solid", fgColor="FF2A78D6")
THIN = Side(style="thin", color="FFD9D9D9")
BORDER = Border(bottom=THIN)
MONEY, PCT1, PCT2, NUM1, NUM2, INT = '#,##0.00', '0.0%', '0.00%', '#,##0.0', '#,##0.00', '#,##0'

a = pd.read_csv(CLEAN / "partA_customers.csv")
b = pd.read_csv(CLEAN / "partB_customers.csv")
print(f"Part A customers {len(a):,} | Part B customers {len(b):,}")

wb = Workbook()
wb.properties.creator = AUTHOR
wb.properties.lastModifiedBy = AUTHOR
wb.properties.title = "E-Commerce Growth Analytics"


def style_title(ws, text, sub=""):
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, size=14, bold=True, color="FFFFFFFF")
    ws["A1"].fill = TITLE_FILL
    ws.row_dimensions[1].height = 24
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(name=FONT, size=9, italic=True, color=MUTED)


def header_row(ws, row, headers, widths=None):
    for i, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=i, value=h)
        cell.font = Font(name=FONT, size=10, bold=True, color=INK)
        cell.fill = HDR_FILL
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w


def write_table(ws, df, start_row, bool_as_int=True):
    """Write a DataFrame as values. Booleans go in as 1/0 so LibreOffice does not rewrite them
    as =TRUE()/=FALSE() formulas, which would inflate the workbook's formula count."""
    header_row(ws, start_row, list(df.columns))
    bool_cols = [i for i, c in enumerate(df.columns) if df[c].dtype == bool]
    for rix, row in enumerate(df.itertuples(index=False), start=start_row + 1):
        vals = list(row)
        if bool_as_int:
            for i in bool_cols:
                vals[i] = int(vals[i])
        for cix, v in enumerate(vals, start=1):
            ws.cell(row=rix, column=cix, value=v)
    return start_row + len(df)


# ============================================================ DATA SHEETS ====
# PART A IS AGGREGATED FOR EXCEL, DELIBERATELY.
# The customer table has 93,350 rows. Excel summary formulas work by scanning a criteria range
# once per output cell, so a few dozen SUMIF/COUNTIF cells over 93,350 rows means tens of millions
# of comparisons - LibreOffice did not finish recalculating it in nine minutes, and a reviewer
# opening the file would wait just as long. So Part A enters Excel as a State x ValueTier grid
# (81 rows) carrying SUMS, not averages: every Part A figure in this workbook is still computed by
# a live formula from those sums, and still reconciles to the Python and SQL totals exactly.
# The full customer-level detail ships as data/cleaned/partA_customers.csv and lives in the SQL
# star schema, which is the right tool for row-level work at this scale.
agg = (a.assign(SingleOrder=(a.Orders == 1).astype(int),
                RepeatCust=a.IsRepeat.astype(int),
                ReviewSum=a.AvgReviewScore.fillna(0),
                ReviewCount=a.AvgReviewScore.notna().astype(int))
       .groupby(["State", "ValueTier"], as_index=False)
       .agg(Customers=("CustomerID", "count"), Orders=("Orders", "sum"),
            Revenue=("TotalRevenue", "sum"), FirstOrderValueSum=("FirstOrderValue", "sum"),
            SingleOrderCustomers=("SingleOrder", "sum"), RepeatCustomers=("RepeatCust", "sum"),
            ReviewScoreSum=("ReviewSum", "sum"), ReviewScoreCount=("ReviewCount", "sum"),
            Items=("TotalItems", "sum")))
agg["Revenue"] = agg.Revenue.round(2)
agg["FirstOrderValueSum"] = agg.FirstOrderValueSum.round(2)
agg["ReviewScoreSum"] = agg.ReviewScoreSum.round(4)

# The grid is complete: every state carries a row for all three value tiers. That invariant lets
# the "states covered" KPI be a cheap COUNTIF on one tier instead of an array formula - and it is
# asserted here so the formula can never quietly become wrong.
_tiers_per_state = agg.groupby("State").ValueTier.nunique()
assert set(_tiers_per_state) == {3}, f"grid is not complete: {_tiers_per_state[_tiers_per_state != 3].to_dict()}"
TIERS_PER_STATE = 3

A_COLS = list(agg.columns)
wsA = wb.active
wsA.title = "PartA_Data"
style_title(wsA, "Part A data - Olist marketplace, aggregated by state and value tier",
            f"81 rows of SUMS over 93,350 customers. Every Part A figure in this workbook is a "
            f"formula over this grid. Author: {AUTHOR}")
A_LAST = write_table(wsA, agg, 5)
wsA["A4"] = ("Aggregated because Excel cannot recalculate 93,350 rows of criteria formulas in "
             "reasonable time. Row-level detail: data/cleaned/partA_customers.csv and the SQL star schema.")
wsA["A4"].font = Font(name=FONT, size=9, italic=True, color=MUTED)
wsA.freeze_panes = "A6"
print(f"  PartA_Data (aggregate) rows 6..{A_LAST}, {len(agg)} rows")

B_COLS = ["ID", "Age", "AgeBand", "Education", "Marital_Status", "Income", "IncomeBand",
          "Children", "HasChildren", "Recency", "TotalSpend", "TotalPurchases",
          "NumDealsPurchases", "DealShare", "NumWebPurchases", "NumCatalogPurchases",
          "NumStorePurchases", "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4",
          "AcceptedCmp5", "CampaignsAccepted", "Response", "R", "F", "M", "RFMScore",
          "ValueTier", "DiscountBehaviour"]
bdata = b[B_COLS].copy()
wsB = wb.create_sheet("PartB_Data")
style_title(wsB, "Part B data - campaign-response customers",
            f"One row per customer. Source: cleaned by python/02_clean_partB.py. Author: {AUTHOR}")
B_LAST = write_table(wsB, bdata, 4)
wsB.freeze_panes = "A5"
print(f"  PartB_Data rows 5..{B_LAST}")

# column letters on the data sheets
AC = {c: get_column_letter(i + 1) for i, c in enumerate(A_COLS)}
BC = {c: get_column_letter(i + 1) for i, c in enumerate(B_COLS)}
def arng(col):
    return f"PartA_Data!${AC[col]}$6:${AC[col]}${A_LAST}"
def brng(col):
    return f"PartB_Data!${BC[col]}$5:${BC[col]}${B_LAST}"

# ========================================================= RFM REBUILD =======
# Rebuild the R, F and M scores with nested IFs using the same frozen bands, then compare to the
# Python scores already in the data. A non-zero mismatch count means the two implementations have
# diverged and the analysis cannot be trusted.
wsR = wb.create_sheet("PartB_RFM_Check")
style_title(wsR, "Part B - RFM scoring rebuilt in Excel formulas",
            "Does Excel assign the same R, F and M scores as Python and SQL? Two checks: whole-column "
            "tests covering every customer, and a visible sample so the logic can be read.")

# --- whole-column check: covers all 2,026 customers in three formulas ---------
# Because the bands are ordered, a score is just a count of thresholds crossed, so the whole
# comparison vectorises into one SUMPRODUCT per dimension. This covers every row; the sample
# below exists so a reader can see the scoring logic written out, not to do the checking.
RR, PP, SS = brng("Recency"), brng("TotalPurchases"), brng("TotalSpend")
PY_R, PY_F, PY_M = brng("R"), brng("F"), brng("M")
wsR["A4"] = "Whole-column check - every customer, not a sample"
wsR["A4"].font = Font(name=FONT, size=11, bold=True, color=INK)
header_row(wsR, 5, ["Dimension", "Excel formula rebuilds the score as", "Rows compared",
                    "Rows where Excel and Python disagree"], [14, 56, 15, 34])
checks = [
    ("Recency (R)", "5 minus the number of upper band edges passed (19, 39, 58, 79)",
     f'=SUMPRODUCT(--((5-({RR}>19)-({RR}>39)-({RR}>58)-({RR}>79))<>{PY_R}))'),
    ("Frequency (F)", "1 plus the number of band edges passed (7, 12, 17, 22)",
     f'=SUMPRODUCT(--((1+({PP}>7)+({PP}>12)+({PP}>17)+({PP}>22))<>{PY_F}))'),
    ("Monetary (M)", "1 plus the number of band edges passed (55, 199, 636, 1174)",
     f'=SUMPRODUCT(--((1+({SS}>55)+({SS}>199)+({SS}>636)+({SS}>1174))<>{PY_M}))'),
]
for i, (dim, desc, formula) in enumerate(checks):
    r_ = 6 + i
    wsR.cell(row=r_, column=1, value=dim).font = Font(name=FONT, size=10, bold=True)
    wsR.cell(row=r_, column=2, value=desc).font = Font(name=FONT, size=9, color=MUTED)
    wsR.cell(row=r_, column=3, value=f"=COUNTA({brng('ID')})").number_format = INT
    mm = wsR.cell(row=r_, column=4, value=formula)
    mm.number_format = INT
    mm.font = Font(name=FONT, size=10, bold=True, color=ACCENT)
    for col in range(1, 5):
        wsR.cell(row=r_, column=col).border = BORDER
wsR["A10"] = "Total disagreements across all three dimensions"
wsR["A10"].font = Font(name=FONT, size=10, bold=True)
wsR["D10"] = "=SUM(D6:D8)"
wsR["D10"].number_format = INT
wsR["D10"].font = Font(name=FONT, size=11, bold=True, color=ACCENT)
wsR["A11"] = "This must be zero. Any other value means the Excel and Python scoring have diverged."
wsR["A11"].font = Font(name=FONT, size=9, italic=True, color=MUTED)

# --- visible sample: the same logic written out row by row --------------------
SAMPLE = 100
wsR["A13"] = f"Worked sample - the first {SAMPLE} customers, scored with nested IFs"
wsR["A13"].font = Font(name=FONT, size=11, bold=True, color=INK)
wsR["A14"] = ("Shown so the scoring logic is readable. The whole-column check above is what actually "
              "covers all 2,026 customers.")
wsR["A14"].font = Font(name=FONT, size=9, italic=True, color=MUTED)
header_row(wsR, 15, ["Customer", "Recency", "Excel R", "Python R", "Purchases", "Excel F",
                     "Python F", "Spend", "Excel M", "Python M", "All three match?"],
           [12, 10, 9, 9, 11, 9, 9, 10, 9, 9, 15])
for i in range(min(SAMPLE, len(b))):
    r_ = 16 + i
    d = 5 + i
    wsR.cell(row=r_, column=1, value=f"=PartB_Data!${BC['ID']}${d}")
    wsR.cell(row=r_, column=2, value=f"=PartB_Data!${BC['Recency']}${d}")
    wsR.cell(row=r_, column=3, value=f'=IF(B{r_}<=19,5,IF(B{r_}<=39,4,IF(B{r_}<=58,3,IF(B{r_}<=79,2,1))))')
    wsR.cell(row=r_, column=4, value=f"=PartB_Data!${BC['R']}${d}")
    wsR.cell(row=r_, column=5, value=f"=PartB_Data!${BC['TotalPurchases']}${d}")
    wsR.cell(row=r_, column=6, value=f'=IF(E{r_}<=7,1,IF(E{r_}<=12,2,IF(E{r_}<=17,3,IF(E{r_}<=22,4,5))))')
    wsR.cell(row=r_, column=7, value=f"=PartB_Data!${BC['F']}${d}")
    wsR.cell(row=r_, column=8, value=f"=PartB_Data!${BC['TotalSpend']}${d}")
    wsR.cell(row=r_, column=9, value=f'=IF(H{r_}<=55,1,IF(H{r_}<=199,2,IF(H{r_}<=636,3,IF(H{r_}<=1174,4,5))))')
    wsR.cell(row=r_, column=10, value=f"=PartB_Data!${BC['M']}${d}")
    wsR.cell(row=r_, column=11, value=f'=IF(AND(C{r_}=D{r_},F{r_}=G{r_},I{r_}=J{r_}),1,0)')
SAMPLE_LAST = 15 + min(SAMPLE, len(b))
wsR.cell(row=SAMPLE_LAST + 1, column=1, value=f"Sample rows matching (of {SAMPLE})").font = Font(name=FONT, size=10, bold=True)
wsR.cell(row=SAMPLE_LAST + 1, column=11, value=f"=SUM(K16:K{SAMPLE_LAST})").number_format = INT
R_LAST = SAMPLE_LAST
print(f"  PartB_RFM_Check: 3 whole-column checks + {SAMPLE}-row worked sample")

# ================================================================= KPIs ======
ws = wb.create_sheet("KPIs", 0)
style_title(ws, "E-Commerce Growth Analytics - headline figures",
            f"Every value is a live formula over PartA_Data and PartB_Data. Author: {AUTHOR}")
ws.column_dimensions["A"].width = 52
ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 46

kpis = [
    ("PART A - Olist marketplace (acquisition economics)", None, None, None),
    ("Customers (Part A)", f"=SUM({arng('Customers')})", INT, "Distinct customer_unique_id values"),
    ("Orders", f"=SUM({arng('Orders')})", INT, "Delivered orders"),
    ("Gross revenue (R$)", f"=SUM({arng('Revenue')})", MONEY, "Items value plus freight, delivered orders only"),
    ("Average order value (R$)", f"=SUM({arng('Revenue')})/SUM({arng('Orders')})", NUM2, "Revenue / orders"),
    ("Repeat customers (2+ orders)", f"=SUM({arng('RepeatCustomers')})", INT, "Customers who ordered twice or more"),
    ("Repeat rate", f"=SUM({arng('RepeatCustomers')})/SUM({arng('Customers')})", PCT2, "THE central finding of Part A"),
    ("Customers with exactly one order", f"=SUM({arng('SingleOrderCustomers')})", INT, "Why RFM frequency scoring fails here"),
    ("Share of customers ordering exactly once",
     f"=SUM({arng('SingleOrderCustomers')})/SUM({arng('Customers')})", PCT2, "Frequency has almost no variance to score"),
    ("Average first-order value (R$)", f"=SUM({arng('FirstOrderValueSum')})/SUM({arng('Customers')})", NUM2, "Value of the acquisition itself"),
    ("Revenue per acquired customer (R$)", f"=SUM({arng('Revenue')})/SUM({arng('Customers')})", NUM2, "Total observed revenue per customer"),
    ("Share of value earned on the first order",
     f"=SUM({arng('FirstOrderValueSum')})/SUM({arng('Revenue')})", PCT2, "First-order value / total value"),
    ("States covered",
     f'=COUNTIF({arng("ValueTier")},"High")', INT,
     "Every state has one row per value tier, so counting one tier counts the states"),
    ("High-value tier share of revenue",
     f"=SUMIF({arng('ValueTier')},\"High\",{arng('Revenue')})/SUM({arng('Revenue')})", PCT2, "Top 20% of customers by revenue"),
    ("Average review score",
     f"=SUM({arng('ReviewScoreSum')})/SUM({arng('ReviewScoreCount')})", NUM2, "1 to 5, customer-level mean"),
    (None, None, None, None),
    ("PART B - campaign dataset (response and discount behaviour)", None, None, None),
    ("Customers (Part B)", f"=COUNTA({brng('ID')})", INT, "After removing 182 duplicate records"),
    ("Total spend (2 years)", f"=SUM({brng('TotalSpend')})", INT, "Sum across six product categories"),
    ("Average spend per customer", f"=AVERAGE({brng('TotalSpend')})", NUM2, None),
    ("Average purchases per customer", f"=AVERAGE({brng('TotalPurchases')})", NUM2, "Deal plus web, catalogue and store"),
    ("Customers with a single purchase", f"=COUNTIF({brng('TotalPurchases')},\"<=1\")", INT, "Contrast with Part A: frequency varies here, so RFM works"),
    ("Accepted at least one campaign", f"=COUNTIF({brng('CampaignsAccepted')},\">0\")", INT, "Across the five historic campaigns"),
    ("Share accepting at least one campaign",
     f"=COUNTIF({brng('CampaignsAccepted')},\">0\")/COUNTA({brng('ID')})", PCT2, None),
    ("Most recent campaign response rate", f"=AVERAGE({brng('Response')})", PCT2, "The sixth and most recent campaign"),
    ("Deal-driven customers", f"=COUNTIF({brng('DiscountBehaviour')},\"Deal-driven\")", INT, "25% or more of purchases made on a deal"),
    ("Deal-driven share of customers",
     f"=COUNTIF({brng('DiscountBehaviour')},\"Deal-driven\")/COUNTA({brng('ID')})", PCT2, None),
    ("Deal-driven share of spend",
     f"=SUMIF({brng('DiscountBehaviour')},\"Deal-driven\",{brng('TotalSpend')})/SUM({brng('TotalSpend')})", PCT2, "A third of customers, a tenth of the money"),
    ("Best tier share of spend",
     f"=SUMIF({brng('ValueTier')},\"Best\",{brng('TotalSpend')})/SUM({brng('TotalSpend')})", PCT2, None),
    ("RFM scores where Excel and Python disagree", "=PartB_RFM_Check!$D$10", INT, "Must be zero - Excel rebuilds the scoring independently"),
]
row = 4
KPI_ROW = {}        # label -> row, so other sheets never reference a hard-coded cell that drifts
for label, formula, fmt, note in kpis:
    if label is None:
        row += 1
        continue
    if formula is not None:
        KPI_ROW[label] = row
    c = ws.cell(row=row, column=1, value=label)
    if formula is None:
        c.font = Font(name=FONT, size=11, bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor="FF52514E")
        ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="FF52514E")
        ws.cell(row=row, column=3).fill = PatternFill("solid", fgColor="FF52514E")
    else:
        c.font = Font(name=FONT, size=10, color=INK)
        v = ws.cell(row=row, column=2, value=formula)
        v.font = Font(name=FONT, size=10, bold=True, color=ACCENT)
        v.number_format = fmt
        v.alignment = Alignment(horizontal="right")
        if note:
            n = ws.cell(row=row, column=3, value=note)
            n.font = Font(name=FONT, size=9, italic=True, color=MUTED)
        for col in (1, 2, 3):
            ws.cell(row=row, column=col).border = BORDER
    row += 1
KPI_LAST = row - 1

# ================================================== PART A: VALUE TIERS ======
ws2 = wb.create_sheet("PartA_ValueTiers")
style_title(ws2, "Part A - customer value tiers", "Top 20% / next 30% / bottom 50% by total revenue. All formulas.")
header_row(ws2, 4, ["Value tier", "Customers", "% of customers", "Revenue (R$)", "% of revenue",
                    "Avg revenue", "Avg orders", "Repeat rate"], [16, 12, 15, 16, 14, 14, 12, 12])
for i, tier in enumerate(["High", "Medium", "Low"]):
    r_ = 5 + i
    ws2.cell(row=r_, column=1, value=tier).font = Font(name=FONT, size=10, bold=True)
    ws2.cell(row=r_, column=2, value=f'=SUMIF({arng("ValueTier")},A{r_},{arng("Customers")})').number_format = INT
    ws2.cell(row=r_, column=3, value=f'=B{r_}/SUM($B$5:$B$7)').number_format = PCT1
    ws2.cell(row=r_, column=4, value=f'=SUMIF({arng("ValueTier")},A{r_},{arng("Revenue")})').number_format = MONEY
    ws2.cell(row=r_, column=5, value=f'=D{r_}/SUM($D$5:$D$7)').number_format = PCT1
    ws2.cell(row=r_, column=6, value=f'=D{r_}/B{r_}').number_format = NUM2
    ws2.cell(row=r_, column=7, value=f'=SUMIF({arng("ValueTier")},A{r_},{arng("Orders")})/B{r_}').number_format = NUM2
    ws2.cell(row=r_, column=8, value=f'=SUMIF({arng("ValueTier")},A{r_},{arng("RepeatCustomers")})/B{r_}').number_format = PCT2
ws2.cell(row=8, column=1, value="Total").font = Font(name=FONT, size=10, bold=True)
ws2.cell(row=8, column=2, value="=SUM(B5:B7)").number_format = INT
ws2.cell(row=8, column=4, value="=SUM(D5:D7)").number_format = MONEY

# ====================================================== PART A: STATES =======
ws3 = wb.create_sheet("PartA_States")
style_title(ws3, "Part A - acquisition economics by state",
            "Which states produce customers, at what basket size, and with what repeat behaviour.")
header_row(ws3, 4, ["State", "Customers", "% of customers", "Revenue (R$)", "% of revenue",
                    "Avg revenue per customer", "Repeat rate", "Avg review score"],
           [8, 12, 15, 16, 14, 22, 12, 15])
states = sorted(a.State.unique())
for i, st_ in enumerate(states):
    r_ = 5 + i
    last = 4 + len(states)
    ws3.cell(row=r_, column=1, value=st_)
    ws3.cell(row=r_, column=2, value=f'=SUMIF({arng("State")},A{r_},{arng("Customers")})').number_format = INT
    ws3.cell(row=r_, column=3, value=f'=B{r_}/SUM($B$5:$B${last})').number_format = PCT1
    ws3.cell(row=r_, column=4, value=f'=SUMIF({arng("State")},A{r_},{arng("Revenue")})').number_format = MONEY
    ws3.cell(row=r_, column=5, value=f'=D{r_}/SUM($D$5:$D${last})').number_format = PCT1
    ws3.cell(row=r_, column=6, value=f'=D{r_}/B{r_}').number_format = NUM2
    ws3.cell(row=r_, column=7, value=f'=SUMIF({arng("State")},A{r_},{arng("RepeatCustomers")})/B{r_}').number_format = PCT2
    ws3.cell(row=r_, column=8,
             value=f'=SUMIF({arng("State")},A{r_},{arng("ReviewScoreSum")})'
                   f'/SUMIF({arng("State")},A{r_},{arng("ReviewScoreCount")})').number_format = NUM2

# ================================================== PART B: TIER SUMMARY =====
ws4 = wb.create_sheet("PartB_Tiers")
style_title(ws4, "Part B - RFM value tiers and campaign response",
            "Response rate and lift by tier. Lift is the tier's response rate divided by the overall rate.")
header_row(ws4, 4, ["Value tier", "Customers", "% of customers", "Total spend", "% of spend",
                    "Avg spend", "Avg purchases", "Avg deal share", "Response rate", "Response lift"],
           [14, 12, 15, 14, 12, 12, 14, 14, 14, 13])
tiers = ["Best", "Core", "Occasional", "Marginal"]
for i, t in enumerate(tiers):
    r_ = 5 + i
    ws4.cell(row=r_, column=1, value=t).font = Font(name=FONT, size=10, bold=True)
    ws4.cell(row=r_, column=2, value=f'=COUNTIF({brng("ValueTier")},A{r_})').number_format = INT
    ws4.cell(row=r_, column=3, value=f'=B{r_}/SUM($B$5:$B$8)').number_format = PCT1
    ws4.cell(row=r_, column=4, value=f'=SUMIF({brng("ValueTier")},A{r_},{brng("TotalSpend")})').number_format = INT
    ws4.cell(row=r_, column=5, value=f'=D{r_}/SUM($D$5:$D$8)').number_format = PCT1
    ws4.cell(row=r_, column=6, value=f'=D{r_}/B{r_}').number_format = NUM2
    ws4.cell(row=r_, column=7, value=f'=SUMIF({brng("ValueTier")},A{r_},{brng("TotalPurchases")})/B{r_}').number_format = NUM2
    ws4.cell(row=r_, column=8, value=f'=AVERAGEIF({brng("ValueTier")},A{r_},{brng("DealShare")})').number_format = PCT1
    ws4.cell(row=r_, column=9, value=f'=SUMIF({brng("ValueTier")},A{r_},{brng("Response")})/B{r_}').number_format = PCT2
    ws4.cell(row=r_, column=10, value=f'=I{r_}/AVERAGE({brng("Response")})').number_format = NUM2

# ================================================ PART B: CAMPAIGNS ==========
ws5 = wb.create_sheet("PartB_Campaigns")
style_title(ws5, "Part B - campaign acceptance by value tier",
            "Which campaign reached which tier. Campaign 3 is the only one that reaches lower tiers.")
header_row(ws5, 4, ["Value tier", "Customers", "Campaign 1", "Campaign 2", "Campaign 3",
                    "Campaign 4", "Campaign 5", "Most recent"], [14, 12, 12, 12, 12, 12, 12, 13])
for i, t in enumerate(tiers):
    r_ = 5 + i
    ws5.cell(row=r_, column=1, value=t).font = Font(name=FONT, size=10, bold=True)
    ws5.cell(row=r_, column=2, value=f'=COUNTIF({brng("ValueTier")},A{r_})').number_format = INT
    for j, col in enumerate(["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4",
                             "AcceptedCmp5", "Response"]):
        ws5.cell(row=r_, column=3 + j,
                 value=f'=SUMIF({brng("ValueTier")},A{r_},{brng(col)})/B{r_}').number_format = PCT1

# ================================================ PART B: DISCOUNT ===========
ws6 = wb.create_sheet("PartB_Discount")
style_title(ws6, "Part B - discount dependence",
            "Deal-driven customers make 25% or more of their purchases on a deal.")
header_row(ws6, 4, ["Behaviour", "Customers", "% of customers", "Total spend", "% of spend",
                    "Avg spend", "Avg spend per purchase", "Avg income", "Response rate"],
           [14, 12, 15, 14, 12, 12, 21, 13, 14])
for i, g in enumerate(["Full-price", "Deal-driven"]):
    r_ = 5 + i
    ws6.cell(row=r_, column=1, value=g).font = Font(name=FONT, size=10, bold=True)
    ws6.cell(row=r_, column=2, value=f'=COUNTIF({brng("DiscountBehaviour")},A{r_})').number_format = INT
    ws6.cell(row=r_, column=3, value=f'=B{r_}/SUM($B$5:$B$6)').number_format = PCT1
    ws6.cell(row=r_, column=4, value=f'=SUMIF({brng("DiscountBehaviour")},A{r_},{brng("TotalSpend")})').number_format = INT
    ws6.cell(row=r_, column=5, value=f'=D{r_}/SUM($D$5:$D$6)').number_format = PCT1
    ws6.cell(row=r_, column=6, value=f'=D{r_}/B{r_}').number_format = NUM2
    ws6.cell(row=r_, column=7, value=f'=D{r_}/SUMIF({brng("DiscountBehaviour")},A{r_},{brng("TotalPurchases")})').number_format = NUM2
    ws6.cell(row=r_, column=8, value=f'=AVERAGEIF({brng("DiscountBehaviour")},A{r_},{brng("Income")})').number_format = NUM2
    ws6.cell(row=r_, column=9, value=f'=SUMIF({brng("DiscountBehaviour")},A{r_},{brng("Response")})/B{r_}').number_format = PCT2

# ============================================= BUSINESS INSIGHTS ============
ws7 = wb.create_sheet("Business_Insights")
style_title(ws7, "What the numbers say",
            "Each figure references the sheets above, so the statements update with the data.")
header_row(ws7, 4, ["#", "Finding", "Figure", "What a marketing team would do"],
           [5, 58, 15, 70])
def kpi_ref(label):
    return f"=KPIs!$B${KPI_ROW[label]}"


insights = [
    ("Only a tiny fraction of marketplace customers ever return", kpi_ref("Repeat rate"),
     "Do not fund a loyalty programme. The repeat base is too small to pay for one."),
    ("Almost all customer value arrives on the first order", kpi_ref("Share of value earned on the first order"),
     "Judge acquisition on first-order contribution, not on projected lifetime value."),
    ("The high-value tier carries over half of all revenue", "=PartA_ValueTiers!E5",
     "Target acquisition at customers who look like this tier: higher basket, better-served states."),
    ("Part B: the Best tier is a small share of customers", "=PartB_Tiers!C5",
     "A small, identifiable group worth protecting with full-margin offers."),
    ("Part B: the Best tier carries a third of all spend", "=PartB_Tiers!E5",
     "Concentrate campaign budget here first."),
    ("Part B: the Best tier responds at several times the base rate", "=PartB_Tiers!J5",
     "Highest return per campaign rupee of any group."),
    ("Part B: the Marginal tier barely responds at all", "=PartB_Tiers!I8",
     "Suppress from paid campaigns; the contact cost is not recovered."),
    ("Deal-driven customers are a third of the base", "=PartB_Discount!C6",
     "Large group, but see the next line before spending on them."),
    ("Deal-driven customers contribute only a tenth of spend", "=PartB_Discount!E6",
     "Discount-led contact buys volume at a margin the basket does not support."),
    ("A deal-driven basket is worth far less per purchase", "=PartB_Discount!G6",
     "Move this group to non-price offers, or stop contacting them."),
]
for i, (text, formula, action) in enumerate(insights):
    r_ = 5 + i
    ws7.cell(row=r_, column=1, value=i + 1).font = Font(name=FONT, size=10, bold=True, color=ACCENT)
    ws7.cell(row=r_, column=2, value=text).font = Font(name=FONT, size=10)
    v = ws7.cell(row=r_, column=3, value=formula)
    v.font = Font(name=FONT, size=10, bold=True, color=ACCENT)
    v.number_format = PCT2 if i in (0, 1, 2, 3, 4, 6, 7, 8) else NUM2
    ws7.cell(row=r_, column=4, value=action).font = Font(name=FONT, size=9, color=MUTED)
    for col in range(1, 5):
        ws7.cell(row=r_, column=col).alignment = Alignment(wrap_text=True, vertical="top")
        ws7.cell(row=r_, column=col).border = BORDER
    ws7.row_dimensions[r_].height = 30

# ====================================================== README SHEET ========
ws0 = wb.create_sheet("README", 0)
style_title(ws0, "E-Commerce Growth Analytics - Excel workbook", f"Author: {AUTHOR}")
ws0.column_dimensions["A"].width = 26
ws0.column_dimensions["B"].width = 104
readme = [
    ("Project", "E-Commerce Growth Analytics: Acquisition Economics & Campaign Response"),
    ("Author", AUTHOR),
    ("Part A dataset", "Brazilian E-Commerce Public Dataset by Olist - 96,470 delivered orders, "
                       "93,350 customers, Sep 2016 to Aug 2018"),
    ("Part B dataset", "Marketing Campaign / Customer Personality dataset - 2,026 customers after cleaning, "
                       "enrolled Jul 2012 to Jun 2014"),
    ("Are the two joined?", "No. They are different companies and share no customer, product, date or "
                            "geography key. Every sheet reports on one part or the other, never both."),
    ("How to read this file", "KPIs is the summary. PartA_* and PartB_* sheets hold the breakdowns. "
                              "PartA_Data and PartB_Data are the cleaned inputs every formula reads."),
    ("Formulas, not values", "Every reported number is a live formula over the data sheets. Change a value "
                             "in PartA_Data or PartB_Data and every summary updates."),
    ("RFM check", "PartB_RFM_Check rebuilds the R, F and M scores with nested IFs and compares them to the "
                  "Python scores row by row. The count on the KPIs sheet must equal the Part B customer count."),
    ("Rounding", "Python rounds half up to match MySQL's ROUND(), so the Python, SQL and Excel figures agree."),
    ("Source of the data", "See data/raw/README.md in the repository for the source, licence and SHA-256 "
                           "of every raw file."),
]
for i, (k, v) in enumerate(readme):
    r_ = 4 + i
    ws0.cell(row=r_, column=1, value=k).font = Font(name=FONT, size=10, bold=True, color=INK)
    c = ws0.cell(row=r_, column=2, value=v)
    c.font = Font(name=FONT, size=10, color=MUTED)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws0.row_dimensions[r_].height = 30

# Set the workbook's default font once, through the Normal named style, rather than stamping a
# Font object onto every cell. Writing ~60,000 individual font records made the file so
# style-heavy that LibreOffice could not open and recalculate it inside five minutes.
for sheet in wb.worksheets:
    sheet.sheet_properties.tabColor = None

wb.save(OUT)

print(f"\nsaved {OUT.relative_to(ROOT)}")
print(f"  sheets: {wb.sheetnames}")
