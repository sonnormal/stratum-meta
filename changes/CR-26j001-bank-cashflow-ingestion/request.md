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
* **Inspected Artifacts:** `scenario.md` in target repositories, JSON event contracts, and approved Acceptance Test Suite
* **Status:** `APPROVED`
* **Decision Timestamp:** `2026-10-07 06:15:00 UTC+7`
* **Decided By:** Human Stakeholder (`sonnormal@gmail.com`)
* **Approved Acceptance Test Suite (The 6 Test Cases):**

| ID | Category | Scenario & Invariant | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **`TC-01`** | **Boundary / Edge** | Mailbox `INBOX` is completely empty (`count == 0`). | Ingestion logs info; 0 DB writes; 0 Viber alerts; exits cleanly with code 0. |
| **`TC-02`** | **Happy Path Single** | 1 unread VIB debit email in `INBOX` (`-75,000 VND`). | Parsed; Ollama extracts fields; guardrail passes; 1 row saved in Postgres; 1 Viber push sent. |
| **`TC-03`** | **Happy Path Batch** | Multiple unread VIB emails in `INBOX`. | Each transaction processed independently; N rows committed; N alerts sent. |
| **`TC-04`** | **Noise Filtering** | Non-bank promotional/newsletter emails in `INBOX`. | Discarded by heuristic filter in < 1ms; Ollama not invoked; 0 DB writes. |
| **`TC-05`** | **Unhappy / Recovery** | IMAP unreachable, Ollama GPU timeout, or Viber 500. | Structured error logged; batch cursor preserved; 0 container crashes; clean exit. |
| **`TC-06`** | **Idempotency** | Re-polling inbox with already-processed emails. | Postgres `ON CONFLICT DO NOTHING`; returns `DUPLICATE_IGNORED`; 0 repeated Viber pushes. |

* **Reviewer Directives / Notes:**
  > *Approved delta scenario approach and the 6-case test suite across services/cashflow and gateway. AI QA Agent authorized to implement Tier 3 automated pre-flight runner.*

---

### 🛡️ GATE-03: User Acceptance Gate (UAT Sign-off)
* **Core Question:** *"Does it work in reality?"*
* **Inspected Environment:** Live container stack on OrbStack / Docker (`stratum-meta/deploy/docker-compose.yml`)
* **Status:** `AWAITING_HUMAN_SIGN_OFF`
* **Scorecard Artifact:** [`uat_results_20261011_190453.md`](uat_results_20261011_190453.md)
* **Verification Scorecard (Automated Pre-Flight & Physical Human Verification):**
  - [x] **`TC-01` Empty Inbox Edge:** Automated pre-flight verified (13ms, 0 DB writes, 0 alerts).
  - [x] **`TC-02` Happy Path Single:** Automated pre-flight verified (6251ms, ledger write verified in PostgreSQL).
  - [x] **`TC-03` Happy Path Batch:** Automated pre-flight verified (6305ms, multi-transaction isolation verified).
  - [x] **`TC-04` Noise Filter:** Automated pre-flight verified (15ms, non-bank email discarded without invoking LLM).
  - [x] **`TC-05` Unhappy Recovery:** Automated pre-flight verified (4938ms, structured error returned, 0 container crashes).
  - [x] **`TC-06` Idempotency Re-run:** Automated pre-flight verified (6176ms, `DUPLICATE_IGNORED`, 0 row drift).
  - [ ] **Physical Device Smoke Check:** Human stakeholder verifies real Viber push notification arrives on physical mobile phone (`+84981801931`).
* **Reviewer Directives / Notes:**
  > *Tier 3 E2E test runner passed 100% (6 / 6 canonical cases). Automated pre-flight verified. Awaiting human stakeholder verification of physical Viber notification to sign off GATE-03.*
