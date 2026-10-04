# ADR-26j001: Standardized Containerized Runtime & OrbStack Environment

> **Decision ID:** `ADR-26j001`  
> **Status:** `ACCEPTED`  
> **Date:** `2026-10-01`  
> **Applies to:** `All Repositories`  
> **Related CR:** `CR-26j001`

---

## 📌 1. Context & Problem Statement

Stratum operates as an autonomous, multi-repository ecosystem running on a local workstation (Mac Studio) while maintaining full capability for future cloud deployment (Fly.io, AWS ECS, Kubernetes).

Without an ecosystem-wide runtime standard:
* Different repositories might demand incompatible local runtime runtimes (native PostgreSQL vs MySQL daemons, host-level Redis versions).
* AI agents might generate scripts assuming host daemon installations, polluting the developer machine.
* Moving from local development to production would introduce subtle environment drift bugs.

---

## ⚖️ 2. Decision

1. **Standard Runtime:** All microservices, gateways, and auxiliary tooling must run in standardized **OCI/Docker Containers**.
2. **Local Engine:** Local multi-container orchestration must execute on **OrbStack** (lightweight Docker daemon on macOS) via standard `Dockerfile` and `docker-compose.yml`.
3. **Zero Host Services:** No service or database may be installed natively on the host OS. All databases, caches, and queues must run inside container networks.
4. **Health Check Contract:** Every service container must implement a lightweight HTTP health check probe endpoint returning `200 OK` on `/healthz`.

---

## 💡 3. Alternatives Considered & Rationale

| Alternative | Pros | Cons | Why Rejected? |
| :--- | :--- | :--- | :--- |
| **Native Host Daemons (Homebrew)** | Slightly lower CPU/memory footprint | Pollutes macOS, version conflicts between projects | Rejected: Fails portability requirement. |
| **Docker Desktop** | Familiar UI | High memory overhead, slow on macOS | Rejected: OrbStack provides 2x speed and ~10% memory usage on Mac Studio. |
| **Local Minikube / K3s** | Matches Kubernetes APIs | Massive complexity for early-stage microservices | Rejected: Over-engineering; Docker Compose is sufficient for early phases. |

---

## 🛡️ 4. Consequences & Multi-Repo Enforcement

### Positive Consequences
* **100% Cloud Portability:** Any container that runs on OrbStack runs identically on any OCI-compliant cloud provider.
* **Hermetic Environments:** Deleting or recreating the workspace leaves zero lingering state on the host system.

### Negative / Trade-offs
* Requires Docker daemon running on the Mac Studio.

### Compliance & Verification
* **Gate 3 Verification:** Every change must build a valid container image and pass `/healthz` check before `GATE-03` sign-off.
