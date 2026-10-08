# 🐳 Stratum Living Container Runtime Topology (C4 Level 2)

> **Document Type:** Living Accumulated Container & Network Deployment Specification  
> **Status:** `ACTIVE` (Synchronized via `STEP-07` post-UAT promotion)  
> **Source Orchestration:** [stratum-meta/deploy/docker-compose.yml](file:///Users/son/Projects/Stratum/stratum-meta/deploy/docker-compose.yml)  
> **Governing Decisions:** [ADR-26j001](file:///Users/son/Projects/Stratum/stratum-meta/architecture/adrs/ADR-26j001-containerized-local-runtime.md), [ADR-26j003](file:///Users/son/Projects/Stratum/stratum-meta/architecture/adrs/ADR-26j003-local-llm-extraction-ollama.md), [ADR-26j004](file:///Users/son/Projects/Stratum/stratum-meta/architecture/adrs/ADR-26j004-ecosystem-technology-stack.md)

---

## 🗺️ 1. Visual Topology Diagram

```mermaid
graph TD
    subgraph Host_Environment ["Host Machine (Mac Studio / PC)"]
        HostOllama["Host Ollama LLM Service<br/><i>qwen3.6:27b on Apple Silicon Metal GPU</i><br/>Port: 11434"]
        ClientHost["Host Browser / HTTP Client<br/>Ports: 8000, 8001, 5432"]
    end

    subgraph Docker_Engine ["Docker / OrbStack Container Runtime"]
        subgraph Perimeter_Net ["Network: stratum-perimeter-net (Bridge)"]
            Gateway["stratum-gateway<br/>(Python 3.12 / FastAPI)<br/>Port: 8000"]
        end

        subgraph Internal_Net ["Network: stratum-internal-net (Bridge)"]
            Cashflow["stratum-cashflow-service<br/>(Python 3.12 / FastAPI / SQLAlchemy)<br/>Port: 8001"]
        end

        subgraph Data_Net ["Network: stratum-data-net (Bridge)"]
            Postgres[("stratum-cashflow-db<br/>(PostgreSQL 16 Alpine)<br/>Port: 5432")]
            DataVol[("Volume: cashflow-data")]
        end
    end

    ClientHost -->|HTTP :8000| Gateway
    ClientHost -->|HTTP :8001| Cashflow
    Gateway -->|host.docker.internal:11434| HostOllama
    Gateway -->|HTTP :8001 / Internal DNS| Cashflow
    Cashflow -->|TCP :5432 / Internal DNS| Postgres
    Postgres --- DataVol
```

---

## 🧱 2. Operational Runtime Matrix

| Container Name | Service Role | Image | Networks | Exposed Ports | Health Probe | Persistent State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [**`stratum-gateway`**](file:///Users/son/Projects/Stratum/gateway) | Perimeter Edge | `deploy-gateway` | `perimeter`, `internal` | `8000:8000` | `GET /healthz` (5s) | Stateless |
| [**`stratum-cashflow-service`**](file:///Users/son/Projects/Stratum/services/cashflow) | Financial Core | `deploy-cashflow` | `internal`, `data` | `8001:8001` | `GET /healthz` (5s) | Stateless |
| **`stratum-cashflow-db`** | Ledger Database | `postgres:16-alpine` | `data` | `5432:5432` | `pg_isready` (3s) | Named Volume: `cashflow-data` |

---

## 🛡️ 3. Core Architectural Invariants

* **Network Boundary Isolation:** `stratum-gateway` belongs strictly to `perimeter` and `internal` networks with **zero route to `stratum-cashflow-db`**.
* **Host Hardware Acceleration Bridge:** `stratum-gateway` reaches the host Metal GPU Ollama service strictly via `http://host.docker.internal:11434` (`extra_hosts`).
* **Authoritative State Isolation:** Only `stratum-cashflow-service` can access `cashflow-data` via internal TCP 5432; direct external SQL access is prohibited.
