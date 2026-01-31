# Stock Card SQL Report — Odoo Module

## 📌 Overview

Stock Card SQL Report is a high-performance Odoo module that generates a detailed stock movement ledger (Stock Card) using a SQL engine instead of ORM aggregation.

It is designed specifically for:

- Large databases
- Heavy stock movement volumes
- Fast reporting requirements
- Accurate running balances
- Location-based stock tracking

All heavy calculations are executed in SQL using window functions, while the wizard layer handles user filters and opening balance logic.

---

## 🎯 Features

- Product-based stock card
- Location-based movement calculation
- Supports location hierarchy (child locations)
- SQL-calculated:
  - Qty In
  - Qty Out
  - Running Balance
- Wizard-based filters
- Optional date range filtering
- Opening balance calculated from last movement before date_from
- Separate result screen (tree view)
- No heavy ORM loops
- Scalable for large datasets

---

## 🧠 Architecture

The module follows a layered reporting design:


### Why this design?

- SQL handles heavy math efficiently
- ORM handles flexible filtering
- Results are reusable for Excel / PDF later
- Clean separation of concerns

---

