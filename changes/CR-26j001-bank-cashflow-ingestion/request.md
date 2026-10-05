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
| **Requester** | Human Stakeholder |
| **Intake Channel** | Conversational Steering / Direct Intent |
| **Created Timestamp** | `2026-10-05 21:00:00 UTC+7` |
| **Current Lifecycle State** | `INTAKE` (Ready for Evaluation) |

---

## 📥 2. Stakeholder Request Intake

### Original Inbound Prompt
```text
Automate the ingestion of bank transaction alert emails (starting with VIB), parse debit/credit amounts and account balance movements, persist them in our cashflow domain service, and deliver instantaneous conversational push alerts to stakeholder over Zalo/Viber.
```

### Initial Intent & Objectives
* **Core Problem / Need:** Stakeholder needs real-time visibility over bank account balance movements (debits, credits, settlements, cashouts) without logging into individual bank mobile apps.
* **Target Outcome:** 
  1. `gateway` polls and parses bank alert emails, publishing canonical `TransactionDetectedEvent` (v1).
  2. `services/cashflow` consumes events, verifies idempotency, updates `account_movements` and account balances in PostgreSQL.
  3. `gateway` dispatches formatted conversational alerts to the stakeholder's verified Zalo/Viber chat.
* **Urgency / Priority:** Standard (Foundational Platform Capability).

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
| `services/cashflow` | Account movement persistence, balance updates & idempotency | `cr-26j001-cashflow-baseline` | [`scenario.md` in target repo](services/cashflow/changes/CR-26j001-bank-cashflow-ingestion/scenario.md) |
| `gateway` | Inbound IMAP email polling & outbound Zalo/Viber dispatch | `cr-26j001-gateway-ingestion` | [`scenario.md` in target repo](gateway/changes/CR-26j001-bank-cashflow-ingestion/scenario.md) |

---

## ⚖️ 5. Three Human Governance Gates Audit Log

### 🛡️ GATE-01: Value & Feasibility Gate
* **Core Question:** *"Why do it & is it worth it?"*
* **Inspected Artifact:** [`evaluation.md`](evaluation.md) (CER)
* **Status:** `PENDING`
* **Decision Timestamp:** `—`
* **Decided By:** `—`
* **Reviewer Directives / Notes:**
  > *Awaiting stakeholder review of evaluation.md.*

---

### 🛡️ GATE-02: Contract & Test Scenario Gate
* **Core Question:** *"What exact behavior to build?"*
* **Inspected Artifacts:** `scenario.md` and `fixtures/` in target repositories
* **Status:** `PENDING`
* **Decision Timestamp:** `—`
* **Decided By:** `—`
* **Reviewer Directives / Notes:**
  > *Unlocks after GATE-01 approval upon authoring STEP-04 Red test scenarios.*

---

### 🛡️ GATE-03: User Acceptance Gate (UAT Sign-off)
* **Core Question:** *"Does it work in reality?"*
* **Inspected Environment:** Live container stack on OrbStack / Docker
* **Status:** `PENDING`
* **Decision Timestamp:** `—`
* **Decided By:** `—`
* **Verification Checklist:**
  - [ ] Live container health checks verified (`200 OK` on `/healthz`)
  - [ ] Sample `.eml` bank emails parsed and persisted accurately
  - [ ] Duplicate emails discarded with zero duplicate balance updates
  - [ ] Conversational notification delivered on target chat channels
* **Reviewer Directives / Notes:**
  > *Pending development and container deployment in STEP-06.*
