# 🌐 Stratum Cross-Repository E2E Acceptance Test Specification: CR-26j002

> **Document Type:** Cross-Service Technical Specification & Executable Tier 3 Acceptance Tests (`STEP-04` Red Phase)  
> **Target Checkpoint:** `GATE-02` (Contract & Test Scenario Gate)  
> **Location:** `meta/changes/CR-26j002-telegram-commands/e2e_scenario.md`  
> **Scope:** Strictly isolated to **Tier 3 Automated E2E Testing** across `gateway`, `services/cashflow`, and simulated Telegram Bot API. Microservice-internal unit and integration tests are isolated in their respective repo `scenario.md` files.

---

## 📌 1. Cross-Service Change Metadata

| Field | Detail |
| :--- | :--- |
| **Change ID** | `CR-26j002` |
| **Primary Business Flow** | [FLOW-002: Telegram Conversational Command Queries](../../flows/telegram-command-query.md) |
| **Associated Feature** | [FEAT-002: Telegram Conversational Financial Queries](../../features/telegram-conversational-queries.md) |
| **Participating Repositories** | [`gateway`](../../../gateway), [`services/cashflow`](../../../services/cashflow) |
| **Master CR Record** | [CR-26j002 Master Request](request.md) |
| **Status:** | `PENDING_REVIEW` (Targeting `GATE-02`) |

---

## 🏛️ 2. Multi-Service Topology & Test Environment

*Executed locally via Docker / OrbStack multi-container stack (`stratum-meta/deploy/docker-compose.yml`):*

| Container / Component | Role in E2E Flow | Exposed Port | Healthcheck Endpoint |
| :--- | :--- | :--- | :--- |
| **`stratum-gateway`** | Telegram long-polling loop, command parser, Chat ID authenticator | `8000` | `http://127.0.0.1:8000/healthz` |
| **`stratum-cashflow-service`** | Aggregated metrics calculation & recent transaction queries | `8001` | `http://127.0.0.1:8001/healthz` |
| **`stratum-cashflow-db`** | PostgreSQL 16 database (`cashflow` DB with 143 backfilled records) | `5432` | `pg_isready -U postgres -d cashflow` |

---

## 🧪 3. Acceptance Test Suite (The 6 Canonical Test Cases)

### TC-01: Boundary / Edge — Unrecognized Message / Help Request
* **Scenario:** Authorized user sends `/start`, `/help`, or plain text `"hello"`.
* **Preconditions:** Telegram bot poller is active.
* **Trigger:** Telegram update event containing text `/help` from `chat_id: 8502789411`.
* **Expected Invariants:**
  - Gateway responds with command help menu:
    * `/today`: Today's debit/credit total & count
    * `/this_month`: Current month total & count
    * `/recent`: Latest 5 transactions
  - Zero database mutations.
  - Exits in < 500ms.

### TC-02: Happy Path — Query Today's Cashflow (`/today`)
* **Scenario:** Stakeholder queries daily total spend.
* **Preconditions:** PostgreSQL has movements for today (or 0 movements if none yet recorded today).
* **Trigger:** Telegram update event `/today` from `chat_id: 8502789411`.
* **Expected Invariants:**
  - Gateway calls `http://cashflow-service:8001/api/v1/metrics/today`.
  - Cashflow service executes SQL aggregation over `occurred_at::date = CURRENT_DATE`.
  - Bot formats response (e.g. `📅 Hôm nay (13-Oct-2026): N giao dịch. Tổng chi: X VND. Tổng thu: Y VND`).
  - Response delivered back via Telegram `sendMessage`.

### TC-03: Happy Path — Query Monthly Cashflow (`/this_month`)
* **Scenario:** Stakeholder queries current month totals.
* **Preconditions:** PostgreSQL contains historical 2026 backfill data.
* **Trigger:** Telegram update event `/this_month` from `chat_id: 8502789411`.
* **Expected Invariants:**
  - Gateway calls `http://cashflow-service:8001/api/v1/metrics/month?year=2026&month=10`.
  - Cashflow service aggregates all rows between start and end of current month.
  - Bot formats response with month name, transaction count, total debit, and total credit.
  - Response delivered back via Telegram `sendMessage`.

### TC-04: Happy Path — Query Recent Transactions (`/recent`)
* **Scenario:** Stakeholder requests recent movements list.
* **Preconditions:** PostgreSQL contains movements in `account_movements`.
* **Trigger:** Telegram update event `/recent` from `chat_id: 8502789411`.
* **Expected Invariants:**
  - Gateway calls `http://cashflow-service:8001/api/v1/movements/recent?limit=5`.
  - Cashflow service returns top 5 rows sorted by `occurred_at DESC`.
  - Bot formats a clean bulleted list containing: Date, Amount (VND), Counterparty, and Description.
  - Response delivered back via Telegram `sendMessage`.

### TC-05: Security / Threat Mitigation — Unauthorized Chat ID
* **Scenario:** An unauthorized Telegram user (`chat_id: 999999999`) sends `/today` or `/recent`.
* **Preconditions:** Bot is listening for updates.
* **Trigger:** Telegram update from `chat_id: 999999999`.
* **Expected Invariants:**
  - Gateway security filter flags sender as unauthorized (`chat.id != 8502789411`).
  - Request is silently ignored (or returns 403 unauthorized notification).
  - Internal `cashflow-service` is NEVER invoked (zero database reads).
  - No financial information disclosed.

### TC-06: Unhappy Path / Resilience — Core Service Temporary Failure
* **Scenario:** `cashflow-service` returns 500 or times out while bot processes `/today`.
* **Preconditions:** Simulated internal endpoint failure.
* **Trigger:** Inbound `/today` command while service is degraded.
* **Expected Invariants:**
  - Gateway catches exception cleanly.
  - Sends polite error message to user (`⚠️ Không thể lấy dữ liệu dòng tiền lúc này. Vui lòng thử lại sau.`).
  - Long polling loop DOES NOT crash or terminate; continues listening for subsequent messages.
