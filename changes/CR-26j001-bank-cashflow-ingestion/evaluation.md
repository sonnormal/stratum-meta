# 📊 Stratum Change Evaluation Report (CER)

> **Document Type:** Pre-Implementation Feasibility, Scope & Cybersecurity Evaluation (`STEP-03`)  
> **Target Checkpoint:** `GATE-01` (Value & Feasibility Gate)  
> **Location:** `meta/changes/CR-26j001-bank-cashflow-ingestion/evaluation.md`  
> **Associated Request:** [`request.md`](request.md) (`CR-26j001`)

---

## 📌 1. Change Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j001` |
| **Title** | Bank Transaction Ingestion & Cashflow Alerting |
| **Requester** | Human Stakeholder |
| **Intake Channel** | Conversational Steering / Direct Intent |
| **Timestamp** | `2026-10-05 21:00:00 UTC+7` |
| **AI Evaluation Agent** | `orchestrator:evaluation-agent-v1` |
| **Status** | `PENDING_REVIEW` (Awaiting `GATE-01` Sign-Off) |

---

## 🎯 2. Executive Summary & Intent

### 2.1 Problem Statement
The stakeholder manages accounts across banks (starting with Vietnam International Bank - VIB). Currently, tracking cashflow movements (payments, settlements, debits, cashouts) requires manually opening mobile banking apps or checking raw email alerts. There is no automated ledger of cashflow movements, no unified balance tracking, and no instant cross-channel alerting via conversational bots (Zalo/Viber).

### 2.2 Proposed Solution
Implement a decoupled, event-driven ingestion pipeline across two repositories:
1. **`gateway` (Edge Adapter):** Periodically polls transaction alert emails via IMAP, verifies DKIM/sender legitimacy, extracts financial transaction details, and publishes canonical `TransactionDetectedEvent` (v1). It also serves as the outbound delivery edge for Zalo/Viber bot alerts.
2. **`services/cashflow` (Domain Service):** Consumes transaction events, enforces strict idempotency via unique constraints, persists account movements in PostgreSQL, recalculates latest account balances, and dispatches conversational notification payloads back through `gateway`.

---

## 📐 3. Scope Definition & Boundary Analysis

### 3.1 In-Scope Deliverables
* **`gateway`:**
  * Background IMAP poller configured via environment credentials.
  * MIME parsing and bank-specific email parser plugin (VIB alert pattern).
  * Outbound Zalo and Viber bot webhook message dispatchers.
* **`services/cashflow`:**
  * PostgreSQL table `account_movements` with composite unique index on `(bank_code, raw_source_ref)`.
  * Idempotency verification preventing duplicate processing.
  * Event consumer for `contracts/events/transaction_detected.v1.json`.
  * Notification message formatter (amount, masked account, remaining balance).
* **`meta/contracts/`:**
  * Canonical `TransactionDetectedEvent` (v1) JSON schema.

### 3.2 Out-of-Scope (Explicitly Deferred)
* **Web UI Dashboard (`web`):** Visual frontend charts and tables will be tackled in a dedicated follow-up CR once backend data models stabilize.
* **Additional Banks:** Support for Vietcombank, Techcombank, and Momo is deferred to future CRs. The parser interface in `gateway` will be structured to accept new bank plugins without modifying core logic.
* **Historical CSV Statement Import:** Manual batch file processing is deferred.

### 3.3 Repository Impact Matrix

| Repository | Component Role | Impact Level | Primary Changes Required |
| :--- | :--- | :--- | :--- |
| `gateway` | Perimeter Edge | `High` | IMAP poller, MIME parser, VIB regex extractor, event publisher, Zalo/Viber dispatcher. |
| `services/cashflow` | Financial Core | `High` | Initial service skeleton, PostgreSQL migrations (`account_movements`), consumer loop, balance logic. |
| `web` | Web Application | `None` | Untouched in this change. |
| `meta` | Steering | `Low` | Contract definition (`transaction_detected.v1.json`), flow documentation (`FLOW-001`), CR tracking. |

---

## 🛡️ 4. Cybersecurity & Threat Assessment (STRIDE)

| Threat Category | Potential Risk / Vulnerability | Concrete Mitigation Strategy |
| :--- | :--- | :--- |
| **Spoofing** | Attacker injects fraudulent emails pretending to be bank transaction alerts. | `gateway` enforces SPF/DKIM validation and restricts processing to authorized bank sender domains (e.g. `*@vib.com.vn`). |
| **Tampering** | Event payload corrupted or modified in transit across message bus. | Strict schema enforcement against `contracts/events/transaction_detected.v1.json`. Malformed payloads are rejected to DLQ. |
| **Repudiation** | Ambiguity regarding source or timing of a recorded cashflow movement. | Store immutable `raw_source_ref` (RFC 5322 `Message-ID`), bank timestamp, and system ingestion timestamp. |
| **Information Disclosure** | Leakage of full bank account numbers in logs or push notifications. | Bank account numbers are strictly masked (e.g. `*4321`) before logging or message dispatch. |
| **Denial of Service** | Malformed emails or IMAP spam flood causing resource exhaustion. | Regex timeouts, memory-bounded MIME streaming, and rate-limited IMAP fetch batches. |
| **Elevation of Privilege** | Rogue client triggering unauthorized push alerts. | `gateway` webhook endpoints require preshared bearer tokens; notifications only dispatch to pre-approved chat IDs. |

### Secrets & Credentials Management
* Zero hardcoded credentials.
* IMAP app passwords, database URLs, and Zalo/Viber bot tokens are loaded strictly via container environment variables (`.env` template provided).

---

## 💰 5. Cost-Benefit & Operational Feasibility

### 5.1 Effort & Timeline
* Implementation Effort: Small/Medium (driven entirely by AI agents under strict TDD).
* Tier 1 Unit tests (< 1s execution) and Tier 2 Integration tests with Testcontainers (PostgreSQL).

### 5.2 Infrastructure & Operational Costs
* Compute: $0 (Runs locally on Mac Studio via OrbStack / Docker).
* Storage: Minimal (~few MB of PostgreSQL data for personal bank movements).
* Third-Party APIs: $0 (Standard email IMAP and free tier personal Zalo/Viber bot webhooks).

### 5.3 Net ROI Verdict
* **Verdict:** `High Net Positive ROI`.
* Replaces tedious manual mobile app logins with instant, automated, auditable cashflow awareness.

---

## 📦 6. Proposed Repository Decomposition Plan

Upon `GATE-01` approval, this change will be decomposed into independent repository specifications:

```text
[CR-26j001] Macro Change: Bank Email Ingestion & Cashflow Alerting
  ├── gateway: Spec & TDD Task (scenario.md & fixtures/ in gateway repo)
  │     ├── Tier 1: Unit tests for MIME parsing & VIB regex extraction
  │     └── Tier 2: Integration test publishing TransactionDetectedEvent
  │
  └── services/cashflow: Spec & TDD Task (scenario.md & fixtures/ in services/cashflow repo)
        ├── Tier 1: Unit tests for balance recalculation & alert text formatting
        └── Tier 2: Testcontainers PostgreSQL unique constraint & persistence test
```

---

## ⚖️ 7. GATE-01 Decision & Human Review Block

### Review Options

```text
┌────────────────────────────────────────────────────────────────────────┐
│               GATE-01: VALUE & FEASIBILITY REVIEW                      │
│                                                                        │
│  [ ✅ APPROVE (WORTH IT) ]    [ ❌ REJECT (NOT WORTH IT) ]             │
│                                                                        │
│  [ 🔄 REQUEST SCOPE REVISION ]                                         │
└────────────────────────────────────────────────────────────────────────┘
```

* **Option 1: `[Approve]`** → Proceeds immediately to `STEP-04` (generate repo-scoped specs and trigger TDD Red test suites in `gateway` and `services/cashflow`).
* **Option 2: `[Reject]`** → Shelves the change request with recorded feedback; zero code generated.
* **Option 3: `[Request Scope Revision]`** → Adjusts in-scope boundaries or security constraints before proceeding.

---

### Audit Sign-Off
* **Decision:** `PENDING`
* **Decided By:** `—`
* **Timestamp:** `—`
