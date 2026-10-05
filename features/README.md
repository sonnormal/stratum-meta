# ✨ Stratum Living Features Catalog

> **Purpose:** Living catalog of domain capabilities and functional specifications in the Stratum ecosystem.  
> **Location:** `meta/features/`  
> **Rule:** Every business capability must have a living specification document that states **what it does**, its **business rules**, and **which repository implements it**.

---

## 🎯 What is a Feature?

A **Feature** is a living specification of a domain capability from the stakeholder's perspective:
* **Scope:** It captures functional requirements, acceptance criteria, and edge cases.
* **Traceability:** It explicitly documents **which repository implements the code** (e.g. `Implemented in: services/cashflow`).
* **Evolution:** When a Change Request (CR) modifies how a feature works, the feature specification in this folder is updated to reflect the new truth.

---

## 🗂️ Feature Register

| ID | Title | Implementing Repository | Associated Flow |
| :--- | :--- | :--- | :--- |
| [`FEAT-001`](vib-transaction-alert.md) | Bank Transaction Ingestion & Cashflow Alerting | `services/cashflow` | [`FLOW-001`](../flows/email-transaction-ingestion.md) |

---

## 📝 Authoring a New Feature

To specify a new capability, copy the canonical template from [**`templates/feature.md`**](../templates/feature.md) and define the acceptance criteria, business rules, and implementing repository.
