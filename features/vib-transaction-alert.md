# FEAT-001: Bank Transaction Ingestion & Cashflow Alerting

> **Feature ID:** `FEAT-001`  
> **Status:** `ACTIVE`  
> **Implementing Repository:** `services/cashflow`  
> **Supporting Ingress Repo:** `gateway`  
> **Related Flow:** [`flows/email-transaction-ingestion.md`](../flows/email-transaction-ingestion.md)  
> **Relevant Contracts:** [`contracts/events/transaction_detected.v1.json`](../contracts/events/transaction_detected.v1.json)

---

## 📌 1. Capability Overview

The **Bank Transaction Ingestion & Cashflow Alerting** feature monitors bank transaction alert emails (starting with VIB), parses debit/credit amounts, timestamps, and remaining account balances, persists cashflow movements in a local PostgreSQL database, and delivers immediate push alerts to the stakeholder over Zalo/Viber.

---

## 🎯 2. Acceptance Criteria (User Stories)

* **As a:** Stakeholder managing personal finances and bank accounts
* **I want to:** Receive an instantaneous conversational notification whenever a bank account incurs a transaction
* **So that:** I have immediate visibility over debits, credits, and current account balances without logging into banking apps.

### Concrete Criteria
- [ ] Parses debit transactions (e.g. `GD: -50,000VND`, merchant name, remaining balance).
- [ ] Parses credit transactions (e.g. `GD: +1,200,000VND`, sender name).
- [ ] Ignores promotional or non-transaction emails from the bank.
- [ ] Strict idempotency: Duplicate emails received via IMAP never create duplicate cashflow records or duplicate push alerts.

---

## 📋 3. Domain Rules & Edge Cases

1. **Currency Handling:** Default currency is `VND`. Amounts must be stored as decimal/bigint (avoid floating point errors).
2. **Account Masking:** The bank account number must always be masked (e.g. `*4321`) in logs and conversational notifications for privacy.
3. **Balance Tracking:** If the email reports available balance, the latest account balance is updated; if not, balance remains unchanged.
4. **Idempotency Key:** Composite unique index on `(bank_code, raw_source_ref)` prevents double-counting.

---

## 📦 4. Implementation & Repository Mapping

* **Implementing Service:** `services/cashflow`
* **Storage:** PostgreSQL table `account_movements` (managed by `services/cashflow`)
* **Inbound Event:** Consumes `TransactionDetectedEvent` (v1) from internal bus.
* **Alert Delivery:** Dispatches message to `gateway` conversational bot webhook.
