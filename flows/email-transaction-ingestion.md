# FLOW-001: Inbound Email Transaction Ingestion & Alerting

> **Flow ID:** `FLOW-001`  
> **Status:** `ACTIVE`  
> **Trigger:** Polling bank transaction alert emails via IMAP/OAuth  
> **Participating Repositories:** [`stratum-gateway`](file:///Users/son/Projects/Stratum/stratum-gateway), [`stratum-services/vib-tracker`](file:///Users/son/Projects/Stratum/stratum-services)  
> **Relevant Contracts:** [`contracts/events/transaction_detected.v1.json`](../contracts/events/transaction_detected.v1.json)  
> **Related Features:** [`features/vib-transaction-alert.md`](../features/vib-transaction-alert.md)

---

## 📌 1. Overview & Objective

This flow automates the ingestion of financial alert emails sent by banks (starting with VIB). When an alert arrives, `stratum-gateway` parses the raw MIME email, normalizes the financial data, and emits a standard `TransactionDetectedEvent`. The domain service `stratum-services/vib-tracker` consumes the event, enforces idempotency, updates financial records in PostgreSQL, and routes an instant alert notification to the stakeholder via Zalo/Viber.

---

## 🗺️ 2. Cross-Repo Sequence Diagram (Workflow)

```mermaid
sequenceDiagram
    autonumber
    actor VIB as VIB Mail Server
    participant Gateway as stratum-gateway
    participant Bus as Internal Event Bus
    participant Service as stratum-services/vib-tracker
    actor User as Stakeholder (Zalo/Viber)

    VIB->>Gateway: New email in IMAP inbox
    Gateway->>Gateway: Fetch .eml, parse headers & regex body
    Gateway->>Bus: Emit TransactionDetectedEvent (v1)
    Bus->>Service: Consume TransactionDetectedEvent
    Service->>Service: Check event_id idempotency (PostgreSQL)
    Service->>Service: Persist transaction & recalculate daily sum
    Service-->>User: Dispatch push alert (Amount, Merchant, Balance)
```

---

## 🔄 3. Step-by-Step Execution & Data Transformation (Dataflow)

### Step 1: Raw Ingress & Parsing (`stratum-gateway`)
* **Input:** Raw RFC 5322 `.eml` payload from `vib.com.vn`.
* **Transform:** Regex extractor parses amount, currency, account mask, transaction type, and date.
* **Contract Output:** Canonical [`TransactionDetectedEvent` (v1)](../contracts/events/transaction_detected.v1.json).

### Step 2: Persistence & Idempotency (`stratum-services/vib-tracker`)
* **Input:** `TransactionDetectedEvent` (v1).
* **Processing:** 
  1. Checks if `event_id` or `raw_source_ref` already exists in PostgreSQL unique index.
  2. Commits transaction record in database.
  3. Formats conversational alert message.
* **Output:** Message sent to stakeholder's verified chat ID.

---

## 🛡️ 4. Failure Modes & Resilience

| Scenario | Handled By | Behavior |
| :--- | :--- | :--- |
| **Email is not a transaction alert** | `stratum-gateway` | Safely ignored; logs info without emitting event. |
| **Duplicate email retrieved from IMAP** | `stratum-services/vib-tracker` | Dropped gracefully via unique constraint on `raw_source_ref`. |
| **PostgreSQL container unreachable** | `stratum-services/vib-tracker` | Event stays on queue / retry buffer with exponential backoff. |
