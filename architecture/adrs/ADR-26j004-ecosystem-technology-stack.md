# ADR-26j004: Standardized Ecosystem Technology Stack

> **Decision ID:** `ADR-26j004`  
> **Status:** `ACCEPTED`  
> **Date:** `2026-10-06`  
> **Applies to:** `All Repositories` (`gateway`, `services/*`, `web`)  
> **Related CR:** `CR-26j001`

---

## 📌 1. Context & Problem Statement

Stratum operates as an autonomous, multi-repository platform with 100% AI-generated code governed by strict Test-Driven Development (TDD).

Without an explicit ecosystem-wide technology standard, AI agents and developers will inevitably introduce:
* **Toolchain Fragmentation:** Juggling multiple package managers, linters, and runtime engines across repositories.
* **Paradigm Mismatches:** Conflating big-data lakehouses (OLAP) with transactional databases (OLTP).
* **Testability Friction:** Divergent test runners that break Tier 1 (< 1ms in-memory) and Tier 2 (isolated Testcontainers) invariants.

The ecosystem requires an authoritative standard covering all six architectural tiers of the software stack.

---

## ⚖️ 2. Decision: The 6-Tier Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 6-TIER STRATUM STACK                          │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Backend Language & Typing   │ Python 3.12+ (Ruff + Mypy)            │
│ 2. Contract & Schema Engine    │ Pydantic v2                           │
│ 3. API & Web Service Framework │ FastAPI (Async ASGI)                  │
│ 4. Relational Storage & DDL    │ PostgreSQL 16+ & Alembic (SQLAlchemy) │
│ 5. Automated TDD Harness       │ pytest + testcontainers-python        │
│ 6. Frontend Application Stack  │ TypeScript + React + Vite             │
└────────────────────────────────┴───────────────────────────────────────┘
```

### 2.1 Backend Language & Toolchain (`gateway`, `services/*`)
* **Standard:** **Python 3.12+** with strict type annotations.
* **Linter & Formatter:** **`ruff`** for sub-second formatting and linting.
* **Static Type Checker:** **`mypy`** in strict mode.

### 2.2 Data Modeling & Schema Contracts
* **Standard:** **Pydantic v2** (Rust-backed core).
* **Role:** Enforces data integrity at runtime and maps directly (1-to-1) to canonical JSON Schemas in `meta/contracts/`.

### 2.3 API & Web Service Framework
* **Standard:** **FastAPI**.
* **Role:** Lightweight, asynchronous ASGI web framework with native OpenAPI schema generation and dependency injection.

### 2.4 Relational Persistence & Migrations (OLTP)
* **Standard:** **PostgreSQL 16+** with **Alembic** and **SQLAlchemy**.
* **Role:** Authoritative operational database for account movements, balances, and idempotency locks. Variable raw metadata stored in native `JSONB` columns with GIN indexing.

### 2.5 Automated Testing Harness (Strict TDD)
* **Standard:** **`pytest`** and **`testcontainers-python`**.
* **Role:** Tier 1 Unit tests run in-memory (< 1ms, 0 I/O); Tier 2 Integration tests execute against isolated ephemeral PostgreSQL containers in OrbStack.

### 2.6 Frontend Web Application (`web/`)
* **Standard:** **TypeScript + React + Vite**.
* **Role:** Fast, client-side dashboard consuming backend REST APIs defined by canonical OpenAPI contracts.

---

## 💡 3. Alternatives Considered & Rationale Across All 6 Tiers

### Tier 1: Backend Language

| Candidate | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Go (Golang)** | Single 15MB binary, 15MB RAM, instant boot, high concurrency. | More boilerplate for complex JSON validation; MIME parsing of messy bank emails requires third-party libraries. | **Deferred:** Adopting Go alongside Python on Day 1 imposes the "Polyglot Tax" (two toolchains, two CI setups, two test harnesses). `gateway` may be rewritten in Go in a future CR once contracts stabilize. |
| **TypeScript / Node.js** | Single language across backend and `web`. | `node_modules` dependency bloat, async unhandled promise rejection traps, weaker standard data parsing libraries. | **Rejected:** Python offers superior AI code generation density and native Ollama SDK integration. |
| **Rust** | Maximum execution speed, zero memory bugs. | Steep compilation overhead slows down TDD Red/Green inner-loop. | **Rejected:** Massive over-engineering for I/O-bound email and financial persistence services. |

### Tier 2: Contract & Schema Validation

| Candidate | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Marshmallow / Cerberus** | Pure Python schema validation. | Slower (Python-native); lacks bidirectional JSON Schema export and OpenAPI compatibility. | **Rejected:** Pydantic v2 is 5–20x faster (Rust core) and is the industry standard for FastAPI and Ollama structured outputs. |
| **Raw Python Dictionaries** | Zero external dependencies. | Zero runtime type guarantees; silent schema drift bugs; high risk of AI hallucinations. | **Rejected:** Violates strict contract invariants. |

### Tier 3: API & Web Service Framework

| Candidate | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Flask** | Minimal, simple. | Synchronous by default; lacks native type-hint validation; requires separate plugins for OpenAPI docs. | **Rejected:** Lacks modern async ASGI performance and built-in Pydantic integration. |
| **Django / Django REST** | "Batteries-included" admin and ORM. | Monolithic architecture; heavy ORM tightly coupled to Django runtime; fights decoupled microservices. | **Rejected:** Monolithic antipattern for lightweight, independent microservices. |

### Tier 4: Database & Storage (OLTP)

| Candidate | Category | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- | :--- |
| **Apache Iceberg + MinIO** | OLAP Lakehouse | Open table format for petabyte-scale analytics and Trino/DuckDB scans. | **Zero write-time unique constraints.** High small-file metadata overhead for single-row writes. Requires catalog, object storage, and compaction daemons. | **Rejected for OLTP:** Wrong tool for operational transactional services. Reserved for future analytical archiving. |
| **SQLite** | Embedded SQL | Zero daemon, single file. | Locks entire file on write (`SQLITE_BUSY`). Incompatible with ephemeral Kubernetes pods (requires persistent volume mounting). | **Rejected:** Fails concurrency and Kubernetes cloud-native portability. |
| **MongoDB / DocumentDB** | NoSQL Document | Flexible schema. | Weaker relational integrity; multi-document ACID transactions require complex coordination; lacks declarative composite constraints. | **Rejected:** Relational PostgreSQL with `JSONB` provides the same flexibility with stronger ACID guarantees. |

### Tier 5: Automated Testing Harness

| Candidate | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Python `unittest`** | Standard library, zero install. | Verbose xUnit class boilerplate; awkward assertion syntax (`self.assertEqual`); lacks modern fixture dependency injection. | **Rejected:** `pytest` is vastly more expressive, faster, and standard in Python engineering. |
| **Mock-Only Testing (No Testcontainers)** | Blistering fast. | Never verifies real database queries, schema constraints, or transactional rollbacks. Bugs escape to production. | **Rejected:** Violates Stratum's Tier 2 seam testing mandate. |

### Tier 6: Frontend Application Stack

| Candidate | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Next.js (App Router)** | Server-side rendering (SSR), SEO. | Complex server/client component boundary rules; heavy Node.js runtime requirement; vendor lock-in tendencies. | **Rejected:** A private financial dashboard does not need public SEO. A static SPA on Vite is simpler, faster, and cheaper to host. |
| **Vue / Angular / Svelte** | Component frameworks. | Fragmented ecosystem tooling compared to React; lower training data density for autonomous AI coding agents. | **Rejected:** React + TypeScript has the highest AI code synthesis accuracy and component ecosystem maturity. |

---

## 🛡️ 4. Consequences & Multi-Repo Enforcement

### Positive Consequences
* **Unified Developer Experience:** Every backend service follows the exact same structure: `pyproject.toml`, `ruff`, `mypy`, `FastAPI`, `Pydantic`, and `pytest`.
* **Zero Double-Counting:** PostgreSQL handles concurrent write collisions atomically via `ON CONFLICT DO NOTHING`.
* **100% Hermetic Tests:** `testcontainers-postgres` boots in 1.2s on OrbStack for rapid Tier 2 verification.
* **Deterministic Agent Synthesis:** AI agents work within a well-bounded, predictable stack with maximum code-generation accuracy.

### Compliance & Verification
* Every repository must pass `ruff check`, `mypy --strict`, and `pytest` with 100% assertions passing before advancing through `GATE-02` and `GATE-03`.
