# data/cleaned/

*Author: Pranit Ajay Chaudhari*

Everything here is **generated** by the Python pipeline from `data/raw/`. Delete the folder, run
`bash run_all.sh`, and it comes back byte-for-byte identical — the pipeline is deterministic and
this is checked on every run.

## What is committed

| File | Size | What it is |
|---|---|---|
| `partA_cleaning_log.csv` | 1 KB | Every Part A cleaning step and the row count after it — the audit trail |
| `partB_cleaning_log.csv` | 1 KB | The same for Part B |
| `partB_customers.csv` | 446 KB | The 2,026 cleaned Part B customers with RFM scores and tiers |

## What is not committed, and why

| File | Size |
|---|---|
| `partA_orders.csv` | 19 MB |
| `partA_order_items.csv` | 15 MB |
| `partA_customers.csv` | 14 MB |

Those three total **47 MB** and are rebuilt in about 90 seconds by `run_all.sh` from the raw files,
which **are** committed. Committing regenerable intermediates alongside their own inputs would
roughly double the repository for no benefit, so they are listed in `.gitignore`.

**This matters for the SQL step.** `sql/02_import_data.sql` loads from this folder, so run
`bash run_all.sh` before `python python/06_run_sql.py` on a fresh clone. The README says the same.

## Rounding

Derived float columns are rounded to six decimal places before writing. Without that, a floating
point reduction can land one row a single bit apart between runs — one customer's average order
value wrote as `209.5433333333333` on one run and `209.54333333333335` on the next — which makes
the output non-reproducible for no analytical gain. Six decimals is far more precision than any
published figure uses.
