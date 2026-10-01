# Stratum

> **Autonomous, AI-Agent-Driven Software Engineering & Operations**  
> *100% AI-Generated Code, Tests, and Infrastructure — Governed by Human-in-the-Loop Review.*

---

## 🌟 Vision & Overview

**Stratum** is an autonomous software lifecycle ecosystem where AI agents design, test, build, deploy, and operate software systems. Human stakeholders maintain strategic governance and oversight through lightweight conversational checkpoints delivered via **Email (`sonnormal@gmail.com`)**, **Zalo**, and **Viber**.

Every initiative—from the initial system setup to new features, optimizations, and bug fixes—is treated and executed as an explicit, auditable **Change Request (CR)**.

---

## 🏛️ Core Principles

1. **100% AI-Generated Code via Strict TDD**
   * No manual coding. AI agents write automated tests *first* (`Red`), receive human approval, then synthesize minimal code (`Green`).
   * **Testing Scope:** Focuses on **Tier 1 (Unit Tests)** for domain algorithms/parsing and **Tier 2 (Integration Tests)** with containerized databases/caches (Docker/Testcontainers). Multi-service E2E automation is phased in when architecture stabilizes.

2. **Omnichannel Conversational Interface**
   * All stakeholder interactions (change requests, approval gates, alerts) occur via **Email (`sonnormal@gmail.com`)**, **Zalo**, and **Viber**.

3. **Three Human Governance Gates (HITL)**
   * **`GATE-01` (Value Gate):** *Why do it?* — Approves business value, cost, and cybersecurity before development begins.
   * **`GATE-02` (Contract & Scenario Gate):** *What to build?* — Approves plain-language test scenarios and edge cases *before* implementation code is synthesized.
   * **`GATE-03` (User Acceptance Gate):** *Does it work?* — Stakeholder verifies functionality in a live container environment before release.

4. **Containerized & Portable by Design**
   * Workloads run in standardized containers (`Dockerfile`, `docker-compose.yml`) on **OrbStack / Docker** locally.
   * Frictionless transition to cloud environments (Fly.io, AWS, GCP, or Kubernetes) whenever public 24/7 access is required.

5. **Self-Observing Runtime**
   * Container health probes, structured logging, and automated error alerting back to conversational channels.

---

## 🗂️ Workspace & Repository Structure

Stratum is organized as an umbrella workspace containing focused, decoupled repositories:

```text
/Users/son/Projects/Stratum/                 <-- Workspace Root (Mac Studio)
├── stratum-meta/                            <-- (Current Repo) Global Docs, Governance, Schemas & ADRs
│   ├── README.md                            <-- Platform Overview
│   ├── docs/
│   │   ├── workflow.md                      <-- Universal 7-step lifecycle & 3 gates
│   │   ├── testing_strategy.md              <-- Testing tiers (Unit, Integration, E2E)
│   │   └── templates/                       <-- Change Evaluation Report templates
│   └── changes/                             <-- Dedicated archive of all Change Requests (CRs)
│
├── stratum-gateway/                         <-- Omnichannel Gateway (Email IMAP/OAuth + Zalo/Viber)
│
└── stratum-services/                        <-- Domain Services & Microservices
```

---

## 📑 Change Management

All changes in Stratum are proposed, evaluated, approved, and archived in the [**`changes/`**](changes/) directory. Every change follows the universal lifecycle documented in [`docs/workflow.md`](docs/workflow.md).

---

## 🚀 Quick Reference Documents

* 👉 **[Universal Workflow & 3 Governance Gates (`docs/workflow.md`)](docs/workflow.md)**
* 👉 **[Testing Strategy: Unit & Integration Tiers (`docs/testing_strategy.md`)](docs/testing_strategy.md)**
* 👉 **[Change Evaluation Template (`docs/templates/change_evaluation_template.md`)](docs/templates/change_evaluation_template.md)**
* 👉 **[Change Archive (`changes/`)](changes/)**
