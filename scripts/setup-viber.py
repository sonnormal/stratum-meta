#!/usr/bin/env python3
"""
Stratum Viber Bot Diagnostic & Verification CLI
Validates Viber Bot Auth Token, inspects account metadata, and tests alert delivery.
"""
import argparse
import json
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


def save_secret(key: str, value: str) -> None:
    lines = []
    found = False
    if SECRETS_FILE.exists():
        with open(SECRETS_FILE, "r") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f'{key}="{value}"\n')
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f'{key}="{value}"\n')

    with open(SECRETS_FILE, "w") as f:
        f.writelines(new_lines)


def get_account_info(token: str) -> dict:
    headers = {"X-Viber-Auth-Token": token}
    with httpx.Client(timeout=10.0) as client:
        resp = client.post("https://chatapi.viber.com/pa/get_account_info", headers=headers, json={})
        return resp.json()


def send_test_message(token: str, receiver_id: str, message: str) -> dict:
    headers = {"X-Viber-Auth-Token": token}
    payload = {
        "receiver": receiver_id,
        "min_api_version": 1,
        "type": "text",
        "text": message,
    }
    with httpx.Client(timeout=10.0) as client:
        resp = client.post("https://chatapi.viber.com/pa/send_message", headers=headers, json=payload)
        return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stratum Viber Bot Setup & Diagnostics")
    parser.add_argument("--token", help="Viber Bot Auth Token (Application Key)")
    parser.add_argument("--receiver", help="Viber Recipient User ID")
    parser.add_argument("--send-test", action="store_true", help="Send a test ping message")
    args = parser.parse_args()

    secrets = load_secrets()
    token = args.token or secrets.get("VIBER_AUTH_TOKEN", "")
    receiver = args.receiver or secrets.get("VIBER_RECEIVER_ID", "")

    if not token:
        print("❌ No Viber Auth Token provided.")
        print("   Pass via --token <TOKEN> or set VIBER_AUTH_TOKEN in .env.secrets")
        sys.exit(1)

    print("======================================================================")
    print("🤖 Stratum Viber Bot Diagnostic Tool")
    print("======================================================================")

    # 1. Validate Token with Viber API
    print("🔍 Calling Viber API: /pa/get_account_info...")
    info = get_account_info(token)

    if info.get("status") != 0:
        print(f"❌ Viber API rejected token: status={info.get('status')} message={info.get('status_message')}")
        sys.exit(1)

    print("✅ Token validated successfully!")
    print(f"   Bot Name     : {info.get('name')}")
    print(f"   Bot URI      : {info.get('uri')}")
    print(f"   Subscribers  : {info.get('subscribers_count', 0)}")
    print(f"   Deep Link    : viber://pa?chatURI={info.get('uri')}")

    # Save token to .env.secrets if newly provided
    if args.token and args.token != secrets.get("VIBER_AUTH_TOKEN"):
        save_secret("VIBER_AUTH_TOKEN", args.token)
        print("💾 Saved VIBER_AUTH_TOKEN to .env.secrets")

    # 2. Check Receiver ID
    if args.receiver and args.receiver != secrets.get("VIBER_RECEIVER_ID"):
        save_secret("VIBER_RECEIVER_ID", args.receiver)
        receiver = args.receiver
        print("💾 Saved VIBER_RECEIVER_ID to .env.secrets")

    # 3. Test Message if requested
    if args.send_test:
        if not receiver:
            print("❌ Cannot send test message: VIBER_RECEIVER_ID is not configured.")
            print("   Pass --receiver <USER_ID> or add VIBER_RECEIVER_ID to .env.secrets")
            sys.exit(1)

        print(f"\n📤 Sending test alert to receiver: {receiver}...")
        test_msg = "[Stratum Test] 🔔 Bank cashflow notification channel verified!"
        res = send_test_message(token, receiver, test_msg)
        if res.get("status") == 0:
            print("✅ Test message delivered successfully! Check your phone.")
        else:
            print(f"❌ Failed to send message: status={res.get('status')} message={res.get('status_message')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
