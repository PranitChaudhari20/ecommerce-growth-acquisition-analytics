"""
06_run_sql.py  -  execute the SQL project and export every result set
=====================================================================
Author: Pranit Ajay Chaudhari

Runs 01_create_schema.sql, 02_import_data.sql and 03_business_queries.sql against a live
MySQL 8 or MariaDB server, then writes each query's result to sql/query_results/.

Usage:  python python/06_run_sql.py --user root --password "..." [--socket /path/mysqld.sock]
"""
import argparse
import csv
import re
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
OUT = SQL / "query_results"
OUT.mkdir(exist_ok=True)


def statements(text):
    """Split a script into statements, ignoring comment-only lines."""
    cleaned = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    return [s.strip() for s in re.split(r";\s*\n", cleaned) if s.strip()]


def run_script(cur, path, replace=None):
    text = path.read_text(encoding="utf-8")
    for old, new in (replace or {}).items():
        text = text.replace(old, new)
    for stmt in statements(text):
        cur.execute(stmt)
        if cur.description:
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            print(f"   {path.name}: {cols}")
            for rrow in rows:
                print(f"      {rrow}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default="")
    ap.add_argument("--socket", default=None)
    a = ap.parse_args()

    conn = pymysql.connect(host=a.host, port=a.port, user=a.user, password=a.password,
                           unix_socket=a.socket, local_infile=True, autocommit=True,
                           charset="utf8mb4")
    cur = conn.cursor()

    print("1/3  schema")
    run_script(cur, SQL / "01_create_schema.sql")

    print("2/3  import")
    # Rewrite the repo-relative LOAD DATA paths to absolute ones for this machine.
    run_script(cur, SQL / "02_import_data.sql", {
        "'data/cleaned/": f"'{(ROOT / 'data' / 'cleaned').as_posix()}/"})

    print("3/3  business queries")
    cur.execute("USE ecommerce_growth")
    blocks = re.split(r"^-- QUERY ", (SQL / "03_business_queries.sql").read_text(encoding="utf-8"),
                      flags=re.M)[1:]
    for block in blocks:
        header, body = block.split("\n", 1)
        num, title, _question = [p.strip() for p in header.split("|")]
        sql = "\n".join(l for l in body.splitlines()
                        if not l.strip().startswith("--")).strip().rstrip(";")
        sql = sql.split("\n-- ====")[0].strip().rstrip(";")
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        path = OUT / f"q{num}_{slug}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"   Q{num} {title:<36} {len(rows):>3} rows -> {path.relative_to(ROOT)}")

    conn.close()
    print("\nAll SQL executed.")


if __name__ == "__main__":
    main()
