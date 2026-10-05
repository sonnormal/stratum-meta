# 📜 Stratum Shared Contracts

> **Purpose:** Canonical repository of formal, machine-readable interfaces between independent Stratum repositories.  
> **Location:** `meta/contracts/`  
> **Rule:** Repositories must never communicate using ad-hoc, unversioned payloads. All cross-repo messages and APIs must adhere to contracts defined here.

---

## 🎯 What is a Contract?

A **Contract is The Agreement**. It defines the **binding mutual obligations between a Producer and Consumer** (syntax + behavior + idempotency + error handling + breaking change guarantees):

* **Beyond a simple interface:** While an interface merely declares field names and types, a contract establishes the complete behavioral pact and reliability invariants between independent repositories.
* **Events (`events/`):** Asynchronous message payloads emitted to queues or pub/sub topics (defined via JSON Schema or Protobuf).
* **APIs (`apis/`):** Synchronous HTTP/REST endpoints and gRPC service definitions (defined via OpenAPI / Swagger or Protobuf).

---

## 📂 Directory Layout

```text
contracts/
├── README.md           # This guide
├── events/             # Asynchronous event schemas
│   └── transaction_detected.v1.json
└── apis/               # Synchronous REST/gRPC specifications
    └── (OpenAPI / gRPC specs)
```

---

## 🏷️ Versioning & Evolution Rules

1. **Explicit File Versioning:** Every contract filename includes its major version: `<name>.v<Major>.<ext>` (e.g. `transaction_detected.v1.json`).
2. **Backward Compatibility:**
   * Adding optional fields or additive endpoints is a **non-breaking change** (remains `v1`).
   * Renaming fields, removing fields, or changing data types is a **breaking change** and requires introducing a new file (`v2`).
3. **Producer & Consumer Testing:**
   * **Producers** (e.g. `gateway`) validate outbound payloads against the contract in Tier 2 integration tests.
   * **Consumers** (e.g. `services/cashflow`) validate inbound deserialization against the contract in Tier 2 integration tests.
