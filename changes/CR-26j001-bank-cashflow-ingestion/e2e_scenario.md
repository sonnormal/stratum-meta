# 🌐 Stratum Cross-Repository E2E Acceptance Test Specification: CR-26j001

> **Document Type:** Cross-Service Technical Specification & Executable Tier 3 Acceptance Tests (`STEP-04` Red Phase)  
> **Target Checkpoint:** `GATE-02` (Contract & Test Scenario Gate)  
> **Location:** `stratum-meta/changes/CR-26j001-bank-cashflow-ingestion/e2e_scenario.md`  
> **Scope:** Strictly isolated to **Tier 3 Automated E2E Testing** across `gateway`, `services/cashflow`, and host Ollama GPU. Microservice-internal unit and integration tests are isolated in their respective repo `scenario.md` files.

---

## 📌 1. Cross-Service Change Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j001` |
| **Primary Business Flow** | [FLOW-001: Inbound Email Transaction Ingestion & Alerting](../../flows/email-transaction-ingestion.md) |
| **Associated Feature** | [FEAT-001: Bank Transaction Ingestion & Cashflow Alerting](../../features/vib-transaction-alert.md) |
| **Participating Repositories** | [`gateway`](../../../gateway), [`services/cashflow`](../../../services/cashflow) |
| **Bound Contracts** | [`TransactionDetectedEvent (v1)`](../../contracts/events/transaction_detected.v1.json) |
| **Master CR Record** | [CR-26j001 Master Request](request.md) |
| **Status** | `APPROVED` (Signed off at `GATE-02`) |
| **Automated Runner** | [`scripts/e2e-verify.sh`](../../scripts/e2e-verify.sh) |
| **Latest E2E Report** | [`e2e_results_20261011_195515.md`](e2e_results_20261011_195515.md) |

---

## 🏛️ 2. Multi-Service Topology & Test Environment

*Executed locally via Docker / OrbStack multi-container stack (`stratum-meta/deploy/docker-compose.yml`):*

| Container / Component | Role in E2E Flow | Exposed Port | Healthcheck Endpoint |
| :--- | :--- | :--- | :--- |
| **`stratum-gateway`** | Ingress API, MIME parsing, Ollama client, Viber webhook | `8000` | `http://127.0.0.1:8000/healthz` |
| **`stratum-cashflow-service`** | Cashflow domain core, ledger rules, idempotency | `8001` | `http://127.0.0.1:8001/healthz` |
| **`stratum-cashflow-db`** | PostgreSQL 16 database (`cashflow` DB) | `5432` | `pg_isready -U postgres -d cashflow` |
| **Host Engine (Ollama)** | Local LLM extraction (`qwen3.6:27b` on Apple Silicon Metal GPU) | `11434` | `http://127.0.0.1:11434/api/tags` |

---

## 🧪 3. Acceptance Test Suite (The 6 Canonical Test Cases)

### TC-01: Boundary / Edge — Empty Payload
* **Scenario:** Inbound POST to `/api/v1/ingest/email` has completely empty body (`b""`).
* **Preconditions:** Clean stack.
* **Trigger:** `curl -s -4 -X POST http://127.0.0.1:8000/api/v1/ingest/email -d ""`
* **Expected Invariants:**
  - HTTP 200 with payload `{"processed":false,"skip_reason":"NOT_BANK_ALERT"}`.
  - Zero PostgreSQL database mutations in `account_movements`.
  - Zero external Viber notifications dispatched.
  - Exits in < 50ms with zero errors.

### TC-02: Happy Path Single — Single VIB Debit Email
* **Scenario:** 1 unread VIB debit email arrives (`-75,000 VND` at Highlands Coffee).
* **Preconditions:** Inbound MIME fixture [`sample_vib_debit.eml`](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_vib_debit.eml).
* **Trigger:** POST binary `.eml` to `http://127.0.0.1:8000/api/v1/ingest/email`.
* **Expected Invariants:**
  - Gateway parses MIME, passes heuristic filter, invokes Ollama (`qwen3.6:27b`).
  - Verbatim amount guardrail confirms `75000` exists in email text.
  - POSTs `TransactionDetectedEvent` to Cashflow Core (`http://cashflow-service:8001/api/v1/movements`).
  - Cashflow Core inserts 1 row into `account_movements` with `status: RECORDED`.
  - Viber notification dispatched.
  - HTTP 200 returned with `{"processed":true,"movement_status":"RECORDED"}`.

### TC-03: Happy Path Batch — Subsequent Inbound VIB Credit Email
* **Scenario:** Subsequent unread VIB credit email arrives (`+500,000 VND` from NGUYEN VAN A).
* **Preconditions:** Inbound MIME fixture [`sample_vib_credit.eml`](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_vib_credit.eml).
* **Trigger:** POST binary `.eml` to `http://127.0.0.1:8000/api/v1/ingest/email`.
* **Expected Invariants:**
  - Processed in independent transaction.
  - Exactly 1 new row committed in `account_movements` with `transaction_type: CREDIT`, `amount: 500000.00`.
  - HTTP 200 returned with `{"processed":true,"movement_status":"RECORDED"}`.

### TC-04: Noise Filtering — Promotional / Non-Bank Email
* **Scenario:** Non-bank promotional newsletter email arrives.
* **Preconditions:** Inbound MIME fixture [`sample_non_bank.eml`](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_non_bank.eml).
* **Trigger:** POST binary `.eml` to `http://127.0.0.1:8000/api/v1/ingest/email`.
* **Expected Invariants:**
  - Fast heuristic filter discards email in < 100ms.
  - Ollama LLM is completely bypassed (0 GPU cycles wasted).
  - 0 DB writes; 0 Viber notifications.
  - HTTP 200 returned with `{"processed":false,"skip_reason":"NOT_BANK_ALERT"}`.

### TC-05: Unhappy / Fault Recovery — Email Missing Verbatim Amount
* **Scenario:** Corrupted email alert with missing amount text.
* **Preconditions:** Inbound MIME fixture [`sample_vib_invalid_amount.eml`](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_vib_invalid_amount.eml).
* **Trigger:** POST binary `.eml` to `http://127.0.0.1:8000/api/v1/ingest/email`.
* **Expected Invariants:**
  - Pipeline catches missing amount / guardrail violation.
  - Returns structured response `{"processed":false,"skip_reason":"AMOUNT_NOT_FOUND"}`.
  - 0 unhandled 500 crashes; container `/healthz` remains 200 OK.

### TC-06: Idempotency Re-run — Duplicate Submission of TC-02
* **Scenario:** Duplicate re-submission of the identical email from `TC-02`.
* **Preconditions:** `sample_vib_debit.eml` was already successfully recorded.
* **Trigger:** Re-submit [`sample_vib_debit.eml`](../../../gateway/changes/CR-26j001-bank-cashflow-ingestion/fixtures/sample_vib_debit.eml).
* **Expected Invariants:**
  - Cashflow Core triggers PostgreSQL `ON CONFLICT (bank_code, raw_source_ref) DO NOTHING`.
  - HTTP 200 returned with `{"processed":true,"movement_status":"DUPLICATE_IGNORED"}`.
  - Database row count in `account_movements` strictly unchanged (1 -> 1).
  - 0 duplicate Viber messages dispatched.

---

## 📊 4. Authoritative Database Invariants

```sql
SELECT bank_code, account_number_mask, transaction_type, amount, currency, counterparty, raw_source_ref 
FROM account_movements;
```

Expected State post-suite:
* Exactly 2 authoritative rows (`RFC822-MSG-20261006-VIB-001@vib.com.vn` and `RFC822-MSG-20261006-VIB-002@vib.com.vn`).
* Zero partial states or phantom transactions.

---

## 🔄 5. Regression Promotion Policy (`STEP-07`)

1. **Cumulative E2E Regression Journey:** `TC-02` (Happy Path Debit Ingestion to Ledger) promoted to `stratum-meta/tests/e2e/regression/test_bank_ingestion_journey.py`.
2. **Push-Down to Tier 2 Integration:** `sample_vib_credit.eml` and `sample_vib_invalid_amount.eml` are preserved permanently in `gateway/tests/fixtures/real/` and `services/cashflow/tests/fixtures/real/` to be continuously verified during inner-loop commits.

---

## ⚖️ 6. GATE-02 Approval Log

* **Status:** `APPROVED`
* **Approved By:** Human Stakeholder (`sonnormal@gmail.com`)
* **Approval Timestamp:** `2026-10-07 06:15:00 UTC+7`
* **Sign-off Directive:**
  > *Approved Tier 3 Acceptance Suite across all 6 canonical cases. AI QA Agent authorized to execute automated pre-flight runner against Docker/OrbStack.*
