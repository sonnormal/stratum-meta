# 📑 Stratum Change Request (CR) Master Record

> **Document Type:** Master Change Request Record & Governance Audit Log  
> **Lifecycle:** Maintained continuously across `GATE-01`, `GATE-02`, and `GATE-03`.  
> **Location:** `meta/changes/CR-26j002-telegram-commands/request.md`

---

## 📌 1. Request Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j002` |
| **Title** | Two-Way Conversational Telegram Commands (`/today`, `/this_month`, `/recent`) |
| **Requester** | Human Stakeholder (`sonnormal@gmail.com` / Chat ID `8502789411`) |
| **Ingress Channel** | Telegram Bot API (`@Sonnormal_cashflow_alert_bot`, long-polling loop) |
| **Egress Channel** | Telegram Bot API (`@Sonnormal_cashflow_alert_bot`, Markdown formatted replies) |
| **Created Timestamp** | `2026-10-13 21:00:00 UTC+7` |
| **Current Lifecycle State** | `INITIALIZED` (Awaiting `GATE-01` Value & Feasibility Decision) |

---

## 📥 2. Stakeholder Request Intake

### Original Inbound Prompt
```text
Enable two-way Telegram Bot interactions for the cashflow tracking system: allow the stakeholder to query aggregated spend for today (/today), current month (/this_month), and inspect the most recent transactions (/recent) directly on their mobile device via @Sonnormal_cashflow_alert_bot.
```

### Initial Intent & Objectives
* **Core Problem / Need:** Stakeholder currently receives one-way transaction push notifications, but cannot interactively query accumulated daily or monthly spend, or inspect historical transactions without opening pgAdmin or a database CLI.
* **Target Outcome:** 
  1. `services/cashflow` provides REST query endpoints to aggregate daily/monthly totals and list latest movements.
  2. `gateway` runs an asynchronous Telegram update poller (`getUpdates` with offset tracking), strictly authenticating the stakeholder's Chat ID.
  3. Responds immediately to `/today`, `/this_month`, `/recent`, and `/help` with clean, formatted mobile reports.
* **Urgency / Priority:** High (Unlocks direct interactive financial utility on mobile).

### Concrete Parameters & Invariants
* **Bot Username:** `@Sonnormal_cashflow_alert_bot`
* **Authorized Stakeholder Chat ID:** `8502789411` (all messages from unauthorized chat IDs are rejected or silently discarded)
* **Default Currency:** `VND`
* **Supported Commands:**
  * `/today`: Total debits, credits, and transaction count for the current calendar day.
  * `/this_month`: Total debits, credits, and transaction count for the current calendar month.
  * `/recent` (or `/recent [N]`): Formatted summary of the last 5 (or up to N) movements.
  * `/help` (or `/start`): Welcome message and command index.

---

## 📚 3. Supporting Documentation

| Document | Path / Link | Description |
| :--- | :--- | :--- |
| **Change Evaluation Report (CER)** | [`evaluation.md`](evaluation.md) | `STEP-03` / `GATE-01` Scope, Security & Cost-Benefit assessment |
| **Canonical Feature Spec** | [`../../features/telegram-conversational-queries.md`](../../features/telegram-conversational-queries.md) | `FEAT-002` Functional rules & acceptance criteria |
| **System Choreography Flow** | [`../../flows/telegram-command-query.md`](../../flows/telegram-command-query.md) | `FLOW-002` Sequence diagram for conversational polling |
| **Tier 3 E2E Acceptance Spec** | [`e2e_scenario.md`](e2e_scenario.md) | Cross-repo E2E acceptance test suite & harness |

---

## 📦 4. Affected Repositories & Execution Scope

| Repository | Role in Change | Branch / PR | Target Repo Scenario Spec |
| :--- | :--- | :--- | :--- |
| `services/cashflow` | Aggregation queries, recent movements endpoint & repo methods | `cr-26j002-cashflow-queries` | [`scenario.md` in services/cashflow](../../../services/cashflow/changes/CR-26j002-telegram-commands/scenario.md) |
| `gateway` | Telegram command listener, long poller, chat ID auth & reply formatter | `cr-26j002-gateway-commands` | [`scenario.md` in gateway](../../../gateway/changes/CR-26j002-telegram-commands/scenario.md) |

---

## ⚖️ 5. Three Human Governance Gates Audit Log

### 🛡️ GATE-01: Value & Feasibility Gate
* **Core Question:** *"Why do it & is it worth it?"*
* **Inspected Artifact:** [`evaluation.md`](evaluation.md) (CER)
* **Status:** `PENDING_REVIEW`
* **Decision Timestamp:** `PENDING`
* **Decided By:** Human Stakeholder (`sonnormal@gmail.com`)

---

### 🛡️ GATE-02: Contract & Test Scenario Gate
* **Core Question:** *"What exact behavior to build?"*
* **Inspected Artifacts:** [`e2e_scenario.md`](e2e_scenario.md) and target repo `scenario.md` specs
* **Status:** `PENDING`
* **Decision Timestamp:** `PENDING`

---

### 🛡️ GATE-03: User Acceptance Gate (UAT)
* **Core Question:** *"Does it work in reality?"*
* **Inspected Artifacts:** Pre-flight E2E scorecard and live test on `@Sonnormal_cashflow_alert_bot`
* **Status:** `PENDING`
* **Decision Timestamp:** `PENDING`
