# ⚖️ Stratum Engineering Standards & Governance

> **Purpose:** Canonical registry of cross-repository operational rules, development lifecycles, testing policies, and ubiquitous language governing all repositories in the Stratum ecosystem.  
> **Location:** `meta/standards/`  
> **Audience:** Human stakeholders and autonomous AI development agents.

---

## 🎯 What are Stratum Standards?

While [**`architecture/`**](file:///Users/son/Projects/Stratum/stratum-meta/architecture) defines **the technical machine** (system topology, container configurations, and ADRs), **`standards/`** defines **the operating rules** for how software is specified, built, tested, and verified:

* **Ecosystem-Wide:** Every repository (`services/*`, `gateway`, `web`, `meta`) must adhere to these policies.
* **Autonomous Guardrails:** AI development agents must strictly abide by these lifecycle and testing constraints before generating code.

---

## 🗂️ Standards Catalog

| Standard Document | Scope | Purpose |
| :--- | :--- | :--- |
| [**`sdlc.md`**](sdlc.md) | Universal Lifecycle & 3 Gates | The 7-step autonomous development lifecycle governed by 3 Human-in-the-Loop review gates (Value, Scenario, UAT). |
| [**`testing.md`**](testing.md) | Quality Assurance & Verification | Tier 1 (Unit), Tier 2 (Integration with Testcontainers), and Tier 3 (E2E) testing definitions, speeds, and rules. |
| [**`glossary.md`**](glossary.md) | Ubiquitous Language Dictionary | Platform-wide terminology definitions (`CR`, `Gates`, `Flow`, `Feature`, `Contract`, `ADR`, `Seam`) to prevent semantic drift. |
