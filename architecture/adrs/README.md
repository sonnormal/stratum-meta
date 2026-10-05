# 🏛️ Stratum Architectural Decision Records (ADRs)

This directory documents the immutable, foundational architectural decisions that govern all repositories in the Stratum ecosystem.

---

## 🎯 What is an ADR?

An **Architectural Decision Record (ADR)** captures a significant architectural choice, its business/technical rationale, and its binding rules across all repositories.

* **Multi-Repo Standard:** An ADR defines rules that **every repository must obey** (e.g. standard container runtime, testing policies, communication protocols).
* **AI Guardrails:** ADRs prevent AI development agents from proposing or synthesizing conflicting technologies (e.g. choosing MongoDB when the ecosystem standardized on PostgreSQL).

---

## 🏷️ Identification & File Format

Every architectural decision is assigned a unique ID conforming to the Stratum temporal standard: **`ADR-YYaXXX`**

* **`YY`**: 2-digit Year (`26` for 2026).
* **`a`**: Single **lowercase letter** denoting the month:
  * `a`=Jan, `b`=Feb, `c`=Mar, `d`=Apr, `e`=May, `f`=Jun
  * `g`=Jul, `h`=Aug, `i`=Sep, **`j`=Oct**, `k`=Nov, **`m`=Dec** *(skips `l` to avoid confusion with `1`)*
* **`XXX`**: 3-digit monthly sequence number (`001`, `002`, `003`...).

*Example:* **`ADR-26j001`** is the 1st architectural decision record created in October 2026.

* **File Format:** `ADR-YYaXXX-<short-title>.md` (e.g., `ADR-26j001-containerized-local-runtime.md`)
* **Status Lifecycle:** `PROPOSED` → `ACCEPTED` → `SUPERSEDED` (by `ADR-YYaXXX`) → `REJECTED`

---

## 🗂️ ADR Register

| ID | Title | Status | Date | Primary Scope |
| :--- | :--- | :--- | :--- | :--- |
| [`ADR-26j001`](ADR-26j001-containerized-local-runtime.md) | Standardized Containerized Runtime & OrbStack Environment | `ACCEPTED` | 2026-10-01 | All Repositories |
| [`ADR-26j002`](ADR-26j002-strict-tdd-and-testcontainers.md) | Strict Test-Driven Development & Isolated Testcontainers | `ACCEPTED` | 2026-10-01 | All Service Repos |
| [`ADR-26j003`](ADR-26j003-local-llm-extraction-ollama.md) | Standardized Local LLM Document Extraction via Ollama | `ACCEPTED` | 2026-10-05 | `gateway`, `services/*` |

---

## 📝 Creating a New ADR

To propose a new cross-repo standard, copy the canonical template from [**`templates/adr.md`**](../../templates/adr.md) and submit a Change Request through `stratum-meta`.
