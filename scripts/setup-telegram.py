#!/usr/bin/env python3
"""
Stratum Telegram Bot Diagnostic & Verification CLI
Validates Telegram Bot Token, tests connectivity, and dispatches a test alert to phone.
"""
import argparse
import sys
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).parent.resolve()
STRATUM_META = SCRIPT_DIR.parent
STRATUM_ROOT = STRATUM_META.parent
SECRETS_FILE = STRATUM_ROOT / ".env.secrets"


def load_secrets() -> dict[str, str]:
    secrets = {}
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    secrets[k.strip()] = v.strip().strip('"').strip("'")
    return secrets


def main() -> None:
    parser = argparse.ArgumentParser(description="Stratum Telegram Bot Diagnostics")
    parser.add_argument("--token", help="Telegram Bot Token")
    parser.add_argument("--chat-id", help="Telegram Chat ID")
    parser.add_argument("--message", default="🔔 [Stratum] Push notification channel verified!", help="Test message text")
    args = parser.parse_args()

    secrets = load_secrets()
    token = args.token or secrets.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = args.chat_id or secrets.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env.secrets")
        sys.exit(1)

    print("======================================================================")
    print("🤖 Stratum Telegram Bot Diagnostic Tool")
    print(f"   Chat ID : {chat_id}")
    print("======================================================================")

    # 1. Validate Bot Identity
    with httpx.Client(timeout=10.0) as client:
        print("🔍 Checking Bot Identity with Telegram API (/getMe)...")
        res = client.get(f"https://api.telegram.org/bot{token}/getMe")
        if res.status_code != 200:
            print(f"❌ Failed to verify bot: HTTP {res.status_code} - {res.text}")
            sys.exit(1)

        bot_data = res.json().get("result", {})
        print(f"✅ Bot Validated: @{bot_data.get('username')} ({bot_data.get('first_name')})")

        # 2. Dispatch Test Message
        print(f"📤 Sending test notification to Chat ID: {chat_id}...")
        send_res = client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": args.message},
        )
        if send_res.status_code == 200 and send_res.json().get("ok"):
            msg_id = send_res.json().get("result", {}).get("message_id")
            print(f"✅ Notification delivered to your phone! (Message ID: {msg_id})")
        else:
            print(f"❌ Delivery failed: HTTP {send_res.status_code} - {send_res.text}")
            sys.exit(1)


if __name__ == "__main__":
    main()
