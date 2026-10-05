# 📑 Stratum Change Request (CR) Master Record

> **Document Type:** Master Change Request Record & Governance Audit Log  
> **Lifecycle:** Maintained continuously across `GATE-01`, `GATE-02`, and `GATE-03`.  
> **Location:** `meta/changes/CR-YYaXXX-<short-title>/request.md`

---

## 📌 1. Request Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-YYaXXX` (e.g. `CR-26j001`) |
| **Title** | *Brief descriptive title of the change* |
| **Requester** | Human Stakeholder (Verified Email / Verified Chat ID) |
| **Intake Channel** | Email / Zalo / Viber |
| **Created Timestamp** | `YYYY-MM-DD HH:MM:SS UTC+7` |
| **Current Lifecycle State** | `INTAKE` / `EVALUATION` / `TDD_RED` / `TDD_GREEN` / `UAT` / `COMPLETED` / `REJECTED` |

---

## 📥 2. Stakeholder Request Intake

### Original Inbound Prompt
```text
[Paste the raw stakeholder prompt as received from Email, Zalo, or Viber]
```

### Initial Intent & Objectives
* **Core Problem / Need:** *What problem is being solved or what capability is requested?*
* **Target Outcome:** *What is the expected behavior once released?*
* **Urgency / Priority:** *Standard / Expedited / Critical Bugfix*

---

## 📚 3. Supporting Documentation

*Each change in `meta` may include supporting documentation to provide deeper domain or technical context:*

| Document | Path / Link | Description |
| :--- | :--- | :--- |
| **Change Evaluation Report (CER)** | [`evaluation.md`](evaluation.md) | `STEP-03` / `GATE-01` Scope, Security & Cost-Benefit assessment |
| **Architecture / Spike Notes** | `docs/architecture-spike.md` | *(Optional)* Technical design spike, component diagrams |
| **Domain Research / References** | `docs/domain-research.md` | *(Optional)* Industry rules, API documentation, format specifications |
| **Data Contracts / Schemas** | `docs/schemas/` | *(Optional)* Protobuf, OpenAPI, or DB schema definitions |

---

## 📦 4. Affected Repositories & Execution Scope

*Unit and integration tests are isolated per repository. Test scenarios and fixtures live in the target repositories below:*

| Repository | Role in Change | Branch / PR | Target Repo Scenario Spec |
| :--- | :--- | :--- | :--- |
| `services/<service>` | Core business logic & persistence | `cr-YYaXXX-...` | [`scenario.md` in target repo](<target-repo>/changes/CR-YYaXXX-<short-title>/scenario.md) |
| `gateway` | Ingress ingestion & payload parsing | `cr-YYaXXX-...` | [`scenario.md` in target repo](<target-repo>/changes/CR-YYaXXX-<short-title>/scenario.md) |

---

## ⚖️ 5. Three Human Governance Gates Audit Log

### 🛡️ GATE-01: Value & Feasibility Gate
* **Core Question:** *"Why do it & is it worth it?"*
* **Inspected Artifact:** [`evaluation.md`](evaluation.md) (CER)
* **Status:** `PENDING / APPROVED / REJECTED / REVISED`
* **Decision Timestamp:** `YYYY-MM-DD HH:MM:SS UTC+7`
* **Decided By:** `[Stakeholder Identity]` via `[Email / Zalo / Viber]`
* **Reviewer Directives / Notes:**
  > *[Record stakeholder decision notes or scope constraints here]*

---

### 🛡️ GATE-02: Contract & Test Scenario Gate
* **Core Question:** *"What exact behavior to build?"*
* **Inspected Artifacts:** `scenario.md` and `fixtures/` in target repositories
* **Status:** `PENDING / APPROVED / REJECTED / REVISED`
* **Decision Timestamp:** `YYYY-MM-DD HH:MM:SS UTC+7`
* **Decided By:** `[Stakeholder Identity]` via `[Email / Zalo / Viber]`
* **Reviewer Directives / Notes:**
  > *[Record stakeholder feedback on test scenarios and edge cases here]*

---

### 🛡️ GATE-03: User Acceptance Gate (UAT Sign-off)
* **Core Question:** *"Does it work in reality?"*
* **Inspected Environment:** Live container stack on OrbStack / Cloud UAT
* **Status:** `PENDING / APPROVED / REJECTED / REVISED`
* **Decision Timestamp:** `YYYY-MM-DD HH:MM:SS UTC+7`
* **Decided By:** `[Stakeholder Identity]` via `[Email / Zalo / Viber]`
* **Verification Checklist:**
  - [ ] Live container health check verified (`200 OK`)
  - [ ] Real / sample data verified end-to-end
  - [ ] Conversational notifications received on target channels
* **Reviewer Directives / Notes:**
  > *[Record stakeholder UAT sign-off notes or required revisions here]*
