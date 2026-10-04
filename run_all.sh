#!/usr/bin/env bash
# Reproduce the whole project from the prepared raw files.
# Author: Pranit Ajay Chaudhari
set -euo pipefail

python python/01_clean_partA.py      # 9 Olist tables  -> 96,470 orders / 93,350 customers
python python/02_clean_partB.py      # 2,240 records   -> 2,026 customers
python python/03_analysis_partA.py   # acquisition economics -> outputs/tables/partA_*.csv
python python/04_analysis_partB.py   # RFM, campaigns, discounts -> outputs/tables/partB_*.csv
python python/05_build_charts.py     # 12 charts -> screenshots/
python python/07_build_excel.py      # Excel workbook -> excel/
python python/09_recalc_excel.py excel/Ecommerce_Growth_Analytics.xlsx

echo
echo "SQL (optional, needs MySQL 8 or MariaDB with local_infile enabled):"
echo "  python python/06_run_sql.py --user root --password \"...\""
echo "Then confirm all three tools agree:"
echo "  python python/08_verify.py"
