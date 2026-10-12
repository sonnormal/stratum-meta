# 🐘 Exploring Stratum Cashflow Database via pgAdmin 4

> **Guide Location:** `stratum-meta/deploy/pgadmin-guide.md`  
> **Target Database:** `stratum-cashflow-db` (PostgreSQL 16)  
> **Image:** `dpage/pgadmin4:latest` (Pre-pulled in OrbStack)

---

## 🚀 1. Launching pgAdmin 4

You can launch the pre-pulled `dpage/pgadmin4:latest` container using any of the three options below:

### Option A: Via Docker Compose (Recommended)
From the repository root, run:
```bash
docker compose -f stratum-meta/deploy/docker-compose.yml --profile tools up -d pgadmin
```

### Option B: Via Standalone Docker Run
Run directly inside the shared `stratum-data-net` network:
```bash
docker run -d \
  --name stratum-pgadmin \
  --restart unless-stopped \
  --network stratum-data-net \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@stratum.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -e PGADMIN_CONFIG_SERVER_MODE=False \
  dpage/pgadmin4:latest
```

### Option C: Via OrbStack Desktop GUI
1. Open the **OrbStack** desktop app.
2. Under **Containers**, locate the `stratum-pgadmin` container (if created) or run the `dpage/pgadmin4` image.
3. Ensure port `5050` is mapped to container port `80`, and network is set to `stratum-data-net`.

---

## 🔐 2. Logging In to pgAdmin

1. Open your browser and navigate to:
   * **URL:** [http://localhost:5050](http://localhost:5050) *(or in OrbStack: `http://stratum-pgadmin.orb.local`)*
2. Enter the login credentials:
   * **Email:** `admin@stratum.com`
   * **Password:** `admin`

---

## 🔗 3. Connecting to the Cashflow Database

Once inside the pgAdmin dashboard:

1. Right-click **Servers** in the left sidebar tree → select **Register** → **Server...**
2. In the **General** tab:
   * **Name:** `Stratum Cashflow`
3. Click the **Connection** tab and fill in the connection parameters:

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Host name/address** | `cashflow-db` | Container DNS name inside `stratum-data-net` *(or `host.docker.internal` / `localhost`)* |
| **Port** | `5432` | Standard PostgreSQL port |
| **Maintenance database** | `cashflow` | Domain database name |
| **Username** | `postgres` | Superuser |
| **Password** | `postgres` | Default development password |
| **Save password?** | ☑️ *Checked* | Avoid re-typing password on reconnect |

4. Click **Save**.

---

## 🔍 4. Navigating the Data

In the left tree view, expand:
* **Servers** → **Stratum Cashflow** → **Databases** → **cashflow** → **Schemas** → **public** → **Tables** → **`account_movements`**

* **View All Rows:** Right-click **`account_movements`** → **View/Edit Data** → **All Rows**.
* **Open Query Tool:** Right-click **`cashflow`** database (or select from top menu: **Tools** → **Query Tool**).

---

## 📊 5. Exploration SQL Queries

Paste and run (`F5` or click ▶️) any of the following queries in the Query Tool:

### Query 1: Total Movements & Volume by Transaction Type
```sql
SELECT 
    transaction_type, 
    COUNT(*) AS total_transactions, 
    TO_CHAR(SUM(amount), 'FM999,999,999,999') || ' VND' AS total_volume
FROM account_movements 
GROUP BY transaction_type;
```

### Query 2: Top 15 Largest Expenses in 2026
```sql
SELECT 
    occurred_at, 
    counterparty, 
    category, 
    TO_CHAR(amount, 'FM999,999,999,999') || ' VND' AS amount, 
    description 
FROM account_movements 
WHERE transaction_type = 'DEBIT' 
ORDER BY amount DESC 
LIMIT 15;
```

### Query 3: Monthly Cashflow Breakdown (Debits vs Credits)
```sql
SELECT 
    TO_CHAR(occurred_at, 'YYYY-MM') AS month,
    COUNT(*) AS total_movements,
    TO_CHAR(SUM(CASE WHEN transaction_type = 'DEBIT' THEN amount ELSE 0 END), 'FM999,999,999,999') || ' VND' AS total_debit,
    TO_CHAR(SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE 0 END), 'FM999,999,999,999') || ' VND' AS total_credit
FROM account_movements
GROUP BY TO_CHAR(occurred_at, 'YYYY-MM')
ORDER BY month DESC;
```

### Query 4: Top 10 Merchants & Counterparties by Spending
```sql
SELECT 
    COALESCE(counterparty, 'Unknown') AS counterparty, 
    COUNT(*) AS transaction_count, 
    TO_CHAR(SUM(amount), 'FM999,999,999,999') || ' VND' AS total_spent
FROM account_movements 
WHERE transaction_type = 'DEBIT' 
GROUP BY counterparty 
ORDER BY SUM(amount) DESC 
LIMIT 10;
```

### Query 5: Spending by Extracted Category
```sql
SELECT 
    COALESCE(category, 'General') AS category, 
    COUNT(*) AS transaction_count, 
    TO_CHAR(SUM(amount), 'FM999,999,999,999') || ' VND' AS total_amount 
FROM account_movements 
WHERE transaction_type = 'DEBIT' 
GROUP BY category 
ORDER BY SUM(amount) DESC;
```

---

## 🛑 6. Stopping pgAdmin

When you finish exploring the database, you can stop the pgAdmin container using the matching method:

### Option A: Via Docker Compose
```bash
docker compose -f stratum-meta/deploy/docker-compose.yml --profile tools stop pgadmin
```

### Option B: Via Standalone Docker CLI
```bash
docker stop stratum-pgadmin && docker rm stratum-pgadmin
```

### Option C: Via OrbStack Desktop GUI
1. Open the **OrbStack** desktop app.
2. Under **Containers**, locate **`stratum-pgadmin`**.
3. Click the square **Stop** (■) button (or right-click → **Stop**).

---

> **Note on Data Persistence:** Stopping or removing the pgAdmin container has zero impact on your data. The PostgreSQL database (`stratum-cashflow-db`) and all stored transaction movements remain permanently persisted in the `cashflow-data` volume.
