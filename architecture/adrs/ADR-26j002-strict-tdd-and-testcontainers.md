# ADR-26j002: Strict TDD and Isolated Testcontainers for Tier 2 Tests

> **Decision ID:** `ADR-26j002`  
> **Status:** `ACCEPTED`  
> **Date:** `2026-10-01`  
> **Applies to:** `services/*`, `gateway`, `web`  
> **Related CR:** `CR-26j001`

---

## 📌 1. Context & Problem Statement

Stratum code is 100% synthesized by AI agents. Code cannot be trusted without automated verification written *before* implementation. Furthermore, in a decoupled multi-repo architecture, running tests for Service A should not depend on a running Service B.

---

## ⚖️ 2. Decision

1. **Strict TDD Order:** Automated tests must be authored first (`Red` state), approved at `GATE-02`, before minimal code is synthesized (`Green` state).
2. **Tier 1 (Unit Tests):** Pure domain logic and parsing must be tested in-memory with 0 network calls and 0 disk access.
3. **Tier 2 (Integration Tests):** Persistence and message seams must use **Testcontainers** (ephemeral programmatic Docker containers).
4. **Zero Cross-Repo Deadlocks:** Repositories must run Tier 2 tests in complete isolation. Sibling services or external third-party APIs must be simulated via mock contracts (e.g. WireMock), never live network calls to sibling repos.
5. **Colocated Scenarios & Fixtures:** `scenario.md` and `fixtures/` are stored directly within the target repository (`<repo>/changes/CR-YYaXXX/`) to ensure self-contained test execution.

---

## 🛡️ 3. Consequences & Multi-Repo Enforcement

* **Enforcement:** PRs with missing unit/integration tests or broken red/green cycles are rejected at `GATE-02`.
* **Reliability:** Every repository can run its full test suite offline without orchestrating the rest of the Stratum stack.
