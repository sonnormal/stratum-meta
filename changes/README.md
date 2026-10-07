# 📑 Stratum Change Archive

This directory maintains the immutable, historical records of all **Change Requests (CRs)** in the Stratum ecosystem.

---

## 🏷️ Identification Standard: `CR-YYaXXX`

Every change is assigned a unique ID following the format: **`CR-YYaXXX`**

* **`YY`**: 2-digit Year (`26` for 2026).
* **`a`**: Single **lowercase letter** denoting the month:
  * `a`=Jan, `b`=Feb, `c`=Mar, `d`=Apr, `e`=May, `f`=Jun
  * `g`=Jul, `h`=Aug, `i`=Sep, **`j`=Oct**, `k`=Nov, **`m`=Dec** *(skips `l` to avoid confusion with `1`)*
* **`XXX`**: 3-digit monthly sequence number (`001`, `002`, `003`...).

*Example:* **`CR-26j001`** is the 1st change request initiated in October 2026.

---

## 📂 Structure: Change Organization & Separation of Concerns

Stratum maintains a clean architectural boundary between **global change governance** (in `meta`) and **repo-scoped executable test contracts** (in specific repositories).

### 1. Global Change Archive (`meta/changes/`)

Every change maintains its overarching governance, intake record, evaluation, and supporting documentation in `meta`:

```text
changes/CR-YYaXXX-<short-title>/
├── request.md        # Master request intake, overview, status, and gate approval audit log (Gate 1, 2, 3)
├── evaluation.md     # STEP-03 / GATE-01 Report (Scope, Security, Cost-Benefit)
└── docs/             # Supporting docs (domain research, architecture notes, specifications) (optional)
```

* **`request.md`**: The master record for the change request. Captures the original stakeholder prompt (from Email, Zalo, or Viber), sender identity, timestamps, current lifecycle status, and the formal audit log for all 3 Human Governance Gates (`GATE-01`, `GATE-02`, `GATE-03`).
* **`evaluation.md`**: The comprehensive Change Evaluation Report (CER) authored during `STEP-03` to assess feasibility, cybersecurity (STRIDE), and cost-benefit before writing any code.
* **`docs/` (Supporting Docs)**: Each change may include supporting documentation, such as domain research, workflow diagrams, architectural spikes, external API documentation, or schemas.

### 2. Repo-Specific Test Scenarios & Fixtures (`<target-repo>/`)

Because early-phase verification strictly focuses on **Tier 1 (Unit Tests)** and **Tier 2 (Integration Tests)** that involve only a single repository in isolation, **`scenario.md`** and the **`fixtures/`** directory are located directly within the **specific repository** being changed:

```text
<target-repo>/changes/CR-YYaXXX-<short-title>/
├── scenario.md       # STEP-04 / GATE-02 Approved plain-language test scenarios & edge cases for this repo
└── fixtures/         # Sample test data, raw emails (.eml), mock payloads for Unit & Integration tests
```

* **`scenario.md`**: Plain-language, executable specifications of test scenarios, boundary conditions, and edge cases authored during `STEP-04` and reviewed at `GATE-02`.
* **`fixtures/`**: Repository-specific test fixtures, sample payloads, mock responses, and seed data consumed by Tier 1 and Tier 2 tests.

#### 📐 The Delta Principle for `scenario.md`
To keep `GATE-02` reviews focused and prevent redundant specification churn:
* **`scenario.md` is a Delta Specification:** In subsequent changes touching an existing feature, `scenario.md` documents **only the delta** (new, modified, or deprecated test scenarios introduced by that specific CR). It does **not** duplicate previously verified test scenarios.
* **Delta Categories:** Scenarios must be explicitly labeled:
  * `[NEW]`: Scenarios introducing newly added capabilities.
  * `[MODIFIED]`: Scenarios updating existing behaviors (with clear business rationale).
  * `[DEPRECATED]`: Scenarios retiring obsolete behaviors.
* **Regression Safety:** Past verified behaviors are defended by the **existing automated test suite** running in CI, not by re-copying markdown documentation.
* **Cumulative Specifications:** The living macro business capability is maintained cumulatively in `meta/features/FEAT-XXX.md`, while the full executable specification lives in `<repo>/tests/`.

---

## 🗂️ Change Register

| ID | Title | Status | Date | Folder |
| :--- | :--- | :--- | :--- | :--- |
| `CR-26j001` | Bank Email Ingestion & Cashflow Alerting | `INTAKE` | 2026-10-05 | [`CR-26j001-bank-cashflow-ingestion/`](CR-26j001-bank-cashflow-ingestion/) |
