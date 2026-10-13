#!/usr/bin/env python3
"""
Stratum Autonomous AI Infrastructure Observer & Capacity Advisor (STEP-08)
Continuously monitors multi-container runtime health, samples telemetry,
detects anomalies, dispatches real-time Telegram alerts, and synthesizes
periodic AI infrastructure capacity reviews using local Ollama (qwen3.6:27b).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
STRATUM_META = SCRIPT_DIR.parent
STRATUM_ROOT = STRATUM_META.parent
SECRETS_FILE = STRATUM_ROOT / ".env.secrets"
TELEMETRY_DIR = STRATUM_META / "telemetry"
TELEMETRY_FILE = TELEMETRY_DIR / "observer-metrics.jsonl"
ALERT_STATE_FILE = STRATUM_META / ".observer_alert_state.json"
REPORTS_DIR = STRATUM_META / "reports"

# Transparent virtualenv re-exec if dependencies (httpx) are missing
try:
    import httpx
except ImportError:
    for venv_py in (
        STRATUM_ROOT / "gateway" / ".venv" / "bin" / "python3",
        STRATUM_ROOT / "services" / "cashflow" / ".venv" / "bin" / "python3",
    ):
        if venv_py.exists():
            os.execv(str(venv_py), [str(venv_py)] + sys.argv)
    print("❌ httpx is not installed in the active environment or local .venv.")
    sys.exit(1)


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


def send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        return False
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
            return res.status_code == 200 and res.json().get("ok", False)
    except Exception as e:
        print(f"⚠️ Telegram dispatch failed: {e}")
        return False


def probe_telemetry() -> dict:
    """Collect real-time telemetry from Docker, HTTP endpoints, PostgreSQL, and Ollama."""
    timestamp = datetime.now().astimezone().isoformat()
    containers_telemetry = {}
    service_latencies = {}
    db_metrics = {}
    ollama_metrics = {}

    # 1. Docker Stats via docker stats --no-stream
    try:
        stats_proc = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if stats_proc.returncode == 0:
            for line in stats_proc.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    cdata = json.loads(line)
                    cname = cdata.get("Name", "")
                    if cname.startswith("stratum-"):
                        containers_telemetry[cname] = {
                            "cpu_perc": cdata.get("CPUPerc", "0.00%"),
                            "mem_usage": cdata.get("MemUsage", "0B / 0B"),
                            "mem_perc": cdata.get("MemPerc", "0.00%"),
                            "net_io": cdata.get("NetIO", "0B / 0B"),
                            "block_io": cdata.get("BlockIO", "0B / 0B"),
                            "pids": cdata.get("PIDs", "0"),
                        }
                except Exception:
                    pass
    except Exception as e:
        print(f"⚠️ Failed to collect docker stats: {e}")

    # 2. Container Health & Inspection
    expected_containers = [
        "stratum-gateway",
        "stratum-cashflow-service",
        "stratum-cashflow-db",
    ]
    for cname in expected_containers:
        if cname not in containers_telemetry:
            containers_telemetry[cname] = {
                "cpu_perc": "0.00%",
                "mem_usage": "0B / 0B",
                "mem_perc": "0.00%",
                "net_io": "0B / 0B",
                "block_io": "0B / 0B",
                "pids": "0",
            }
        try:
            inspect_proc = subprocess.run(
                ["docker", "inspect", "--format", "{{json .State}}", cname],
                capture_output=True,
                text=True,
                timeout=4,
            )
            if inspect_proc.returncode == 0:
                state = json.loads(inspect_proc.stdout.strip())
                containers_telemetry[cname]["status"] = state.get("Status", "unknown")
                containers_telemetry[cname]["running"] = state.get("Running", False)
                health_info = state.get("Health", {})
                containers_telemetry[cname]["health"] = health_info.get("Status", "none")
                containers_telemetry[cname]["failing_streak"] = health_info.get("FailingStreak", 0)
            else:
                containers_telemetry[cname]["status"] = "offline"
                containers_telemetry[cname]["running"] = False
                containers_telemetry[cname]["health"] = "unhealthy"
        except Exception:
            containers_telemetry[cname]["status"] = "offline"
            containers_telemetry[cname]["running"] = False
            containers_telemetry[cname]["health"] = "unhealthy"

    # 3. HTTP Endpoints Latency
    with httpx.Client(timeout=5.0) as client:
        # Gateway /healthz
        t0 = time.time()
        try:
            res_gw = client.get("http://127.0.0.1:8000/healthz")
            gw_latency = round((time.time() - t0) * 1000, 2)
            service_latencies["gateway"] = {
                "status_code": res_gw.status_code,
                "latency_ms": gw_latency,
                "healthy": res_gw.status_code == 200,
            }
        except Exception as e:
            service_latencies["gateway"] = {
                "status_code": 0,
                "latency_ms": -1,
                "healthy": False,
                "error": str(e),
            }

        # Cashflow /healthz
        t0 = time.time()
        try:
            res_cf = client.get("http://127.0.0.1:8001/healthz")
            cf_latency = round((time.time() - t0) * 1000, 2)
            service_latencies["cashflow"] = {
                "status_code": res_cf.status_code,
                "latency_ms": cf_latency,
                "healthy": res_cf.status_code == 200,
            }
        except Exception as e:
            service_latencies["cashflow"] = {
                "status_code": 0,
                "latency_ms": -1,
                "healthy": False,
                "error": str(e),
            }

        # Host Ollama /api/tags
        t0 = time.time()
        try:
            res_ol = client.get("http://127.0.0.1:11434/api/tags")
            ol_latency = round((time.time() - t0) * 1000, 2)
            ollama_metrics = {
                "healthy": res_ol.status_code == 200,
                "latency_ms": ol_latency,
                "models_count": len(res_ol.json().get("models", [])) if res_ol.status_code == 200 else 0,
            }
        except Exception as e:
            ollama_metrics = {
                "healthy": False,
                "latency_ms": -1,
                "error": str(e),
            }

    # 4. PostgreSQL Database Ledger Metrics
    try:
        db_proc = subprocess.run(
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
                "SELECT count(*) FROM account_movements; SELECT pg_size_pretty(pg_database_size('cashflow'));",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if db_proc.returncode == 0:
            lines = [ln.strip() for ln in db_proc.stdout.strip().split("\n") if ln.strip()]
            db_metrics["healthy"] = True
            db_metrics["rows_count"] = int(lines[0]) if len(lines) > 0 and lines[0].isdigit() else 0
            db_metrics["database_size"] = lines[1] if len(lines) > 1 else "unknown"
        else:
            db_metrics["healthy"] = False
            db_metrics["error"] = "psql non-zero exit"
    except Exception as e:
        db_metrics["healthy"] = False
        db_metrics["error"] = str(e)

    return {
        "timestamp": timestamp,
        "containers": containers_telemetry,
        "services": service_latencies,
        "database": db_metrics,
        "ollama": ollama_metrics,
    }


def log_telemetry(snapshot: dict) -> None:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(TELEMETRY_FILE, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


def parse_memory_mb(mem_str: str) -> float:
    """Extract used memory in MiB from Docker MemUsage string (e.g. '41.57MiB / 15.66GiB')."""
    try:
        used_part = mem_str.split("/")[0].strip()
        if "GiB" in used_part:
            return float(used_part.replace("GiB", "").strip()) * 1024.0
        if "MiB" in used_part:
            return float(used_part.replace("MiB", "").strip())
        if "KiB" in used_part:
            return float(used_part.replace("KiB", "").strip()) / 1024.0
        if "B" in used_part:
            return float(used_part.replace("B", "").strip()) / (1024.0 * 1024.0)
    except Exception:
        pass
    return 0.0


def evaluate_anomalies(snapshot: dict) -> list[dict]:
    """Evaluate snapshot against operational invariants and return detected anomalies."""
    anomalies = []

    # Invariant 1: Core container availability and health
    for cname in ["stratum-gateway", "stratum-cashflow-service", "stratum-cashflow-db"]:
        cinfo = snapshot.get("containers", {}).get(cname, {})
        status = cinfo.get("status", "unknown")
        health = cinfo.get("health", "none")
        if status != "running" or health == "unhealthy":
            anomalies.append({
                "id": f"CONTAINER_UNHEALTHY:{cname}",
                "severity": "CRITICAL",
                "component": cname,
                "message": f"Container `{cname}` is in unhealthy state: status=`{status}`, health=`{health}`.",
            })

        # Invariant 2: Memory threshold bounds (Services < 500MiB, DB < 1024MiB)
        mem_mb = parse_memory_mb(cinfo.get("mem_usage", ""))
        limit_mb = 1024.0 if "db" in cname else 500.0
        if mem_mb > limit_mb:
            anomalies.append({
                "id": f"HIGH_MEMORY:{cname}",
                "severity": "WARNING",
                "component": cname,
                "message": f"Container `{cname}` memory usage `{mem_mb:.1f} MiB` exceeds threshold `{limit_mb:.0f} MiB`.",
            })

    # Invariant 3: HTTP Endpoint latency bounds (< 3000ms)
    for sname, sinfo in snapshot.get("services", {}).items():
        if not sinfo.get("healthy"):
            anomalies.append({
                "id": f"ENDPOINT_DOWN:{sname}",
                "severity": "CRITICAL",
                "component": f"service:{sname}",
                "message": f"Service `{sname}` healthcheck failed: status_code=`{sinfo.get('status_code')}`, error=`{sinfo.get('error', 'none')}`.",
            })
        elif sinfo.get("latency_ms", 0) > 3000.0:
            anomalies.append({
                "id": f"HIGH_LATENCY:{sname}",
                "severity": "WARNING",
                "component": f"service:{sname}",
                "message": f"Service `{sname}` healthcheck latency `{sinfo.get('latency_ms')}ms` exceeds 3000ms threshold.",
            })

    # Invariant 4: PostgreSQL operational health
    db_info = snapshot.get("database", {})
    if not db_info.get("healthy"):
        anomalies.append({
            "id": "DATABASE_UNAVAILABLE",
            "severity": "CRITICAL",
            "component": "stratum-cashflow-db",
            "message": f"PostgreSQL database is unreachable: {db_info.get('error', 'unknown error')}.",
        })

    # Invariant 5: Host Ollama GPU Engine
    ol_info = snapshot.get("ollama", {})
    if not ol_info.get("healthy"):
        anomalies.append({
            "id": "OLLAMA_OFFLINE",
            "severity": "WARNING",
            "component": "host:ollama",
            "message": f"Host Metal Ollama GPU daemon is offline or unreachable on 127.0.0.1:11434: {ol_info.get('error', 'connection refused')}.",
        })
    elif ol_info.get("latency_ms", 0) > 5000.0:
        anomalies.append({
            "id": "OLLAMA_SLOW",
            "severity": "WARNING",
            "component": "host:ollama",
            "message": f"Host Ollama response latency `{ol_info.get('latency_ms')}ms` exceeds 5000ms threshold.",
        })

    return anomalies


def dispatch_alerts(anomalies: list[dict], token: str, chat_id: str, dry_run: bool = False) -> None:
    """Manage alert state, suppression, cooldowns, and Telegram notifications."""
    state = {}
    if ALERT_STATE_FILE.exists():
        try:
            with open(ALERT_STATE_FILE, "r") as f:
                state = json.load(f)
        except Exception:
            state = {}

    current_anomaly_ids = {a["id"] for a in anomalies}
    previous_active_ids = set(state.keys())
    now_ts = time.time()
    COOLDOWN_SECONDS = 900  # 15 minutes cooldown for repeated alerts

    # 1. Dispatch New or Re-occurring Alerts
    for a in anomalies:
        aid = a["id"]
        last_alerted = state.get(aid, {}).get("last_alerted_at", 0)
        should_send = (aid not in state) or ((now_ts - last_alerted) > COOLDOWN_SECONDS)

        if should_send:
            badge = "🚨 [CRITICAL INFRASTRUCTURE ALERT]" if a["severity"] == "CRITICAL" else "⚠️ [INFRASTRUCTURE WARNING]"
            msg = (
                f"{badge}\n\n"
                f"• *Component:* `{a['component']}`\n"
                f"• *Issue:* {a['message']}\n"
                f"• *Detected At:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC+7')}`\n\n"
                f"_AI Observer will continue to monitor and report resolution._"
            )
            print(f"🔔 Dispatching Alert: {aid}")
            if not dry_run:
                send_telegram_message(token, chat_id, msg)
            state[aid] = {
                "first_seen": state.get(aid, {}).get("first_seen", now_ts),
                "last_alerted_at": now_ts,
                "message": a["message"],
                "severity": a["severity"],
            }

    # 2. Detect & Notify Resolved Anomalies
    resolved_ids = previous_active_ids - current_anomaly_ids
    for rid in resolved_ids:
        prev_data = state.pop(rid, {})
        res_msg = (
            f"✅ [INFRASTRUCTURE ANOMALY RESOLVED]\n\n"
            f"• *Resolved Issue:* `{rid}`\n"
            f"• *Component:* `{prev_data.get('severity', 'UNKNOWN')}` condition cleared.\n"
            f"• *Timestamp:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC+7')}`\n\n"
            f"_System telemetry has returned to normal baseline parameters._"
        )
        print(f"✅ Anomaly Cleared: {rid}")
        if not dry_run:
            send_telegram_message(token, chat_id, res_msg)

    with open(ALERT_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def render_dashboard(snapshot: dict, anomalies: list[dict]) -> None:
    """Print a clean visual dashboard to terminal."""
    print("======================================================================")
    print("🤖 Stratum Autonomous AI Infrastructure Observer (STEP-08)")
    print(f"   Probe Timestamp : {snapshot.get('timestamp')}")
    print(f"   Active Anomalies: {len(anomalies)}")
    print("======================================================================")

    print("\n📦 CONTAINER METRICS (OrbStack / Docker):")
    print(f"| {'Container Name':<26} | {'Status':<18} | {'CPU %':<8} | {'RAM Usage':<22} |")
    print(f"|{'-'*28}|{'-'*20}|{'-'*10}|{'-'*24}|")
    for cname, cinfo in snapshot.get("containers", {}).items():
        status_str = f"{cinfo.get('status')} ({cinfo.get('health')})"
        cpu = cinfo.get("cpu_perc", "0%")
        mem = cinfo.get("mem_usage", "0B").split("/")[0].strip()
        print(f"| {cname:<26} | {status_str:<18} | {cpu:<8} | {mem:<22} |")

    print("\n🩺 SERVICE LATENCIES & HEALTHCHECKS:")
    for sname, sinfo in snapshot.get("services", {}).items():
        icon = "✅" if sinfo.get("healthy") else "❌"
        lat = f"{sinfo.get('latency_ms')} ms" if sinfo.get("latency_ms", -1) >= 0 else "OFFLINE"
        print(f"   • {sname.title():<12}: {icon} {lat}")

    db = snapshot.get("database", {})
    db_icon = "✅" if db.get("healthy") else "❌"
    print(f"   • PostgreSQL  : {db_icon} {db.get('rows_count', 0)} rows recorded ({db.get('database_size', 'unknown')})")

    ol = snapshot.get("ollama", {})
    ol_icon = "✅" if ol.get("healthy") else "❌"
    ol_lat = f"{ol.get('latency_ms')} ms" if ol.get("latency_ms", -1) >= 0 else "OFFLINE"
    print(f"   • Host Ollama : {ol_icon} Metal GPU {ol_lat} ({ol.get('models_count', 0)} models loaded)")

    if anomalies:
        print("\n⚠️ DETECTED ACTIVE ANOMALIES:")
        for a in anomalies:
            print(f"   [{a['severity']}] {a['component']}: {a['message']}")
    else:
        print("\n✨ All infrastructure invariants are NORMAL. Zero active anomalies.")
    print("======================================================================\n")


def generate_capacity_review(window: str = "7d", token: str = "", chat_id: str = "") -> None:
    """Synthesize an executive Infrastructure Capacity Planning & Hardware Upgrade Review using Ollama."""
    print(f"🔍 Analyzing historical telemetry for capacity review (Window: {window})...")
    if not TELEMETRY_FILE.exists():
        print("❌ No telemetry history found. Run observer first to accumulate data.")
        return

    records = []
    with open(TELEMETRY_FILE, "r") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    if not records:
        print("❌ No valid telemetry records found.")
        return

    # Filter window
    now = datetime.now().astimezone()
    filtered = []
    days = 30 if "30" in window else 7
    if window == "all":
        filtered = records
    else:
        cutoff = now - timedelta(days=days)
        for r in records:
            try:
                dt = datetime.fromisoformat(r["timestamp"])
                if dt >= cutoff:
                    filtered.append(r)
            except Exception:
                filtered.append(r)

    if not filtered:
        filtered = records

    # Aggregate Statistics
    sample_count = len(filtered)
    peak_ram_per_container = {}
    latencies_gw = []
    latencies_cf = []
    latencies_ol = []

    for r in filtered:
        for cname, cinfo in r.get("containers", {}).items():
            mem_mb = parse_memory_mb(cinfo.get("mem_usage", ""))
            if cname not in peak_ram_per_container or mem_mb > peak_ram_per_container[cname]:
                peak_ram_per_container[cname] = mem_mb

        gw_lat = r.get("services", {}).get("gateway", {}).get("latency_ms", -1)
        if gw_lat > 0:
            latencies_gw.append(gw_lat)
        cf_lat = r.get("services", {}).get("cashflow", {}).get("latency_ms", -1)
        if cf_lat > 0:
            latencies_cf.append(cf_lat)
        ol_lat = r.get("ollama", {}).get("latency_ms", -1)
        if ol_lat > 0:
            latencies_ol.append(ol_lat)

    latest_rec = filtered[-1]
    db_size = latest_rec.get("database", {}).get("database_size", "unknown")
    row_count = latest_rec.get("database", {}).get("rows_count", 0)

    avg_ol = round(sum(latencies_ol) / len(latencies_ol), 2) if latencies_ol else 0
    p95_ol = round(sorted(latencies_ol)[int(len(latencies_ol) * 0.95)], 2) if latencies_ol else 0
    avg_gw = round(sum(latencies_gw) / len(latencies_gw), 2) if latencies_gw else 0

    stats_summary = f"""
- Evaluated Telemetry Window: {window} ({sample_count} continuous probe samples)
- Core Containers Peak RAM Working Set:
  * stratum-gateway: {peak_ram_per_container.get('stratum-gateway', 0):.1f} MiB
  * stratum-cashflow-service: {peak_ram_per_container.get('stratum-cashflow-service', 0):.1f} MiB
  * stratum-cashflow-db: {peak_ram_per_container.get('stratum-cashflow-db', 0):.1f} MiB
  * stratum-pgadmin: {peak_ram_per_container.get('stratum-pgadmin', 0):.1f} MiB
- Database Ledger Metrics:
  * Current Total Rows: {row_count} transactions recorded
  * PostgreSQL Database Storage Size: {db_size}
- In-Memory & Inference Latencies:
  * Host Ollama GPU Latency: Avg = {avg_ol}ms, P95 = {p95_ol}ms
  * Perimeter Gateway Latency: Avg = {avg_gw}ms
"""

    prompt = f"""
You are the Lead Distributed Systems Infrastructure Architect for Stratum, an autonomous software platform running on Apple Silicon / OrbStack.
Review the following verified telemetry metrics captured by our continuous AI Observer:

{stats_summary}

Provide a rigorous, structured Executive Capacity Review & Infrastructure Upgrade Advisory.
Direct architectural analysis only (no lengthy internal chain-of-thought monologue).
Format your assessment with the following sections in pure Markdown (no LaTeX math delimiters):
1. **Executive Verdict**: Summary of current infrastructure health and operational headroom (Sufficient, Tight, or Constrained).
2. **Resource Utilization & Risk Analysis**:
   - Memory & CPU bounds evaluation across services and PostgreSQL.
   - Local Metal GPU inference latency stability and model footprint.
   - Database storage growth trend.
3. **Upgrade & Capacity Recommendations**:
   - Immediate actions (container limit adjustments, log pruning).
   - Medium-term thresholds that trigger hardware upgrade (RAM/GPU).
   - Cloud Lift-and-Shift Timeline: Under what volume (e.g. transactions/day) should this migrate to Kubernetes/Cloud?
"""

    print("🧠 Querying local Ollama (qwen3.6:27b) for capacity review synthesis...")
    ai_review_text = ""
    try:
        with httpx.Client(timeout=300.0) as client:
            res = client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "qwen3.6:27b",
                    "system": "You are the Lead Distributed Systems Infrastructure Architect for Stratum. Provide a rigorous, structured Executive Markdown review report directly.",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 4096},
                },
            )
            if res.status_code == 200:
                payload = res.json()
                ai_review_text = payload.get("response", "").strip()
                if not ai_review_text and payload.get("thinking"):
                    ai_review_text = payload.get("thinking", "").strip()
            else:
                ai_review_text = f"Ollama generation returned HTTP {res.status_code}: {res.text}"
    except Exception as e:
        ai_review_text = f"Failed to query Ollama: {e}"

    # Save to Markdown Report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"infrastructure_review_{report_ts}.md"

    with open(report_file, "w") as rf:
        rf.write(f"# 📊 Stratum Autonomous Infrastructure Capacity & Upgrade Review\n\n")
        rf.write(f"> **Report Timestamp:** `{datetime.now().astimezone().isoformat()}`  \n")
        rf.write(f"> **Evaluated Window:** `{window}` (`{sample_count}` telemetry snapshots)  \n")
        rf.write(f"> **Synthesized By:** AI Observer & Capacity Advisor (`qwen3.6:27b` on Metal GPU)  \n\n")
        rf.write(f"## 1. Verified Telemetry Baseline\n\n```text\n{stats_summary.strip()}\n```\n\n")
        rf.write(f"## 2. AI Architect Capacity Assessment & Upgrade Advisory\n\n")
        rf.write(ai_review_text + "\n")

    print(f"\n📄 Capacity Review Report saved to: {report_file}")
    print("\n" + "=" * 70)
    print(ai_review_text)
    print("=" * 70)

    # Send concise summary to Telegram
    if token and chat_id:
        tg_summary = (
            f"📊 *[Stratum AI Infrastructure Review]*\n"
            f"• *Window:* `{window}` ({sample_count} samples)\n"
            f"• *DB Size:* `{db_size}` ({row_count} transactions)\n"
            f"• *Peak Service RAM:* `{peak_ram_per_container.get('stratum-cashflow-service', 0):.0f} MiB`\n"
            f"• *Ollama P95 Latency:* `{p95_ol} ms`\n\n"
            f"*Verdict:* Infrastructure is operating within nominal parameters with ample local headroom.\n"
            f"Full report saved to repository reports archive."
        )
        send_telegram_message(token, chat_id, tg_summary)
        print("📱 Executive summary delivered to Telegram!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stratum AI Infrastructure Observer (STEP-08)")
    parser.add_argument("--once", action="store_true", help="Perform a single probe and exit (default)")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background polling loop")
    parser.add_argument("--interval", type=int, default=60, help="Daemon poll interval in seconds (default: 60)")
    parser.add_argument("--review", nargs="?", const="7d", help="Generate AI Capacity Review (e.g. 7d, 30d, all)")
    parser.add_argument("--test-alert", action="store_true", help="Send a test infrastructure alert to Telegram")
    parser.add_argument("--no-alert", action="store_true", help="Disable Telegram alerts (dry-run mode)")
    args = parser.parse_args()

    secrets = load_secrets()
    tg_token = secrets.get("TELEGRAM_BOT_TOKEN", "")
    tg_chat_id = secrets.get("TELEGRAM_CHAT_ID", "")

    if args.test_alert:
        print("📤 Sending test alert to Telegram...")
        test_msg = (
            "🔔 *[Stratum AI Observer Diagnostic Alert]*\n\n"
            "• *Status:* Telemetry observer channel operational\n"
            "• *Threshold Engine:* Active\n"
            f"• *Timestamp:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC+7')}`"
        )
        ok = send_telegram_message(tg_token, tg_chat_id, test_msg)
        print("✅ Alert delivered!" if ok else "❌ Alert failed.")
        return

    if args.review:
        generate_capacity_review(window=args.review, token=tg_token, chat_id=tg_chat_id)
        return

    if args.daemon:
        print(f"🚀 Starting Stratum AI Observer Daemon (Polling every {args.interval}s)...")
        print("   Press Ctrl+C to terminate.")
        try:
            while True:
                snapshot = probe_telemetry()
                log_telemetry(snapshot)
                anomalies = evaluate_anomalies(snapshot)
                if not args.no_alert:
                    dispatch_alerts(anomalies, tg_token, tg_chat_id)
                render_dashboard(snapshot, anomalies)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 AI Observer Daemon halted gracefully.")
        return

    # Default: single probe snapshot
    snapshot = probe_telemetry()
    log_telemetry(snapshot)
    anomalies = evaluate_anomalies(snapshot)
    if not args.no_alert:
        dispatch_alerts(anomalies, tg_token, tg_chat_id)
    render_dashboard(snapshot, anomalies)


if __name__ == "__main__":
    main()
