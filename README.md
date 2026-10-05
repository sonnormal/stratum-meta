# Stratum

> **Autonomous, AI-Agent-Driven Software Engineering & Operations**  
> *100% AI-Generated Code, Tests, and Infrastructure — Governed by Human-in-the-Loop Review.*

---

## 🌟 Vision & Overview

**Stratum** is an autonomous software lifecycle ecosystem where AI agents design, test, build, deploy, and operate software systems. Human stakeholders maintain strategic governance and oversight through lightweight conversational checkpoints delivered via **Email**, **Zalo**, and **Viber**.

Every initiative—from the initial system setup to new features, optimizations, and bug fixes—is treated and executed as an explicit, auditable **Change Request (CR)**.

---

## 🏛️ Core Principles

1. **100% AI-Generated Code via Strict TDD**
   * No manual coding. AI agents write automated tests *first* (`Red`), receive human approval, then synthesize minimal code (`Green`).
   * **Testing Scope:** Focuses on **Tier 1 (Unit Tests)** for domain algorithms/parsing and **Tier 2 (Integration Tests)** with containerized databases/caches (Docker/Testcontainers). Multi-service E2E automation is phased in when architecture stabilizes.

2. **Omnichannel Conversational Interface**
   * All stakeholder interactions (change requests, approval gates, alerts) occur via **Email**, **Zalo**, and **Viber**.

3. **Three Human Governance Gates (HITL)**
   * **`GATE-01` (Value Gate):** *Why do it?* — Approves business value, cost, and cybersecurity before development begins.
   * **`GATE-02` (Contract & Scenario Gate):** *What to build?* — Approves plain-language test scenarios and edge cases *before* implementation code is synthesized.
   * **`GATE-03` (User Acceptance Gate):** *Does it work?* — Stakeholder verifies functionality in a live container environment before release.

4. **Containerized & Portable by Design**
   * Workloads run in standardized containers (`Dockerfile`, `docker-compose.yml`) on **OrbStack / Docker** locally.
   * Frictionless transition to production Kubernetes clusters whenever public 24/7 access is required.

5. **Self-Observing Runtime**
   * Container health probes, structured logging, and automated error alerting back to conversational channels.

---

## 🗂️ Workspace & Repository Structure

Stratum is organized as an umbrella workspace containing focused, decoupled repositories:

```text
/Users/son/Projects/Stratum/                 <-- Workspace Root (Mac Studio)
├── stratum-meta/                            <-- (Current Repo) Global Governance, Living Specs, Schemas & ADRs
│   ├── README.md                            <-- Platform Overview
│   ├── changes/                             <-- Dedicated archive of all Change Requests (CRs)
│   ├── flows/                               <-- Cross-repo end-to-end event/data flows & sequence choreographies
│   ├── features/                            <-- Living domain feature specifications (with implementing repo links)
│   ├── contracts/                           <-- Canonical schemas, protobufs & cross-repo API contracts
│   ├── architecture/                        <-- Technical blueprints & Architectural Decision Records (ADRs)
│   │   └── adrs/                            <-- ADR-YYaXXX immutable technical decisions
│   ├── standards/                           <-- Ecosystem engineering standards & governance
│   │   ├── README.md                        <-- Standards catalog
│   │   ├── sdlc.md                          <-- Universal 7-step lifecycle & 3 gates
│   │   ├── testing.md                       <-- Testing tiers (Unit, Integration, E2E)
│   │   └── glossary.md                      <-- Ubiquitous language dictionary
│   └── templates/                           <-- Canonical document blueprints (request, evaluation, scenario, flow, feature, adr)
│
├── stratum-gateway/                         <-- Omnichannel Gateway (Email IMAP/OAuth + Zalo/Viber)
│
└── stratum-services/                        <-- Domain Services & Microservices
```

---

## 📑 Change Management

All changes in Stratum are proposed, evaluated, approved, and archived in the [**`changes/`**](changes/) directory. Every change follows the universal lifecycle documented in [`standards/sdlc.md`](standards/sdlc.md).

---

## 🚀 Quick Reference Documents

* 👉 **[Universal SDLC & 3 Governance Gates (`standards/sdlc.md`)](standards/sdlc.md)**
* 👉 **[Testing Standards: Unit & Integration Tiers (`standards/testing.md`)](standards/testing.md)**
* 👉 **[Engineering Standards Catalog (`standards/`)](standards/README.md)**
* 👉 **[Document Templates (`templates/`)](templates/README.md)**
* 👉 **[System Flows Catalog (`flows/`)](flows/README.md)**
* 👉 **[Living Features Catalog (`features/`)](features/README.md)**
* 👉 **[Shared Contracts (`contracts/`)](contracts/README.md)**
* 👉 **[Architectural Decision Records (`architecture/adrs/`)](architecture/adrs/README.md)**
* 👉 **[Global Glossary & Ubiquitous Language (`standards/glossary.md`)](standards/glossary.md)**
* 👉 **[Change Archive (`changes/`)](changes/)**
