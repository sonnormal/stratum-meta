# 📖 Stratum Global Glossary & Ubiquitous Language

> **Purpose:** Canonical dictionary of terms, acronyms, and concepts for human stakeholders and AI agents across all Stratum repositories.  
> **Location:** `meta/standards/glossary.md`  
> **Rule:** All agents and documentation must strictly use these definitions to prevent semantic drift.

---

## 🏛️ 1. Governance & Lifecycle (SDLC)

| Term | Full Name | Definition |
| :--- | :--- | :--- |
| **`CR`** | Change Request | A formal, auditable unit of evolution in Stratum, tracked under `meta/changes/CR-YYaXXX-<short-title>/`. Contains `request.md`, `evaluation.md`, and supporting docs. |
| **`CR-YYaXXX`** | Change ID Standard | Unique ID format: `YY` = 2-digit year (e.g. `26`), `a` = lowercase month letter (`a`=Jan...`j`=Oct, skipping `l`), `XXX` = 3-digit monthly sequence number. |
| **`CER`** | Change Evaluation Report | The analytical artifact produced in `STEP-03` evaluating scope, cybersecurity threats (STRIDE), and cost-benefit feasibility before any code is written. |
| **`HITL`** | Human-in-the-Loop | The governing architectural pattern where AI generates 100% of code, but humans retain strategic control via conversational review gates. |
| **`GATE-01`** | Value & Feasibility Gate | Human checkpoint: *"Why do it & is it worth it?"* Inspects `evaluation.md` via Email, Zalo, or Viber. |
| **`GATE-02`** | Contract & Test Scenario Gate | Human checkpoint: *"What exact behavior to build?"* Inspects plain-language specs, Tier 1/2 tests, AND the complete Tier 3 Acceptance Test Suite (`e2e_scenario.md`) before code synthesis. |
| **`GATE-03`** | User Acceptance Gate (UAT) | Human checkpoint: *"Does it work in reality?"* Inspects automated Tier 3 E2E report (`e2e_results_*.md`) of pre-approved acceptance suite and performs physical verification (e.g. mobile phone alert buzz) before sign-off. |
| **`request.md`** | Master Request Document | The primary record in a change folder containing the original stakeholder prompt, current lifecycle status, and the 3-gate audit trail. |

---

## 🏗️ 2. Architectural Concepts & Artifacts

| Term | Definition |
| :--- | :--- |
| **`Flow` (`flows/`)** | An evergreen, multi-repository sequence showing how events and data travel across services (e.g., *Email Ingress → Gateway → Service → Notification*). Contains both sequence choreography and payload dataflow. |
| **`Feature` (`features/`)** | A living functional specification describing *what* a capability does, its business rules, edge cases, and explicitly declaring *which repository implements it*. |
| **`Contract` (`contracts/`)** | The formal, machine-readable agreement defining binding mutual obligations between Producer and Consumer repositories (syntax + behavior + idempotency + error handling + breaking change guarantees). Single source of truth. |
| **`ADR`** | **Architectural Decision Record (`ADR-YYaXXX`):** An immutable decision capturing an ecosystem-wide standard (e.g. Docker, OrbStack, TDD policies) that all repositories must follow. |
| **`Supporting Docs`** | Domain research, architecture spikes, user flow diagrams, or reference specifications associated with a Change Request under `changes/.../docs/`. |

---

## 🧪 3. Testing Tiers & Verification

| Term | Definition |
| :--- | :--- |
| **`TDD`** | **Test-Driven Development:** Strict engineering workflow where automated tests are authored first (`Red`), approved at `GATE-02`, and then minimal code is synthesized (`Green`). |
| **`Tier 1 (Unit)`** | In-memory unit test (< 1ms). Tests algorithms, parsing, regex, and state transitions with **0 network calls and 0 disk access**. 100% mocked. |
| **`Tier 2 (Integration)`** | Seam integration test (2–5s) using real containerized databases/caches via **Testcontainers**. Runs in complete repository isolation. |
| **`Tier 3 (E2E)`** | Automated End-to-End test validating cross-service journeys across containerized services. Executed in `STEP-06` pre-flight before `GATE-03`. Stored in `stratum-meta/tests/e2e/`. |
| **`Seam`** | The boundary where application code connects to external infrastructure (database queries, event serialization, cache hits/misses). |
| **`Testcontainers`** | A library that automatically manages ephemeral Docker containers (Postgres, Redis) programmatically during test execution. |
| **`Test Assertion`** | The atomic verification of a single invariant (`assert a == b`). |
| **`Test Case`** | A set of preconditions, inputs, actions, expected results, and postconditions developed for a particular test condition (strictly agnostic to manual or automated execution; ISTQB / ISO 29119 standard). |
| **`Test Scenario`** | An end-to-end operational story or business journey spanning multiple steps and boundaries, from external trigger to final stakeholder outcome. |
| **`Test Fixture`** | The complete contextual baseline and test data required to execute one or more test cases deterministically (including sample payload files, mock responses, database seed records, and pre-allocated state). |
| **`Test Suite`** | A collection of test cases or test scenarios packaged for a specific execution objective (e.g. Tier 1 Suite, Tier 2 Suite, Tier 3 Acceptance Suite). |
| **`Acceptance Test Suite`** | A test suite specifically designed to verify that a system meets its specified acceptance criteria before authorization or release (ISTQB v4.0). Specified in `e2e_scenario.md`, executed by AI in Tier 3, and sampled by humans at `GATE-03`. |
| **`Smoke Test Suite`** | A selective subset of critical happy-path test cases executed to rapidly verify that core features and interfaces function before deeper testing (e.g. health checks, canonical happy path). |
| **`Regression Test Suite`** | A comprehensive multi-tier test suite executed after code changes to ensure that previously developed and verified capabilities remain defect-free across all tiers. |
| **`Production-Parity`** | UAT standard requiring maximum real components and real production channel data; synthetic simulation endpoints are strictly forbidden. |
| **`Fixture Loop`** | **E2E-to-Integration Fixture Feedback Loop:** The architectural process of capturing real payloads during E2E pre-flight execution, sanitizing them, and promoting them into permanent Tier 2 regression test fixtures. |
| **`scenario.md`** | The repository-scoped technical specification and executable test contract stored within the target repository (`<repo>/changes/CR-YYaXXX/scenario.md`). Combines internal technical scope, DB migrations, and Tier 1/2 tests. (Cross-service Tier 3 Acceptance Suites are specified in `stratum-meta/changes/CR-YYaXXX/e2e_scenario.md`). |
| **`fixtures/`** | Repository-specific directory containing test fixtures (sample `.eml` raw emails, mock JSON payloads, SQL seed rows) consumed by Tier 1 and Tier 2 tests. |

---

## 🌐 4. Infrastructure & Communication

| Term | Definition |
| :--- | :--- |
| **`meta`** | The central orchestration repository containing global architecture, SDLC lifecycle, change archives, flows, features, contracts, and ADRs. |
| **`gateway`** | The omnichannel perimeter edge adapter handling IMAP email polling, OAuth authentication, and webhook bridges for Zalo and Viber bots. |
| **`services/*`** | Focused domain microservices (e.g., `services/cashflow`, `services/billing`) executing business logic and database persistence. |
| **`web`** | The web application repository delivering dashboards, charts, and stakeholder user interfaces. |
| **`OrbStack`** | High-performance, lightweight container runtime for macOS (Mac Studio), replacing Docker Desktop for fast local containerized execution. |
| **`Omnichannel`** | The communication approach where stakeholder notifications, approvals, and commands are delivered simultaneously or interchangeably via Email, Zalo, and Viber. |
