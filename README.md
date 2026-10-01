# Stratum

> **Autonomous, AI-Agent-Driven Software Engineering & Operations**  
> *100% AI-Generated Code, Tests, and Infrastructure — Governed by Human-in-the-Loop Review.*

---

## 🌟 Vision & Overview

**Stratum** is an autonomous software lifecycle ecosystem where AI agents design, test, build, deploy, and operate software systems. Human stakeholders maintain strategic control through lightweight conversational checkpoints delivered via **Email (`sonnormal@gmail.com`)**, **Zalo**, and **Viber**.

To prove this platform in practice, Stratum starts with a concrete, containerized **walking skeleton (CR-001)** that exercises the full autonomous lifecycle from day one.

---

## 🎯 Initial Walking Skeleton (`CR-001`): VIB Transaction Alert & Digest

The initial implementation is treated as **Change Request 001 (`CR-001`)**, following the exact same autonomous governance lifecycle as any future feature:

```
[ Email from vib.com.vn ] ──► [ stratum-gateway ] ──► [ VIB Parser Service ]
(sonnormal@gmail.com)          (IMAP / OAuth)             │
                                                          ├──► [ PostgreSQL (OrbStack/Docker) ]
                                                          │    (Persists transactions & balances)
                                                          │
                                                          └──► [ Zalo / Viber Bot Alert ]
                                                               ("💳 Spent 150k VND at Coffee House")
```

### What It Does:
1. **Ingress:** Reads incoming emails in `sonnormal@gmail.com` filtered from `*@vib.com.vn` (Vietnam International Bank transaction notices, debit alerts, balance changes).
2. **Process:** Autonomously parses transaction details:
   - Transaction Amount & Currency
   - Masked Account / Card Number
   - Merchant Name & Description
   - Timestamp & Remaining Account Balance
3. **Store:** Persists records into a containerized **PostgreSQL** database.
4. **Notify:** Dispatches an instant, clean transaction summary to your **Zalo / Viber** bot.
5. **Runtime:** Runs 100% locally on **Docker / OrbStack** on Mac Studio, with zero cloud lock-in—ready to deploy to any cloud VM/Kubernetes later.

---

## 🏛️ Core Principles (Pragmatic Phase 1)

1. **100% AI-Generated Code via Strict TDD**
   * No manual coding. AI agents write automated tests *first* (`Red`), get human approval, then synthesize minimal code (`Green`).
   * **Phase 1 Testing Scope:** Focus strictly on **Tier 1 (Unit Tests)** for parsing/logic and **Tier 2 (Integration Tests)** with containerized databases (PostgreSQL via Testcontainers/Docker). Full multi-service E2E automation is intentionally deferred to later phases.

2. **Omnichannel Conversational Interface**
   * All stakeholder interactions (change requests, approval gates, alerts) occur via **Email (`sonnormal@gmail.com`)**, **Zalo**, and **Viber**.

3. **Three Human Governance Gates (HITL)**
   * **`GATE-01` (Value Gate):** *Why do it?* — Approves business value, cost, and cybersecurity before development.
   * **`GATE-02` (Contract & Scenario Gate):** *What to build?* — Approves plain-language test scenarios and edge cases *before* code is written.
   * **`GATE-03` (User Acceptance Gate):** *Does it work?* — Stakeholder tests the live container in UAT before production sign-off.

4. **Containerized & Portable by Design**
   * Everything runs in standardized containers (`Dockerfile`, `docker-compose.yml`) on **OrbStack / Docker** locally.
   * Frictionless transition to cloud environments (Fly.io, AWS, GCP, or Kubernetes) whenever needed.

5. **Self-Observing Runtime**
   * Container health probes, structured logging, and automated error alerting back to your chat channels.

---

## 🗂️ Lean Repository Structure

Rather than premature multi-repo sprawl, Stratum begins with a focused set of repositories inside the local workspace:

```text
/Users/son/Projects/Stratum/                 <-- Workspace Root (Mac Studio)
├── stratum-meta/                            <-- (Current Repo) Global Docs, Governance, Schemas & ADRs
│   ├── README.md
│   └── docs/
│       ├── workflow.md                      <-- Simplified 7-step lifecycle & 3 gates
│       ├── testing_strategy.md              <-- Unit + Integration test architecture
│       └── templates/
│           └── change_evaluation_template.md
│
├── stratum-gateway/                         <-- Omnichannel Gateway (Email IMAP/OAuth + Zalo/Viber)
│
└── stratum-services/                        <-- Domain Services
    └── vib-expense-tracker/                 <-- Containerized VIB Parser & DB Service
```

---

## 🚀 Quick Reference Documents

* 👉 **[Simplified Workflow & 3 Governance Gates (`docs/workflow.md`)](docs/workflow.md)**
* 👉 **[Testing Strategy: Unit & Integration Tiers (`docs/testing_strategy.md`)](docs/testing_strategy.md)**
* 👉 **[Change Evaluation Template (`docs/templates/change_evaluation_template.md`)](docs/templates/change_evaluation_template.md)**
