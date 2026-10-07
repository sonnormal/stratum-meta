# 🧪 Stratum Repository Specification & Test Scenarios

> **Document Type:** Repo-Specific Technical Specification & Executable Acceptance Tests (`STEP-04` Red Phase)  
> **Target Checkpoint:** `GATE-02` (Contract & Test Scenario Gate)  
> **Location:** `<target-repo>/changes/CR-YYaXXX-<short-title>/scenario.md`  
> **Scope:** Strictly isolated to the **DELTA** of this Change Request (Tier 1 Unit and Tier 2 Integration tests). Existing behaviors are guarded by existing regression test suites. Tag scenarios as `[NEW]`, `[MODIFIED]`, or `[DEPRECATED]`.

---

## 📌 1. Target Repository Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-YYaXXX` (e.g. `CR-26j001`) |
| **Target Repository** | `services/<service>` / `gateway` / `web` |
| **Feature Fulfillments** | [Link to `meta/features/FEAT-XXX...`](file:///Users/son/Projects/Stratum/meta/features/) |
| **Associated Flow** | [Link to `meta/flows/FLOW-XXX...`](file:///Users/son/Projects/Stratum/meta/flows/) |
| **Bound Contracts** | [Link to `meta/contracts/...`](file:///Users/son/Projects/Stratum/meta/contracts/) |
| **Author** | AI QA / Architect Agent |
| **Status** | `PENDING_GATE_02_APPROVAL` |
| **Master CR Record** | [Link to `meta/changes/CR-YYaXXX-.../request.md`](file:///Users/son/Projects/Stratum/meta/changes/) |

---

## 📐 2. Technical Scope & Implementation Invariants

*Defines what THIS repository implements internally before authoring tests and code.*

### 2.1 Modules & Components to Modify / Create
* **Packages / Files:** *e.g., `src/domain/parser.py`, `src/api/routes.py`*
* **Public / Internal Interfaces:** *e.g., `TransactionRepository`, `AlertNotifier`*

### 2.2 Data Persistence & Schema Migrations (If Applicable)
* **Tables / Collections:** *e.g., `vib_transactions`*
* **Indexes & Constraints:** *e.g., Composite unique key on `(bank_code, raw_source_ref)`*
* **Migration Strategy:** *Non-breaking additive migration script (e.g. `0002_add_transaction_tag.sql`)*

### 2.3 Dependencies & Configuration
* **New Libraries:** *Zero unless justified in CER.*
* **Environment Variables:** *e.g., `DATABASE_URL`, `ORB_DOCKER_SEAM_PORT`*

---

## 🔬 3. Tier 1: Unit Test Scenarios (In-Memory Isolation)

*Zero network, zero disk. Tests pure domain logic, mathematical boundary conditions, parsing regex, and error mappings.*

### Scenario 1.1: [Descriptive Scenario Name]
* **Given:** [Precondition / input state / mock configuration]
* **When:** [Action / method invocation]
* **Then:** [Expected return value or exception thrown]
* **Edge Cases Considered:**
  - *e.g., Null / empty string handling*
  - *e.g., Unicode or malformed characters*
  - *e.g., Integer boundary / overflow limits*

### Scenario 1.2: [Negative / Error Scenario Name]
* **Given:** ...
* **When:** ...
* **Then:** ...

---

## 🔌 4. Tier 2: Integration Test Scenarios (Containerized Sandbox)

*Uses Testcontainers (PostgreSQL, Redis, WireMock). Asserts persistence seams, unique constraints, transactional rollbacks, and event emissions.*

### Scenario 2.1: [Database Persistence & Unique Constraint Rollback]
* **Given:** A running PostgreSQL container initialized with latest migrations.
* **When:** An entity with a duplicate unique key is saved.
* **Then:** The repository cleanly throws `DuplicateKeyException` and rolls back partial state without table corruption.

### Scenario 2.2: [Contract Event Serialization & Bus Emission]
* **Given:** A valid internal domain state transition.
* **When:** The service emits an event to the local message broker.
* **Then:** The serialized payload strictly validates against the JSON Schema in `meta/contracts/`.

---

## 📂 5. Test Fixtures Inventory (`fixtures/`)

*Repo-specific sample data, raw inputs, and mock payloads located in `<target-repo>/changes/CR-YYaXXX-<short-title>/fixtures/`:*

| Fixture File | Type | Used In Scenario | Description |
| :--- | :--- | :--- | :--- |
| `fixtures/sample_email.eml` | Raw Email | Scenario 1.1 | Real-world RFC 5322 email with transaction headers |
| `fixtures/mock_webhook_payload.json` | JSON | Scenario 1.2 | Raw webhook payload from gateway |
| `fixtures/db_seed.sql` | SQL | Scenario 2.1 | Pre-seeded baseline rows for containerized DB tests |

---

## ⚖️ 6. GATE-02 Verification Checklist

- [ ] Technical scope in Section 2 respects repository boundaries and bound contracts.
- [ ] Tier 1 tests have zero I/O and run in < 1ms.
- [ ] Tier 2 tests execute against ephemeral Testcontainers without cross-repo dependencies.
- [ ] All test fixtures are sanitized (zero real credentials, production tokens, or PII).
- [ ] Automated test suites fail cleanly (`Red` state) awaiting code synthesis (`STEP-05`).
