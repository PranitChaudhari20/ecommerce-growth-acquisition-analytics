"""
00_prepare_raw.py  -  privacy preparation of the raw files before they are committed
====================================================================================
Author: Pranit Ajay Chaudhari

WHY THIS EXISTS
---------------
The published Olist dataset anonymised its identifiers, but free-text fields were not scrubbed, and
customers typed real contact details into them. A scan of the raw download found NINE real email
addresses - several of them clearly personal accounts - inside review comments, plus one in a
seller's city field.

Re-publishing those on a public GitHub repository would expose other people's personal data for no
analytical gain, because THIS PROJECT NEVER USES THE COMMENT TEXT. The analysis reads
`review_score` only; `review_comment_title` and `review_comment_message` are not referenced in any
script, query or formula.

So the committed copy of the reviews file has those two free-text columns removed, and the single
affected seller city is masked. Everything the analysis actually consumes is untouched.

This script is idempotent and is NOT part of run_all.sh - it is a one-time preparation step, run
once after downloading the raw data. data/raw/README.md records both the original and the prepared
SHA-256 so provenance stays checkable.

Run:  python python/00_prepare_raw.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
DROP_COLS = ["review_comment_title", "review_comment_message"]


def scan(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return sorted(set(EMAIL.findall(text)))


print("Preparing raw files for publication\n" + "=" * 74)

# ---------------------------------------------------------------- reviews ----
rp = RAW / "olist_order_reviews_dataset.csv"
rev = pd.read_csv(rp)
before = scan(rp)
present = [c for c in DROP_COLS if c in rev.columns]
if present:
    rev = rev.drop(columns=present)
    rev.to_csv(rp, index=False)
    print(f"  reviews : dropped {present}")
else:
    print("  reviews : free-text columns already removed (nothing to do)")
print(f"            {len(rev):,} rows x {rev.shape[1]} columns kept: {list(rev.columns)}")
print(f"            email addresses before: {len(before)}, after: {len(scan(rp))}")

# ---------------------------------------------------------------- sellers ----
sp = RAW / "olist_sellers_dataset.csv"
sell = pd.read_csv(sp)
hits = sell.seller_city.astype(str).str.contains(EMAIL, regex=True, na=False)
if hits.any():
    print(f"  sellers : masking {int(hits.sum())} seller_city value(s) containing an email address")
    sell.loc[hits, "seller_city"] = "unknown"
    sell.to_csv(sp, index=False)
else:
    print("  sellers : no contact details in seller_city (nothing to do)")

# ------------------------------------------------------------- final scan ----
print("\n  Final scan of every raw file:")
total = 0
for f in sorted(RAW.glob("*.csv")):
    found = scan(f)
    total += len(found)
    print(f"    {f.name:46} {len(found)} email address(es)")
print(f"\n  TOTAL remaining: {total}")
if total:
    raise SystemExit("Personal data still present - do not publish.")
print("  Clean. Safe to commit.")
