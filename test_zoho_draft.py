from pathlib import Path
import subprocess
import sys

import pandas as pd
from zoho_mail import from_env

FROM_ADDR = "pepper.yang@bc-la.org"

DRAFTS_CSV = Path("outreach_output/drafts.csv")
AUTO_OUTREACH_SCRIPT = Path("auto_outreach.py")


def looks_like_html(text: str) -> bool:
    s = str(text)
    return any(tag in s for tag in ("<br", "<strong", "<div", "<p", "<ul", "<li", "<a "))


def main():
    # Run auto_outreach.py using the SAME python as this script (your .venv)
    print("[1/3] Running auto_outreach.py with current interpreter ...")
    subprocess.run([sys.executable, str(AUTO_OUTREACH_SCRIPT)], check=True)

    if not DRAFTS_CSV.exists():
        raise FileNotFoundError(f"Missing {DRAFTS_CSV}. auto_outreach.py did not generate it.")

    print("[2/3] Loading drafts.csv ...")
    df = pd.read_csv(DRAFTS_CSV)

    required = {"to", "subject", "body"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"drafts.csv missing columns: {sorted(missing)}")

    print("[3/3] Creating Zoho drafts ...")
    client = from_env()

    created = 0
    skipped = 0
    failed = 0

    for i, row in df.iterrows():
        to_addr = str(row.get("to", "")).strip()
        subject = str(row.get("subject", "")).strip()
        body = str(row.get("body", ""))

        if not to_addr or not subject or not body:
            skipped += 1
            print(f"[SKIP] Row {i}: missing to/subject/body")
            continue

        mail_format = "html" if looks_like_html(body) else "plaintext"

        try:
            resp = client.create_draft(
                from_addr=FROM_ADDR,
                to_addr=to_addr,
                subject=subject,
                content=body,
                mail_format=mail_format,
            )
            created += 1
            print(f"[OK] Draft {created}: {to_addr} | {subject}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] Row {i}: {to_addr} | {subject} | {e}")

    print(f"\nDone. Created={created}, Skipped={skipped}, Failed={failed}")


if __name__ == "__main__":
    main()