# FEAT-001: VIB Email Transaction Ingestion & Alerting

> **Feature ID:** `FEAT-001`  
> **Status:** `ACTIVE`  
> **Implementing Repository:** [`stratum-services/vib-tracker`](file:///Users/son/Projects/Stratum/stratum-services)  
> **Supporting Ingress Repo:** [`stratum-gateway`](file:///Users/son/Projects/Stratum/stratum-gateway)  
> **Related Flow:** [`flows/email-transaction-ingestion.md`](../flows/email-transaction-ingestion.md)  
> **Relevant Contracts:** [`contracts/events/transaction_detected.v1.json`](../contracts/events/transaction_detected.v1.json)

---

## 📌 1. Capability Overview

The **VIB Transaction Ingestion & Alerting** feature monitors bank transaction emails from Vietnam International Bank (VIB), parses debit/credit amounts, timestamps, and remaining balances, persists transactions in a local PostgreSQL database, and delivers immediate push alerts to the stakeholder over Zalo/Viber.

---

## 🎯 2. Acceptance Criteria (User Stories)

* **As a:** Stakeholder managing personal finances
* **I want to:** Receive an instantaneous conversational notification whenever my VIB account incurs a transaction
* **So that:** I have immediate visibility over debits, credits, and remaining balance without logging into bank apps.

### Concrete Criteria
- [ ] Parses debit transactions (e.g. `GD: -50,000VND`, merchant name, remaining balance).
- [ ] Parses credit transactions (e.g. `GD: +1,200,000VND`, sender name).
- [ ] Ignores promotional or non-transaction emails from VIB.
- [ ] Strict idempotency: Duplicate emails received via IMAP never create duplicate database rows or duplicate push alerts.

---

## 📋 3. Domain Rules & Edge Cases

1. **Currency Handling:** Default currency is `VND`. Amounts must be stored as decimal/bigint (avoid floating point errors).
2. **Account Masking:** The bank account number must always be masked (e.g. `*4321`) in logs and conversational notifications for privacy.
3. **Balance Tracking:** If the email reports available balance, the latest balance is updated; if not, balance remains unchanged.
4. **Idempotency Key:** Composite unique index on `(bank_code, raw_source_ref)` prevents double-counting.

---

## 📦 4. Implementation & Repository Mapping

* **Implementing Service:** `stratum-services/vib-tracker`
* **Storage:** PostgreSQL table `vib_transactions`
* **Inbound Event:** Consumes `TransactionDetectedEvent` (v1) from internal bus.
* **Alert Delivery:** Dispatches message to `stratum-gateway` conversational bot webhook.
