# 📋 Stratum Document Templates

> **Purpose:** Canonical template registry for all governance, change lifecycle, architecture, and specification documents in the Stratum ecosystem.  
> **Location:** `stratum-meta/templates/`  
> **Naming Standard:** Every template is named **identically to the file or artifact it produces** (no redundant `_template` suffix).

---

## 🗂️ Template Catalog

| Template File | Output Target Location | Lifecycle Gate / Role | Purpose |
| :--- | :--- | :--- | :--- |
| [**`request.md`**](request.md) | `changes/CR-YYaXXX-<title>/request.md` | Intake → `GATE-01/02/03` | Master change request record, original stakeholder prompt, status, and 3-gate audit trail. |
| [**`evaluation.md`**](evaluation.md) | `changes/CR-YYaXXX-<title>/evaluation.md` | `STEP-03` → `GATE-01` | Change Evaluation Report (CER): Scope, STRIDE cybersecurity threat model, cost-benefit analysis. |
| [**`scenario.md`**](scenario.md) | `<target-repo>/changes/CR-YYaXXX-<title>/scenario.md` | `STEP-04` → `GATE-02` | Repo Technical Spec & Test Scenarios: internal scope, DB schema, Tier 1 (Unit) and Tier 2 (Integration) tests. |
| [**`flow.md`**](flow.md) | `flows/FLOW-XXX-<title>.md` | Architecture Spec | Cross-repo multi-service interaction, sequence diagram, and payload dataflow pipeline. |
| [**`feature.md`**](feature.md) | `features/FEAT-XXX-<title>.md` | Architecture Spec | Living domain capability specification, acceptance criteria, and implementing repository mapping. |
| [**`adr.md`**](adr.md) | `architecture/adrs/ADR-YYaXXX-<title>.md` | Architecture Standard | Architectural Decision Record: immutable cross-repo technical invariants and standards. |

---

## 🛠️ Usage Instructions

When generating a new document for a change or architecture evolution, copy the corresponding template directly into its target destination:

```bash
# Example 1: Initiating a Change Evaluation Report (STEP-03)
cp templates/evaluation.md changes/CR-26j001-vib-tracker/evaluation.md

# Example 2: Authoring Test Scenarios for a specific service (STEP-04)
cp templates/scenario.md ../stratum-services/vib-tracker/changes/CR-26j001-vib-tracker/scenario.md

# Example 3: Documenting a new multi-repo flow
cp templates/flow.md flows/email-transaction-ingestion.md
```
