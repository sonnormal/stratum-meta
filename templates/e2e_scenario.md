# 🌐 Stratum Cross-Repository E2E Acceptance Test Specification

> **Document Type:** Cross-Service Technical Specification & Executable Tier 3 Acceptance Tests (`STEP-04` Red Phase)  
> **Target Checkpoint:** `GATE-02` (Contract & Test Scenario Gate)  
> **Location:** `stratum-meta/changes/CR-YYaXXX-<short-title>/e2e_scenario.md`  
> **Scope:** Strictly isolated to **Tier 3 Automated E2E Testing** across multiple interconnected repositories. Microservice internal logic and unit/integration tests are specified in their respective `<repo>/scenario.md` files.

---

## 📌 1. Cross-Service Change Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-YYaXXX` (e.g. `CR-26j001`) |
| **Primary Business Flow** | [FLOW-XXX: Short Title](../../flows/FLOW-XXX-title.md) |
| **Associated Feature** | [FEAT-XXX: Short Title](../../features/FEAT-XXX-title.md) |
| **Participating Repositories** | `gateway`, `services/<service-name>`, etc. |
| **Bound Contracts** | [EventName (v1)](../../contracts/events/name.v1.json) |
| **Master CR Record** | [CR-YYaXXX Master Request](request.md) |
| **Status** | `PENDING_GATE_02_APPROVAL` |

---

## 🏛️ 2. Multi-Service Topology & Test Environment

*Defines the interconnected container stack required to execute this E2E acceptance suite locally in Docker / OrbStack.*

| Container / Component | Role in E2E Flow | Exposed Port | Healthcheck Endpoint |
| :--- | :--- | :--- | :--- |
| **`stratum-gateway`** | Ingress API & perimeter validation | `8000` | `http://127.0.0.1:8000/healthz` |
| **`stratum-<service>-service`** | Core domain processing | `8001` | `http://127.0.0.1:8001/healthz` |
| **`stratum-<service>-db`** | Authoritative persistence | `5432` | `pg_isready` |
| **Host Engine (e.g. Ollama)** | Local inference (Metal GPU) | `11434` | `http://127.0.0.1:11434/api/tags` |

---

## 🧪 3. Acceptance Test Suite (The Canonical Categories)

*The 5 canonical test case categories (ISO/IEC/IEEE 29119-4 / ISTQB v4.0) evaluated end-to-end against the perimeter:*

### TC-01: Boundary / Edge
* **Scenario:** Inbound payload is empty or at system boundary (`count == 0` or empty byte payload).
* **Preconditions:** Clean environment.
* **Trigger:** POST empty payload to perimeter ingress.
* **Expected Invariants:** 
  - Status 200 with structured skip reason (e.g. `NOT_BANK_ALERT`).
  - Zero database mutations.
  - Zero external alerts emitted.
  - Clean exit with zero errors.

### TC-02: Happy Path Single
* **Scenario:** Single canonical event arrives at perimeter.
* **Preconditions:** Single valid event payload / email fixture in inbox.
* **Trigger:** Submit canonical transaction fixture to perimeter ingress.
* **Expected Invariants:**
  - Ingress parses and processes event end-to-end.
  - Domain core records transaction in PostgreSQL ledger (`RECORDED`).
  - Downstream notification dispatched.
  - Authoritative table row matches exact monetary and counterparty values.

### TC-03: Happy Path Batch
* **Scenario:** Multiple transactions arrive in a single batch or sequential processing stream.
* **Preconditions:** N distinct valid transaction fixtures.
* **Trigger:** Submit subsequent batch fixtures.
* **Expected Invariants:**
  - Each transaction processed independently in isolated transactions.
  - Exactly N distinct rows committed to authoritative ledger.
  - Exactly N notifications emitted.

### TC-04: Noise Filtering
* **Scenario:** Unrelated, promotional, or non-domain payload hits the perimeter.
* **Preconditions:** Non-domain sample payload (e.g. marketing newsletter).
* **Trigger:** Submit noise fixture to perimeter ingress.
* **Expected Invariants:**
  - Heuristic filter discards payload in < 100ms.
  - Heavy downstream components (LLM inference, database transactions) are completely bypassed.
  - Zero database writes; zero alerts.

### TC-05: Unhappy / Fault Recovery
* **Scenario:** Payload contains malformed fields, missing mandatory data, or downstream service encounters transient failure.
* **Preconditions:** Malformed payload (e.g. missing amount).
* **Trigger:** Submit malformed fixture to ingress.
* **Expected Invariants:**
  - System captures failure gracefully without unhandled crashes.
  - Structured error returned (e.g. `AMOUNT_NOT_FOUND` or `GUARDRAIL_VIOLATION`).
  - Container health endpoints (`/healthz`) remain 100% green.

### TC-06: Idempotency Re-run
* **Scenario:** Duplicate submission of an already processed transaction.
* **Preconditions:** Payload from `TC-02` was already successfully processed.
* **Trigger:** Re-submit identical payload with same unique natural/synthetic key.
* **Expected Invariants:**
  - Core database applies `ON CONFLICT DO NOTHING`.
  - Ingress returns `DUPLICATE_IGNORED`.
  - Database row count strictly unchanged.
  - Zero duplicate outbound notifications dispatched.

---

## 📊 4. Authoritative Database & State Invariants

*Defines what database records, tables, and constraints MUST be verified post-execution:*

| Table Name | Key Constraints Verified | Expected Final Row Count |
| :--- | :--- | :--- |
| `account_movements` | Composite Unique `(bank_code, raw_source_ref)` | Exactly N valid unique transactions |

---

## 🔄 5. Regression Promotion Policy (`STEP-07`)

* How this suite transitions to permanent regression testing upon merge:
1. **Canonical Business Journey:** `TC-02` is merged into the permanent cumulative E2E regression suite in `stratum-meta/tests/e2e/regression/`.
2. **Push-Down to Tier 2:** Edge cases (`TC-01`), noise filters (`TC-04`), and malformed fixtures (`TC-05`) are captured as sanitized test fixtures and pushed down to `<repo>/tests/fixtures/real/` for parameterized Tier 2 integration tests.

---

## ⚖️ 6. GATE-02 Verification Checklist

- [ ] All 6 canonical test cases have clear inputs, triggers, and expected invariants.
- [ ] Multi-service Docker topology is defined and reproducible via `deploy/docker-compose.yml`.
- [ ] Automated test runner is authorable without manual human intervention.
- [ ] Database assertions inspect real authoritative storage (not ephemeral mocks).
- [ ] Human stakeholder has approved the suite before code authoring (`STEP-05`).
