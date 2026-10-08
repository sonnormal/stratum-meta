# 🔄 Stratum System Flows

> **Purpose:** Living catalog of cross-repository dataflows and interaction choreographies in the Stratum ecosystem.  
> **Location:** `meta/flows/`  
> **Rule:** Every multi-service interaction must have an evergreen flow document that evolves as the system grows.

---

## 🎯 What is a Flow?

A **Flow** documents how data and events move across multiple independent repositories to achieve an end-to-end outcome.

Unlike ephemeral tickets or task branches, **flows are evergreen**:
* When a new service or processing step is introduced via a Change Request (CR), the corresponding flow document is updated.
* Each flow document integrates two complementary views:
  1. **Choreography (The Workflow):** Sequence diagram of service calls, events, and retry policies.
  2. **Data Transformation (The Dataflow):** How raw data shapes evolve across boundaries, mapped to formal [Contracts](../contracts/).

---

## 🗂️ Flow Register

| ID | Title | Primary Repositories Involved | Relevant Contracts |
| :--- | :--- | :--- | :--- |
| [`FLOW-001`](email-transaction-ingestion.md) | Inbound Email Transaction Ingestion & Alerting | `gateway`, `services/cashflow` | `transaction_detected.v1.json` |

---

## 📝 Authoring a New Flow

To document a new cross-repo interaction, copy the canonical template from [**`templates/flow.md`**](../templates/flow.md) and specify participating repositories, sequence diagrams, and error handling.
