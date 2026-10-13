#!/usr/bin/env python3
"""
Stratum Live Production Inbox Poller & Ingestion Runner
Fetches real bank alert emails from Gmail IMAP and pipes them through the live Gateway stack.
"""
import argparse
import imaplib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
STRATUM_META = SCRIPT_DIR.parent
STRATUM_ROOT = STRATUM_META.parent
SECRETS_FILE = STRATUM_ROOT / ".env.secrets"
CURSOR_FILE = STRATUM_META / ".inbox_cursor.json"

try:
    import httpx
except ImportError:
    for venv_py in (
        STRATUM_ROOT / "gateway" / ".venv" / "bin" / "python3",
        STRATUM_ROOT / "services" / "cashflow" / ".venv" / "bin" / "python3",
    ):
        if venv_py.exists():
            os.execv(str(venv_py), [str(venv_py)] + sys.argv)
    print("❌ httpx is not installed in the active Python environment or local .venv.")
    sys.exit(1)


def get_last_cursor_date() -> tuple[str | None, str]:
    """Retrieve the high-water mark date from cursor state file or cashflow database."""
    # 1. Try state file
    if CURSOR_FILE.exists():
        try:
            with open(CURSOR_FILE, "r") as f:
                data = json.load(f)
                val = data.get("last_run_date")
                if val:
                    return str(val), "STATE_FILE"
        except Exception:
            pass

    # 2. Try querying stratum-cashflow-db via docker
    try:
        res = subprocess.run(
            [
                "docker",
                "exec",
                "stratum-cashflow-db",
                "psql",
                "-U",
                "postgres",
                "-d",
                "cashflow",
                "-t",
                "-c",
                "SELECT MAX(occurred_at) FROM account_movements;",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            raw_val = res.stdout.strip().split()[0]  # e.g. 2026-10-12
            dt = datetime.strptime(raw_val, "%Y-%m-%d")
            return dt.strftime("%d-%b-%Y"), "DATABASE_MAX"
    except Exception:
        pass

    return None, "NONE"


def save_cursor_state(run_date: str, metadata: dict) -> None:
    """Save the watermark cursor to persistent storage."""
    try:
        payload = {
            "last_run_date": run_date,
            "last_run_timestamp": datetime.now().astimezone().isoformat(),
            **metadata,
        }
        with open(CURSOR_FILE, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"📌 Updated cursor watermark in {CURSOR_FILE} -> {run_date}")
    except Exception as e:
        print(f"⚠️ Failed to update cursor file: {e}")


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
        default=None,
        help="Start date (e.g. 01-Jan-2026 or 2026-01-01). Defaults to last run / watermark date.",
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
    parser.add_argument(
        "--mailbox",
        "--folder",
        dest="mailbox",
        default="INBOX",
        help="IMAP mailbox folder to select (e.g. INBOX, '[Gmail]/All Mail')",
    )
    parser.add_argument(
        "--all-mail",
        action="store_true",
        help="Convenience: select '[Gmail]/All Mail' folder (includes archived emails)",
    )
    parser.add_argument(
        "--no-alert",
        "--quiet",
        dest="no_alert",
        action="store_true",
        help="Silently ingest into database without dispatching mobile push notifications (ideal for historical backfills)",
    )
    parser.add_argument(
        "--no-update-cursor",
        action="store_true",
        help="Do not update the cursor watermark file after polling completes",
    )
    parser.add_argument("--sender", default="vib.com.vn", help="Sender query string")
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8000", help="Perimeter Gateway URL")
    parser.add_argument("--max", type=int, default=None, help="Max emails to process")
    args = parser.parse_args()

    if args.all_mail:
        args.mailbox = '"[Gmail]/All Mail"'
    elif " " in args.mailbox and not args.mailbox.startswith('"'):
        args.mailbox = f'"{args.mailbox}"'

    cursor_origin = "EXPLICIT_CLI"
    if args.year:
        try:
            yr = int(args.year)
            args.since = f"01-Jan-{yr}"
            args.before = f"01-Jan-{yr + 1}"
            cursor_origin = f"YEAR_FILTER ({args.year})"
        except ValueError:
            print(f"❌ Invalid year: {args.year}")
            sys.exit(1)
    elif args.since is None:
        last_date, source_type = get_last_cursor_date()
        if last_date:
            args.since = last_date
            cursor_origin = f"AUTOMATIC_WATERMARK ({source_type}: {last_date})"
        else:
            args.since = "01-Jan-2026"
            cursor_origin = "DEFAULT_BASELINE (01-Jan-2026)"
    else:
        cursor_origin = f"MANUAL_OVERRIDE ({args.since})"

    norm_since = normalize_imap_date(args.since)
    norm_before = normalize_imap_date(args.before)

    user, password = load_secrets()

    print("======================================================================")
    print("🚀 Stratum Live Inbox Poller & Ingestion Runner")
    print(f"   Mailbox      : {user}")
    print(f"   Folder       : {args.mailbox}")
    print(f"   Cursor Source: {cursor_origin}")
    print(f"   Alert Egress : {'SILENCED (Backfill mode)' if args.no_alert else 'ACTIVE (Telegram)'}")
    print(f"   Date Range   : SINCE {norm_since or 'ANY'} -> BEFORE {norm_before or 'NOW'}")
    print(f"   Sender Filter: {args.sender}")
    print(f"   Gateway API  : {args.gateway_url}")
    print("======================================================================")

    # 1. Connect IMAP
    print("🔍 Connecting to imap.gmail.com:993 (SSL)...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(user, password)
    mail.select(args.mailbox, readonly=True)

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
        if not args.no_update_cursor:
            today_str = datetime.now().strftime("%d-%b-%Y")
            save_cursor_state(
                run_date=today_str,
                metadata={
                    "mailbox": user,
                    "folder": args.mailbox,
                    "total_scanned": 0,
                    "recorded": 0,
                    "duplicates": 0,
                    "skipped": 0,
                    "errors": 0,
                },
            )
        return

    # 2. Process through Gateway API
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = (
        STRATUM_META
        / "changes"
        / "CR-26j001-bank-cashflow-ingestion"
        / f"live_ingestion_results_{timestamp}.md"
    )
    report_file.parent.mkdir(parents=True, exist_ok=True)

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

                post_params = {}
                if args.no_alert:
                    post_params["dispatch_alert"] = "false"

                response = client.post(
                    f"{args.gateway_url}/api/v1/ingest/email",
                    content=raw_bytes,
                    headers={"Content-Type": "message/rfc822"},
                    params=post_params,
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
        rf.write(f"> **Executed At:** `{datetime.now().astimezone().isoformat()}`  \n")
        rf.write(f"> **Target Mailbox:** `{user}`  \n")
        rf.write(f"> **Mailbox Folder:** `{args.mailbox}`  \n")
        rf.write(f"> **Alert Mode:** `{'SILENCED (Backfill mode)' if args.no_alert else 'ACTIVE (Telegram)'}`  \n")
        rf.write(f"> **Filter Criteria:** `{query}`  \n\n")
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

    # Persist Cursor Watermark
    if not args.no_update_cursor:
        today_str = datetime.now().strftime("%d-%b-%Y")
        save_cursor_state(
            run_date=today_str,
            metadata={
                "mailbox": user,
                "folder": args.mailbox,
                "total_scanned": len(msg_ids),
                "recorded": recorded_count,
                "duplicates": duplicate_count,
                "skipped": skipped_count,
                "errors": error_count,
            },
        )


if __name__ == "__main__":
    main()
