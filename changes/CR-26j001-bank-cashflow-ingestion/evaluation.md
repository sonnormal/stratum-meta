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
| **Requester** | Human Stakeholder (`sonnormal@gmail.com` / `+84981801931`) |
| **Intake Channel** | Conversational Steering / Direct Intent |
| **Timestamp** | `2026-10-05 21:00:00 UTC+7` |
| **AI Evaluation Agent** | `orchestrator:evaluation-agent-v1` |
| **Status** | `APPROVED` (`GATE-01` Approved by Stakeholder) |

---

## 🎯 2. Executive Summary & Intent

### 2.1 Problem Statement
The stakeholder manages bank accounts (starting with Vietnam International Bank - VIB) and needs automated daily cashflow awareness. Currently, tracking movements requires manually opening banking apps or spreadsheets. There is no automated ingestion of movements, no semantic categorization of expenses, and no daily digest via conversational chat (Viber).

### 2.2 Proposed Solution
Implement a decoupled, event-driven daily batch pipeline across two repositories:
1. **`gateway` (Edge & Extraction Adapter):** 
   * Executes a daily scheduled IMAP batch check against `sonnormal@gmail.com`.
   * Filters bank emails, feeds raw text to **local host LLM via Ollama** (`http://host.docker.internal:11434` per [`ADR-26j003`](../../architecture/adrs/ADR-26j003-local-llm-extraction-ollama.md)) with strict JSON schema constrained decoding.
   * Extracts amount, currency, transaction type, counterparty (merchant/sender), and category.
   * Runs a deterministic string guardrail on amount before emitting canonical `TransactionDetectedEvent` (v1).
   * Dispatches formatted daily alerts / digests over **Viber Bot** to `+84981801931`.
2. **`services/cashflow` (Domain Service):** 
   * Consumes transaction events, enforces strict idempotency via unique constraints on `(bank_code, raw_source_ref)`, and persists records in PostgreSQL (`account_movements`). Account balance calculation is explicitly omitted.

---

## 📐 3. Scope Definition & Boundary Analysis

### 3.1 In-Scope Deliverables
* **`gateway`:**
  * Daily scheduled IMAP batch worker for `sonnormal@gmail.com`.
  * Local LLM extractor client connecting to Ollama on host Metal GPU (`http://host.docker.internal:11434`, using `qwen3.6` / `qwen2.5`).
  * 3-Stage Ingestion Pipeline: Heuristic Filter → Local LLM Structured JSON → Deterministic Substring Guardrail.
  * Outbound Viber Bot client pushing formatted alert messages to `+84981801931`.
* **`services/cashflow`:**
  * PostgreSQL table `account_movements` (fields: `event_id`, `occurred_at`, `bank_code`, `account_mask`, `transaction_type`, `amount`, `currency`, `counterparty`, `category`, `raw_source_ref`).
  * Idempotency verification preventing duplicate records.
  * Consumer for `contracts/events/transaction_detected.v1.json`.
* **`meta/contracts/`:**
  * Canonical `TransactionDetectedEvent` (v1) JSON schema including `counterparty` and `category`.

### 3.2 Out-of-Scope (Explicitly Deferred)
* **Account Balance Calculation:** Running balance is intentionally omitted; movements and counterparties are tracked directly.
* **Web UI Dashboard (`web`):** Frontend views and aggregation charts deferred to subsequent CR.
* **Non-Banking Emails:** Generalized email reader capabilities deferred; pipeline foundation is established in `gateway`.

### 3.3 Repository Impact Matrix

| Repository | Component Role | Impact Level | Primary Changes Required |
| :--- | :--- | :--- | :--- |
| `gateway` | Perimeter Edge | `High` | Daily IMAP batch poller, Ollama extractor client, guardrail validator, Viber Bot dispatcher. |
| `services/cashflow` | Financial Core | `High` | Initial service skeleton, PostgreSQL migrations (`account_movements`), consumer loop. |
| `web` | Web Application | `None` | Untouched in this change. |
| `meta` | Steering | `Low` | Contract update (`transaction_detected.v1.json`), ADR-26j003, CR tracking. |

---

## 🛡️ 4. Cybersecurity & Threat Assessment (STRIDE)

| Threat Category | Potential Risk / Vulnerability | Concrete Mitigation Strategy |
| :--- | :--- | :--- |
| **Spoofing** | Fraudulent emails injected pretending to be bank alerts. | SPF/DKIM verification in `gateway`, sender domain filtering (`*@vib.com.vn`), authenticated IMAP session. |
| **Tampering / Hallucination** | LLM hallucinates an incorrect numeric amount or inverts debit/credit. | **Deterministic Guardrail:** Validates that the extracted numeric amount string exists verbatim in the raw email body before publishing event. |
| **Repudiation** | Disputed transaction records. | Immutable storage of `raw_source_ref` (RFC 5322 `Message-ID`) and email arrival timestamps. |
| **Information Disclosure** | Leakage of personal banking details to cloud providers. | **100% On-Device:** Local LLM runs via Ollama on host Metal GPU; zero external AI API egress. Bank accounts masked (`*1234`). |
| **Denial of Service** | LLM GPU overload during batch run. | Heuristic pre-filter discards non-bank emails in < 1ms before invoking Ollama. |
| **Elevation of Privilege** | Rogue client dispatching fake Viber alerts. | Webhook requests require preshared bearer tokens; egress strictly restricted to verified recipient phone. |

### Secrets & Credentials Management
* Zero hardcoded credentials.
* Google App Password (`GATEWAY_GMAIL_APP_PASSWORD`), Viber Bot Token (`GATEWAY_VIBER_BOT_TOKEN`), and PostgreSQL URL loaded strictly via environment variables.

---

## 💰 5. Cost-Benefit & Operational Feasibility

### 5.1 Effort & Timeline
* Implementation Effort: Small/Medium (driven entirely by AI agents under strict TDD).
* Tier 1 Unit tests (< 1s execution, mocked LLM) and Tier 2 Integration tests (Testcontainers PostgreSQL + Ollama bridge).

### 5.2 Infrastructure & Operational Costs
* Compute: **$0** (Runs locally on Mac Studio via OrbStack and native host Ollama with 32B GPU acceleration).
* Storage: Minimal (~few MB of PostgreSQL data for personal movements).
* Third-Party APIs: **$0** (Gmail IMAP free, Viber Bot free API, Ollama open-weights model).

### 5.3 Net ROI Verdict
* **Verdict:** `High Net Positive ROI`.
* Delivers complete, automated, categorized cashflow awareness with zero recurring cloud bills and 100% data privacy.

---

## 📦 6. Proposed Repository Decomposition Plan

Upon `GATE-01` approval, this change will be decomposed into independent repository specifications:

```text
[CR-26j001] Macro Change: Bank Email Ingestion & Cashflow Alerting
  ├── gateway: Spec & TDD Task (scenario.md & fixtures/ in gateway repo)
  │     ├── Tier 1: Unit tests for MIME parsing, extractor mock, guardrail validation, Viber format
  │     └── Tier 2: Integration test calling host Ollama bridge & publishing TransactionDetectedEvent
  │
  └── services/cashflow: Spec & TDD Task (scenario.md & fixtures/ in services/cashflow repo)
        ├── Tier 1: Unit tests for movement ingestion & counterparty/category persistence
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

* **Option 1: `[Approve]`** → Proceeds immediately to `STEP-04` (initializes `gateway` and `services/cashflow`, authors `scenario.md`, and writes failing Red test suites).
* **Option 2: `[Reject]`** → Shelves the change request with recorded feedback; zero code generated.
* **Option 3: `[Request Scope Revision]`** → Adjusts in-scope boundaries or security constraints before proceeding.

---

### Audit Sign-Off
* **Decision:** `APPROVED`
* **Decided By:** Human Stakeholder (`sonnormal@gmail.com`)
* **Timestamp:** `2026-10-07 05:25:00 UTC+7`
* **Next Lifecycle Step:** `STEP-04` (Specification & Red Tests in `services/cashflow` and `gateway`)
