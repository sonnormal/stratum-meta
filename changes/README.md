# 📑 Stratum Change Archive

This directory maintains the immutable, historical records of all **Change Requests (CRs)** in the Stratum ecosystem.

---

## 🏷️ Identification Standard: `CR-YYaXXX`

Every change is assigned a unique ID following the format: **`CR-YYaXXX`**

* **`YY`**: 2-digit Year (`26` for 2026).
* **`a`**: Month letter (`A`=Jan, `B`=Feb, `C`=Mar, `D`=Apr, `E`=May, `F`=Jun, `G`=Jul, `H`=Aug, `I`=Sep, `J`=Oct, `K`=Nov, `L`=Dec).
* **`XXX`**: 3-digit monthly sequence number (`001`, `002`, `003`...).

*Example:* **`CR-26J001`** is the 1st change request initiated in October 2026.

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
| `CR-26J001` | Initial Implementation: VIB Email Transaction Alert & Digest | In Discussion | 2026-10-01 | [`CR-26J001-vib-tracker/`](CR-26J001-vib-tracker/) |
