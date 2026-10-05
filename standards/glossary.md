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
| **`GATE-02`** | Contract & Test Scenario Gate | Human checkpoint: *"What exact behavior to build?"* Inspects plain-language test scenarios (`scenario.md`) before code synthesis. |
| **`GATE-03`** | User Acceptance Gate (UAT) | Human checkpoint: *"Does it work in reality?"* Live verification on local/cloud container stack before operational sign-off. |
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
| **`Tier 3 (E2E)`** | End-to-End test validating full user journeys across all deployed services. Deferred during initial development until APIs stabilize. |
| **`Seam`** | The boundary where application code connects to external infrastructure (database queries, event serialization, cache hits/misses). |
| **`Testcontainers`** | A library that automatically manages ephemeral Docker containers (Postgres, Redis) programmatically during test execution. |
| **`scenario.md`** | The repository-scoped technical specification and executable test contract stored within the target repository (`<repo>/changes/CR-YYaXXX/scenario.md`). Combines internal technical scope, DB migrations, and Tier 1 & Tier 2 test scenarios. |
| **`fixtures/`** | Repository-specific directory containing sample test data (sample `.eml` raw emails, mock JSON payloads, SQL seed rows) consumed by Tier 1 and Tier 2 tests. |

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
