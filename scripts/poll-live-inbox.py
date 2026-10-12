#!/usr/bin/env python3
"""
Stratum Live Production Inbox Poller & Ingestion Runner
Fetches real bank alert emails from Gmail IMAP and pipes them through the live Gateway stack.
"""
import argparse
import imaplib
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).parent.resolve()
STRATUM_META = SCRIPT_DIR.parent
STRATUM_ROOT = STRATUM_META.parent
SECRETS_FILE = STRATUM_ROOT / ".env.secrets"


def load_secrets() -> tuple[str, str]:
    if not SECRETS_FILE.exists():
        print(f"❌ Secrets file not found at {SECRETS_FILE}")
        sys.exit(1)

    gmail_user = ""
    gmail_pass = ""

    with open(SECRETS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GMAIL_USER="):
                gmail_user = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("GMAIL_APP_PASSWORD="):
                gmail_pass = line.split("=", 1)[1].strip().strip('"').strip("'").replace(" ", "")

    if not gmail_user or not gmail_pass:
        print("❌ Missing GMAIL_USER or GMAIL_APP_PASSWORD in .env.secrets")
        sys.exit(1)

    return gmail_user, gmail_pass


def normalize_imap_date(date_input: str | None) -> str | None:
    if not date_input:
        return None
    date_str = date_input.strip()
    for fmt in ("%d-%b-%Y", "%d-%B-%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%b-%Y")
    except ValueError:
        pass
    try:
        dt = datetime.strptime(date_str, "%Y")
        return dt.strftime("01-Jan-%Y")
    except ValueError:
        pass
    return date_str


def main() -> None:
    parser = argparse.ArgumentParser(description="Stratum Live Production Inbox Poller")
    parser.add_argument(
        "--since",
        "--start-date",
        dest="since",
        default="01-Jan-2026",
        help="Start date (e.g. 01-Jan-2026 or 2026-01-01)",
    )
    parser.add_argument(
        "--before",
        "--end-date",
        dest="before",
        default=None,
        help="End date (e.g. 31-Dec-2026 or 2026-12-31)",
    )
    parser.add_argument(
        "--year",
        default=None,
        help="Filter exclusively by year (e.g. 2026 sets 01-Jan-2026 to 01-Jan-2027)",
    )
    parser.add_argument("--sender", default="vib.com.vn", help="Sender query string")
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8000", help="Perimeter Gateway URL")
    parser.add_argument("--max", type=int, default=None, help="Max emails to process")
    args = parser.parse_args()

    if args.year:
        try:
            yr = int(args.year)
            args.since = f"01-Jan-{yr}"
            args.before = f"01-Jan-{yr + 1}"
        except ValueError:
            print(f"❌ Invalid year: {args.year}")
            sys.exit(1)

    norm_since = normalize_imap_date(args.since)
    norm_before = normalize_imap_date(args.before)

    user, password = load_secrets()

    print("======================================================================")
    print("🚀 Stratum Live Inbox Poller & Ingestion Runner")
    print(f"   Mailbox      : {user}")
    print(f"   Date Range   : SINCE {norm_since or 'ANY'} -> BEFORE {norm_before or 'NOW'}")
    print(f"   Sender Filter: {args.sender}")
    print(f"   Gateway API  : {args.gateway_url}")
    print("======================================================================")

    # 1. Connect IMAP
    print("🔍 Connecting to imap.gmail.com:993 (SSL)...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(user, password)
    mail.select("INBOX", readonly=True)

    query_parts = [f'FROM "{args.sender}"']
    if norm_since:
        query_parts.append(f'SINCE "{norm_since}"')
    if norm_before:
        query_parts.append(f'BEFORE "{norm_before}"')
    query = f"({' '.join(query_parts)})"

    print(f"📬 Executing IMAP Search: {query}")
    status, data = mail.search(None, query)
    msg_ids = data[0].split() if data and data[0] else []

    total_matching = len(msg_ids)
    print(f"   Found {total_matching} matching emails in date range.")

    if args.max and args.max > 0:
        msg_ids = msg_ids[-args.max:]
        print(f"   Limiting to latest {len(msg_ids)} emails.")

    if not msg_ids:
        print("ℹ️  No matching emails found to process.")
        mail.close()
        mail.logout()
        return

    # 2. Process through Gateway API
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = (
        STRATUM_META
        / "changes"
        / "CR-26j001-bank-cashflow-ingestion"
        / f"live_ingestion_results_{timestamp}.md"
    )

    recorded_count = 0
    duplicate_count = 0
    skipped_count = 0
    error_count = 0
    details = []

    print("\n▶️ Streaming emails to Gateway Ingestion API...")

    with httpx.Client(timeout=180.0) as client:
        for idx, mid in enumerate(msg_ids, 1):
            t_start = time.time()
            try:
                res, msg_data = mail.fetch(mid, "(RFC822)")
                raw_bytes = msg_data[0][1]

                response = client.post(
                    f"{args.gateway_url}/api/v1/ingest/email",
                    content=raw_bytes,
                    headers={"Content-Type": "message/rfc822"},
                )
                duration_ms = int((time.time() - t_start) * 1000)

                if response.status_code == 200:
                    payload = response.json()
                    processed = payload.get("processed", False)
                    status_str = payload.get("movement_status") or payload.get("skip_reason") or "UNKNOWN"

                    if status_str == "RECORDED":
                        recorded_count += 1
                        icon = "✅ RECORDED"
                    elif status_str == "DUPLICATE_IGNORED":
                        duplicate_count += 1
                        icon = "🔁 DUPLICATE"
                    else:
                        skipped_count += 1
                        icon = "⏭️  SKIPPED "

                    print(f"   [{idx}/{len(msg_ids)}] ID {mid.decode()}: {icon} ({status_str}) in {duration_ms}ms")
                    details.append(
                        f"| `{mid.decode()}` | `{status_str}` | `{duration_ms}ms` | `HTTP 200` |"
                    )
                else:
                    error_count += 1
                    print(f"   [{idx}/{len(msg_ids)}] ID {mid.decode()}: ❌ HTTP {response.status_code}")
                    details.append(
                        f"| `{mid.decode()}` | `ERROR: HTTP {response.status_code}` | `{duration_ms}ms` | `FAILED` |"
                    )

            except Exception as e:
                error_count += 1
                print(f"   [{idx}/{len(msg_ids)}] ID {mid.decode()}: ❌ ERROR: {e}")
                details.append(f"| `{mid.decode()}` | `EXCEPTION: {e}` | - | `FAILED` |")

    mail.close()
    mail.logout()

    print("\n======================================================================")
    print("📊 LIVE INGESTION SUMMARY")
    print(f"   Total Scanned  : {len(msg_ids)}")
    print(f"   New Recorded   : {recorded_count}")
    print(f"   Duplicates     : {duplicate_count}")
    print(f"   Filtered/Skip  : {skipped_count}")
    print(f"   Errors         : {error_count}")
    print("======================================================================")

    # Write Markdown Report
    with open(report_file, "w") as rf:
        rf.write(f"# 📊 Live Production Inbox Ingestion Report\n\n")
        rf.write(f"> **Executed At:** `{datetime.utcnow().isoformat()}Z`  \n")
        rf.write(f"> **Filter Criteria:** `{query}`  \n")
        rf.write(f"> **Target Mailbox:** `{user}`  \n\n")
        rf.write(f"## Summary Metrics\n\n")
        rf.write(f"| Metric | Count |\n| :--- | :--- |\n")
        rf.write(f"| **Total Emails Evaluated** | `{len(msg_ids)}` |\n")
        rf.write(f"| **New Transactions Recorded** | `{recorded_count}` |\n")
        rf.write(f"| **Duplicates Safely Ignored** | `{duplicate_count}` |\n")
        rf.write(f"| **Promotional/Noise Skipped** | `{skipped_count}` |\n")
        rf.write(f"| **Failures / Errors** | `{error_count}` |\n\n")
        rf.write(f"## Execution Log\n\n")
        rf.write(f"| Email ID | Outcome | Latency | HTTP Status |\n| :--- | :--- | :--- | :--- |\n")
        rf.write("\n".join(details) + "\n")

    print(f"📄 Report written to: {report_file}")


if __name__ == "__main__":
    main()
