# 🏛️ Stratum System Architecture

> **Purpose:** Authoritative blueprints, system topology, container network design, and Architectural Decision Records (ADRs) for the Stratum ecosystem.  
> **Location:** `meta/architecture/`  
> **Audience:** Human stakeholders, system architects, and autonomous AI development agents.

---

## 🧭 Navigation & Core Documents

| Document | Scope | Purpose |
| :--- | :--- | :--- |
| [**`overview.md`**](overview.md) | **System Architecture Landscape** | The macro blueprint: C4 context, container topology, network isolation zones, bounded contexts, and end-to-end data pipelines. |
| [**`adrs/`**](adrs/README.md) | **Architectural Decision Records** | Chronological, immutable records capturing why specific technologies, runtimes, and engineering invariants were adopted. |

---

## 🧱 Architectural Foundations at a Glance

1. **Autonomous SDLC:** 100% AI-generated code governed by 3 Human-in-the-Loop review gates ([`standards/sdlc.md`](../standards/sdlc.md)).
2. **Containerized Portability:** OrbStack locally, Kubernetes in production ([ADR-26j001](adrs/ADR-26j001-containerized-local-runtime.md)).
3. **Strict TDD:** Tier 1 in-memory unit tests + Tier 2 isolated Testcontainers ([ADR-26j002](adrs/ADR-26j002-strict-tdd-and-testcontainers.md)).
4. **Local LLM Extraction:** Ollama host sidecar over Apple Silicon Metal GPU ([ADR-26j003](adrs/ADR-26j003-local-llm-extraction-ollama.md)).
5. **Unified 6-Tier Tech Stack:** Python 3.12, Pydantic v2, FastAPI, PostgreSQL 16, pytest, React + Vite ([ADR-26j004](adrs/ADR-26j004-ecosystem-technology-stack.md)).
