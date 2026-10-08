# 📑 Stratum Change Request (CR) Master Record

> **Document Type:** Master Change Request Record & Governance Audit Log  
> **Lifecycle:** Maintained continuously across `GATE-01`, `GATE-02`, and `GATE-03`.  
> **Location:** `meta/changes/CR-26j001-bank-cashflow-ingestion/request.md`

---

## 📌 1. Request Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j001` |
| **Title** | Bank Transaction Ingestion & Cashflow Alerting |
| **Requester** | Human Stakeholder (`sonnormal@gmail.com` / `+84981801931`) |
| **Ingress Channel** | Gmail IMAP (`sonnormal@gmail.com`, daily scheduled batch) |
| **Egress Channel** | Viber Bot (`+84981801931`) |
| **Created Timestamp** | `2026-10-05 21:00:00 UTC+7` |
| **Current Lifecycle State** | `INTAKE` (Configuring Concrete Parameters) |

---

## 📥 2. Stakeholder Request Intake

### Original Inbound Prompt
```text
Automate the ingestion of bank transaction alert emails (starting with VIB), parse debit/credit amounts, counterparty, and category/item, persist them in our cashflow domain service via daily run, and deliver conversational push alerts to stakeholder over Viber.
```

### Initial Intent & Objectives
* **Core Problem / Need:** Stakeholder needs automated cashflow tracking (amount, counterparty, item/category, datetime) without balance tracking or manual spreadsheet entry.
* **Target Outcome:** 
  1. `gateway` runs on a daily schedule, fetches unread bank emails from Gmail via IMAP, extracts transaction amount, datetime, counterparty, and category.
  2. `services/cashflow` consumes events, verifies idempotency, and records the movements in PostgreSQL.
  3. `gateway` sends a daily digest / transaction alert over Viber Bot to `+84981801931`.
* **Urgency / Priority:** Standard (Foundational Platform Capability).

### Concrete Channel & Target Parameters
* **Ingress Mailbox:** `sonnormal@gmail.com` (Gmail IMAP over SSL, port 993)
* **Ingress Cadence:** Daily scheduled batch run (once per day)
* **Ingress Auth Method:** Google App Password (`GATEWAY_GMAIL_APP_PASSWORD` env var, zero hardcoded secrets)
* **Egress Channel:** Viber Bot (`+84981801931`)
* **Data Scope:** Transaction amount, counterparty (merchant/sender), category/item, datetime, description (account balance is explicitly not tracked)
* **Default Currency:** `VND`

---

## 📚 3. Supporting Documentation

| Document | Path / Link | Description |
| :--- | :--- | :--- |
| **Change Evaluation Report (CER)** | [`evaluation.md`](evaluation.md) | `STEP-03` / `GATE-01` Scope, Security & Cost-Benefit assessment |
| **Canonical Feature Spec** | [`features/vib-transaction-alert.md`](../../features/vib-transaction-alert.md) | `FEAT-001` Functional rules & acceptance criteria |
| **System Choreography Flow** | [`flows/email-transaction-ingestion.md`](../../flows/email-transaction-ingestion.md) | `FLOW-001` Cross-repo sequence diagram |
| **Shared Event Contract** | [`contracts/events/transaction_detected.v1.json`](../../contracts/events/transaction_detected.v1.json) | `TransactionDetectedEvent` v1 JSON Schema |

---

## 📦 4. Affected Repositories & Execution Scope

*Unit and integration tests are isolated per repository. Test scenarios and fixtures live in the target repositories below:*

| Repository | Role in Change | Branch / PR | Target Repo Scenario Spec |
| :--- | :--- | :--- | :--- |
| `services/cashflow` | Account movement persistence, balance updates & idempotency | `cr-26j001-cashflow-baseline` | [`scenario.md` in target repo](../../../services/cashflow/changes/CR-26j001-bank-cashflow-ingestion/scenario.md) |
| `gateway` | Inbound IMAP email polling & outbound Zalo/Viber dispatch | `cr-26j001-gateway-ingestion` | [`scenario.md` in target repo](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/scenario.md) |

---

## ⚖️ 5. Three Human Governance Gates Audit Log

### 🛡️ GATE-01: Value & Feasibility Gate
* **Core Question:** *"Why do it & is it worth it?"*
* **Inspected Artifact:** [`evaluation.md`](evaluation.md) (CER)
* **Status:** `APPROVED`
* **Decision Timestamp:** `2026-10-07 05:25:00 UTC+7`
* **Decided By:** Human Stakeholder (`sonnormal@gmail.com`)
* **Reviewer Directives / Notes:**
  > *Approved to proceed with local Ollama qwen3.6 extraction, PostgreSQL persistence, and Viber push.*

---

### 🛡️ GATE-02: Contract & Test Scenario Gate
* **Core Question:** *"What exact behavior to build?"*
* **Inspected Artifacts:** `scenario.md` and `fixtures/` in target repositories
* **Status:** `APPROVED`
* **Decision Timestamp:** `2026-10-07 06:15:00 UTC+7`
* **Decided By:** Human Stakeholder (`sonnormal@gmail.com`)
* **Reviewer Directives / Notes:**
  > *Approved delta scenario approach and test specifications across services/cashflow and gateway.*

---

### 🛡️ GATE-03: User Acceptance Gate (UAT Sign-off)
* **Core Question:** *"Does it work in reality?"*
* **Inspected Environment:** Live container stack on OrbStack / Docker (`stratum-meta/deploy/docker-compose.yml`)
* **Status:** `READY_FOR_REVIEW`
* **Decision Timestamp:** `—`
* **Decided By:** `—`
* **Verification Checklist:**
  - [x] Live container health checks verified (`200 OK` on `http://localhost:8000/healthz` and `http://localhost:8001/healthz`)
  - [x] Sample `.eml` bank emails parsed and persisted accurately (`Highlands Coffee`, `75,000 VND`, `*4321` into PostgreSQL `account_movements`)
  - [x] Duplicate emails discarded with zero duplicate updates (`DUPLICATE_IGNORED` on second ingestion, table row count stays at 1)
  - [x] Conversational notification formatted and dispatched (`ViberClient.send_alert`)
* **Reviewer Directives / Notes:**
  > *E2E simulation executed live against host Ollama (qwen3.6:27b on Apple Silicon Metal GPU) and multi-container stack. Ready for stakeholder UAT sign-off.*
