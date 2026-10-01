# 📑 Stratum Change Archive

This directory maintains the immutable, historical records of all **Change Requests (CRs)** in the Stratum ecosystem.

---

## 🏷️ Identification Standard: `CR-YYaXXX`

Every change is assigned a unique ID following the format: **`CR-YYaXXX`**

* **`YY`**: 2-digit Year (`26` for 2026).
* **`a`**: Single **lowercase letter** denoting the month:
  * `a`=Jan, `b`=Feb, `c`=Mar, `d`=Apr, `e`=May, `f`=Jun
  * `g`=Jul, `h`=Aug, `i`=Sep, **`j`=Oct**, `k`=Nov, `l`=Dec
* **`XXX`**: 3-digit monthly sequence number (`001`, `002`, `003`...).

*Example:* **`CR-26j001`** is the 1st change request initiated in October 2026.

---

## 📂 Structure: One Folder per Change

Every change resides in its own dedicated directory:
```text
changes/CR-YYaXXX-<short-title>/
├── change.md         # Master overview, status, and gate approval audit log (Gate 1, 2, 3)
├── evaluation.md     # STEP-03 / GATE-01 Report (Scope, Security, Cost-Benefit)
├── scenarios.md      # STEP-04 / GATE-02 Approved plain-language test scenarios
└── fixtures/         # Sample test data, raw emails (.eml), mock payloads (optional)
```

---

## 🗂️ Change Register

| ID | Title | Status | Date | Folder |
| :--- | :--- | :--- | :--- | :--- |
| `CR-26j001` | Initial Implementation: VIB Email Transaction Alert & Digest | In Discussion | 2026-10-01 | [`CR-26j001-vib-tracker/`](CR-26j001-vib-tracker/) |
