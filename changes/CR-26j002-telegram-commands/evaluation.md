# 📄 Stratum Change Evaluation Report (CER)

> **Document Type:** Change Evaluation & Feasibility Assessment (Generated in `STEP-03`)  
> **Target Checkpoint:** `GATE-01` (Human Value & Feasibility Decision)  
> **Location:** `meta/changes/CR-26j002-telegram-commands/evaluation.md`

---

## 📌 1. Request Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j002` |
| **Request Title** | Two-Way Conversational Telegram Commands (`/today`, `/this_month`, `/recent`) |
| **Requester** | Human Stakeholder (`sonnormal@gmail.com` / Chat ID `8502789411`) |
| **Intake Channel** | Telegram Bot API (`@Sonnormal_cashflow_alert_bot`) |
| **Timestamp** | `2026-10-13 21:05:00 UTC+7` |
| **AI Evaluation Agent** | `orchestrator:evaluation-agent-v1` |
| **Status:** | `PENDING_REVIEW` (Awaiting `GATE-01` Sign-Off) |

---

## 🎯 2. Executive Summary & AI Recommendation

### Brief Overview
The stakeholder currently receives one-way outbound push alerts when bank transactions occur, but has no on-demand mobile interface to query financial state. This change introduces two-way conversational command handling over the existing Telegram bot `@Sonnormal_cashflow_alert_bot`. The stakeholder can send `/today`, `/this_month`, and `/recent` to inspect accumulated cashflow metrics directly on mobile without needing a web dashboard or SQL query.

### Strategic Recommendation
> [!NOTE]
> **AI Recommendation:** `RECOMMENDED`
> 
> **Rationale:** Low implementation risk and high operational utility. Exposes aggregated metrics already stored in PostgreSQL (`143` backfilled records, `1.88B VND`) without requiring extra infrastructure, public webhooks, or open incoming ports.

---

## 🔍 3. Multi-Level Impact Analysis

### 3.1 Process Impact
* **Business & User Workflows:** Stakeholder gains instant conversational access to daily and monthly financial totals directly in Telegram chat.
* **Operational Runbooks:** Zero change to deployment workflows; long-polling loop runs as an asynchronous background worker within the existing `stratum-gateway` container.
* **Compliance & Governance:** Strict single-user authorization preserves data privacy; no financial data is broadcast to unauthorized users.
* **CI/CD & Delivery Pipelines:** Standard 3-tier automated verification applies (Tier 1 unit tests, Tier 2 Testcontainers integration, Tier 3 multi-service E2E).

### 3.2 Feature & API Contract Impact
* **Affected Capabilities:** Introduces interactive chat commands while preserving existing transaction alert push notifications.
* **API & Contract Changes:**
  * [x] **Non-breaking Additions:**
    * `services/cashflow`:
      - `GET /api/v1/metrics/today` -> Summary of debits/credits for current calendar date.
      - `GET /api/v1/metrics/month?year=YYYY&month=MM` -> Summary of debits/credits for target calendar month.
      - `GET /api/v1/movements/recent?limit=5` -> Ordered list of latest N movements.
    * `gateway`:
      - Background worker polling Telegram `getUpdates`.
* **Data Schema Impact:** Purely additive read queries against existing `account_movements` table. Zero schema migrations or DDL changes required.

### 3.3 Repository Impact Matrix

| Repository | Component Role | Impact Level | Primary Changes Required |
| :--- | :--- | :--- | :--- |
| `gateway` | Ingress / Egress Gateway | `Medium` | Asynchronous Telegram poller, Chat ID authenticator, command dispatcher, and message formatter. |
| `services/cashflow` | Domain & Persistence Service | `Medium` | Add aggregation repository methods and REST read endpoints (`/metrics/today`, `/metrics/month`, `/movements/recent`). |
| `stratum-meta` | Living Specs & Orchestration | `Low` | E2E scenario specs (`e2e_scenario.md`), mock Telegram test fixtures, and automated verification script. |

---

## 🛡️ 4. Cybersecurity & Threat Assessment

### 4.1 Threat Modeling (STRIDE)

| Threat Category | Applicable? | Risk Level | Description & Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Spoofing (Identity)** | Yes | Medium | Unauthorized Telegram users messaging the public bot. **Mitigation:** Strict message filtering: check `message.chat.id == TELEGRAM_CHAT_ID`. Messages from unauthorized chats are ignored or rejected. |
| **Tampering (Data Integrity)** | No | Low | Inbound commands are strictly read-only (`/today`, `/recent`). No state mutation is permitted via Telegram commands. |
| **Repudiation** | No | Low | Every command received and responded to is logged with timestamp, user ID, command name, and latency. |
| **Information Disclosure** | Yes | High | Financial amounts and counterparties exposed if bot responds to unauthorized queries. **Mitigation:** Chat ID whitelist enforced before parsing any command or querying `cashflow-service`. |
| **Denial of Service (DoS)** | Yes | Low | Telegram rate limits outgoing bot messages (max 30 msgs/sec). Long polling avoids exposing public HTTP ingress ports. |
| **Elevation of Privilege** | No | Low | Bot commands only invoke read endpoints. |

### 4.2 Ingress Architecture: Long Polling vs. Webhook
* **Architectural Decision:** Use **Telegram Long Polling (`getUpdates`)** rather than Webhook.
  * *Rationale:* Stratum runs locally in containerized environments (OrbStack / Docker Desktop) without a public IP or reverse proxy. Webhooks require public tunnels (ngrok, Cloudflare Tunnel) which introduce external dependencies and security attack surface. Long polling initiates outbound HTTPS requests to `api.telegram.org` and requires **zero incoming firewall ports**.

---

## 💰 5. Cost-Benefit & Operational Feasibility

* **Implementation Compute Cost:** Minimal (~12 hours AI agent synthesis and verification across unit, integration, and E2E tiers).
* **Runtime Overhead:**
  * Memory: < 15MB additional RAM in `stratum-gateway`.
  * CPU: Negligible (< 0.1% CPU idle during long-polling timeout).
* **ROI:** High. Immediately closes the interactive loop for financial monitoring on mobile.

---

## ⚖️ 6. Decision & Gate Checkpoint

* **Target Checkpoint:** `GATE-01: Value & Feasibility Gate`
* **Recommendation:** `APPROVE` and proceed to `STEP-04` (TDD Phase 1: Author Red Tests and Acceptance Specs).
