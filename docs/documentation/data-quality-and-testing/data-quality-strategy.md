# FinFlow Product Analytics Engineering Platform - Data Quality Strategy

> **Last Updated:** September 2026
> **Version:** 1.0
> **Status:** Active
> **Owner:** Ajibola Komolafe (Analytics Engineering)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Tools Used](#2-documentation-overview--project-scope)

# 1. Executive Summary

This document defines the testing and data quality strategy for the FinFlow analytics platform. It establishes the checks, validation rules, monitoring mechanisms, and failure-handling procedures used to ensure that data is accurate, complete, consistent, timely, and fit for analytical use.

# 2. Documentation Overview and Project Scope

| Item | Description |
|---|---|
| Purpose | The scope of this project and data testing effort is to ensure the generated data is analytically reliable and trustworthy. |
| Technical Scope | Data generation → Azure ADLS Gen2 → Snowflake → dbt → BI |
| Primary Technology Tools | Python, DuckDB, Azure ADLS, Snowflake, dbt, Streamlit |
| Testing Layers | Source, transformation, business logic, data quality |
| Frequency | 3-Year Historical Backfill, Daily/Incremental |

# 3. Data Architecture

```
Synthetic Event Generation
        │
        ▼
     ADLS Gen2
        │
        ▼
  Snowflake Raw Layer
        │
        ▼
    dbt Staging
        │
        ▼
   dbt Intermediate
        │
        ▼
   dbt Marts / Facts
        │
        ▼
 Streamlit / Analytics

```

# 4. Testing Scope

This section of the project highlights the testing scope at each layer.

| Layer | What is tested |
|---|---|
| Python Synthetic Generation | Schema, distributions, IDs, timestamps |
| Azure ADLS Gen2 (Data Lake) | File availability, schema, duplicates, completeness |
| Snowflake and dbt Bronze Layer | Data types, nulls, uniqueness |
| Snowflake and dbt Intermediate Layer | Relationships and business logic |
| Marts | Business Rules and Analytical Correctness |
| BI | Metric Reconciliation |
