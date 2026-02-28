# 📦 Stock Movement Analysis

[![Odoo Version](https://img.shields.io/badge/Odoo-16%2B-purple)](#)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](#)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](#)

Stock Movement Analysis is an analytical module for Odoo that provides a consolidated view of product movements within a selected period.

It focuses purely on **operational stock movements** such as Sales, Purchases, Inventory Adjustments, Manufacturing, and Internal Transfers.



---

## 📑 Table of Contents

- [Overview](#overview)
- [Movement Types Covered](#movement-types-covered)
- [Features](#features)
- [Business Use Cases](#business-use-cases)
- [Technical Approach](#technical-approach)
- [Installation](#installation)
- [Access Rights](#access-rights)
- [Dependencies](#dependencies)
- [License](#license)

---

## 🔎 Overview

This module analyzes validated stock moves (`stock.move`) and classifies them by operation type within a defined date range.

It allows inventory managers to understand:

- How much was sold
- How much was purchased
- Inventory adjustment quantities
- Manufacturing consumption & production
- Internal stock transfers

All analysis is performed using standard Odoo ORM.

---

## 🔄 Movement Types Covered

The module categorizes stock movements into:

- 🛒 Sales (Customer Deliveries)
- 📦 Purchases (Vendor Receipts)
- 🏭 Manufacturing (MO Consumption & Production)
- 🔁 Internal Transfers
- 📊 Inventory Adjustments

Each movement type is aggregated per product within the selected period.

---

## 🚀 Features

- Period-based stock movement analysis
- Product-level aggregation
- Classification by operation type
- Clean tree & pivot views
- Filter by:
  - Date range
  - Product
  - Category
  - Warehouse
- No impact on valuation or accounting

---

## 🏢 Business Use Cases

- Compare sales vs purchase quantities
- Analyze manufacturing consumption vs production
- Detect excessive internal transfers
- Audit inventory adjustments
- Review product movement trends

---

## 🏗 Technical Approach

### Core Model

```python
stock.move.line
```

### Logic Summary

1. Filter validated moves (`state = done`)
2. Apply date range filter
3. Classify moves based on:
   - Picking type
   - Source & Destination locations
4. Aggregate quantities per product
5. Present summarized results



## ⚙ Installation

1. Add the module to your custom addons directory.
2. Restart Odoo.
3. Update Apps List.
4. Install **Stock Movement Analysis**.

---

## 🔐 Access Rights

Recommended groups:

- Inventory User
- Inventory Manager

---

## 📦 Dependencies

```python
'depends': [
    'stock',
]
```

---

## 📝 License

LGPL-3

---

## 👨‍💻 Maintainer

Designed for operational inventory analysis and reporting clarity.
