# ADR-26j003: Standardized Local LLM Document Extraction via Ollama

> **Decision ID:** `ADR-26j003`  
> **Status:** `ACCEPTED`  
> **Date:** `2026-10-05`  
> **Applies to:** `gateway`, `services/*`  
> **Related CR:** `CR-26j001`

---

## 📌 1. Context & Problem Statement

Stratum services ingest unstructured and semi-structured external communications (e.g., bank alert emails, payment notifications, transaction memos). 

Traditional regex and hardcoded template extractors suffer from critical failure modes:
1. **Layout Brittleness:** Bank HTML templates frequently change spacing, headers, or promotional banners, causing regex parsers to break silently.
2. **Lack of Semantic Understanding:** Regex cannot categorize expenses (e.g. classifying `"ShopeeFood"` as `Food & Beverage`) or clean messy bank wire memos (e.g. extracting counterparty names from transaction codes).
3. **Cloud LLM Hazards:** Sending personal financial emails to third-party cloud APIs (OpenAI, Anthropic) introduces recurring API costs, external network latency, and severe privacy/compliance risks.

---

## ⚖️ 2. Decision

1. **Standard Local Inference Engine:** Ingestion parsing and semantic extraction must execute on a **locally hosted LLM via Ollama** running natively on the host workstation (Mac Studio Apple Silicon) with Metal GPU acceleration.
2. **Container Network Bridge:** Containerized services (e.g., `gateway`) must connect to Ollama via the internal Docker bridge gateway: `http://host.docker.internal:11434`.
3. **Model Standard:** Baseline extraction standardizes on high-precision open-weights models (e.g. `qwen3.6:27b` / `qwen2.5:32b` or larger).
4. **Three-Stage Ingestion Pipeline:**
   * **Stage 1 (Heuristic Pre-Filter):** Fast sender/subject string check (< 1ms) to discard irrelevant emails before consuming GPU compute.
   * **Stage 2 (Constrained LLM Extraction):** Prompt LLM with strict JSON Schema (`format: "json"`). Model extracts `amount`, `currency`, `transaction_type`, `occurred_at`, `counterparty`, and `category`.
   * **Stage 3 (Deterministic Post-Guardrail):** A deterministic sanity check verifies that the extracted numeric `amount` exists as a substring in the raw input body. If mismatched, the event is flagged for human review to prevent financial hallucinations.
5. **Strict TDD Testability Invariant:**
   * **Tier 1 (Unit Tests):** Must **never** call the live Ollama API. The extraction seam (`EmailExtractor`) must be fully mocked in-memory (0 network, < 1ms execution).
   * **Tier 2 (Integration Tests) & UAT:** Connect to the live local Ollama endpoint or containerized mock server.

---

## 💡 3. Alternatives Considered & Rationale

| Alternative | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Hardcoded Regex / Templates** | Fast, zero memory footprint | Extremely brittle; cannot extract counterparty or category semantics | Rejected: High maintenance; breaks on minor email format changes. |
| **Cloud LLM APIs (OpenAI / Claude)** | Zero local compute needed | Monthly API cost, network latency, leaks financial data to third parties | Rejected: Violates 100% local privacy and cost-efficiency principles. |
| **Containerized Ollama (inside Docker)** | Self-contained in Docker Compose | Cannot use native Apple Silicon Metal GPU acceleration on macOS (runs CPU-only) | Rejected: Unacceptable 5–10x latency penalty compared to host-native Metal. |

---

## 🛡️ 4. Consequences & Multi-Repo Enforcement

### Positive Consequences
* **100% Privacy & Zero Cost:** All financial emails and transaction details are processed on-device with zero third-party data egress and $0 API billing.
* **Extensible Gateway:** The same local LLM pipeline can extract bills, invoices, receipts, and flight confirmations without writing new regex templates.
* **Semantic Enrichment:** Transactions are automatically categorized and counterparties normalized at ingestion time.

### Negative / Trade-offs
* Requires Ollama running on the Mac host (`ollama serve`).
* Higher memory footprint (16GB–24GB RAM for 27B–36B models), which the Mac Studio easily accommodates.

### Compliance & Verification
* **Gate 2 Verification:** Unit tests for extraction logic must pass with mocked responses.
* **Gate 3 Verification:** Live container test in `STEP-06` must successfully parse a sample `.eml` via `http://host.docker.internal:11434` and verify guardrail validation.
