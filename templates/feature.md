# FEAT-XXX: [Descriptive Feature Title]

> **Feature ID:** `FEAT-XXX`  
> **Status:** `ACTIVE` / `PLANNED` / `DEPRECATED`  
> **Implementing Repository:** `stratum-services/<service>` (or `stratum-gateway`)  
> **Related Flow:** [`flows/FLOW-XXX-...`](../flows/)  
> **Relevant Contracts:** [`contracts/events/...`](../contracts/)

---

## 📌 1. Capability Overview

*What does this feature provide to the stakeholder or system? Describe the high-level business capability.*

---

## 🎯 2. Acceptance Criteria (User Stories)

* **As a:** Stakeholder
* **I want to:** *[Action / capability]*
* **So that:** *[Value / outcome]*

### Concrete Verification Criteria
- [ ] Criterion 1: Given X, when Y, then Z.
- [ ] Criterion 2: Negative test / edge case handled gracefully.

---

## 📋 3. Domain Rules & Edge Cases

1. **Rule 1 (Data Validation):** *Constraints, bounds, mandatory fields.*
2. **Rule 2 (Idempotency):** *How duplicates are identified and discarded.*
3. **Rule 3 (Formatting / Presentation):** *How data is rendered in chat / emails.*

---

## 📦 4. Implementation & Repository Mapping

* **Primary Codebase:** `stratum-services/<service>`
* **Data Persistence:** Table schema / entity definitions.
* **Inbound Contract:** [`contracts/events/...`](../contracts/)
* **Outbound Contract / Notification:** Notification format / Webhook.
