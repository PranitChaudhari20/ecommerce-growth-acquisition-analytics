"""
09_recalc_excel.py - recalculate Excel formulas using LibreOffice.
Author: Pranit Ajay Chaudhari

Usage:
    python python/09_recalc_excel.py excel/Ecommerce_Growth_Analytics.xlsx

The script requires LibreOffice/soffice on PATH. It writes the recalculated workbook
back to the same path and fails clearly if recalculation cannot be completed.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

def main():
    if len(sys.argv) != 2:
        print("Usage: python python/09_recalc_excel.py <workbook.xlsx>", file=sys.stderr)
        return 2

    workbook = Path(sys.argv[1]).resolve()
    if not workbook.exists():
        print(f"ERROR: workbook not found: {workbook}", file=sys.stderr)
        return 2

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print(
            "ERROR: LibreOffice (soffice/libreoffice) is required to recalculate "
            "Excel formulas. Install LibreOffice and rerun.",
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory(prefix="xlsx_recalc_") as td:
        outdir = Path(td)
        profile = outdir / "profile"
        profile.mkdir()
        cmd = [
            soffice, "--headless", "--nologo", "--nodefault", "--nofirststartwizard",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to", "xlsx", "--outdir", str(outdir), str(workbook),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print("ERROR: LibreOffice recalculation timed out.", file=sys.stderr)
            return 2

        recalculated = outdir / workbook.name
        if result.returncode != 0 or not recalculated.exists():
            print("ERROR: LibreOffice could not recalculate the workbook.", file=sys.stderr)
            if result.stdout.strip():
                print(result.stdout.strip(), file=sys.stderr)
            if result.stderr.strip():
                print(result.stderr.strip(), file=sys.stderr)
            return 2

        shutil.copy2(recalculated, workbook)

    print(f"Recalculated Excel workbook: {workbook}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
