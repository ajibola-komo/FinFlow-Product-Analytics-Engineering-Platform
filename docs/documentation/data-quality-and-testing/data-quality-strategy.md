# FinFlow Product Analytics Engineering Platform - Data Quality Strategy

> **Last Updated:** September 2026
> **Version:** 1.0
> **Status:** Active
> **Owner:** Ajibola Komolafe (Analytics Engineering)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Tools Used](#2-documentation-overview--project-scope)
3. [Data Architecture](#3-data-architecture)
4. [Testing Scope](#4-testing-scope)
5. [Data Quality Dimensions](#5-data-quality-dimensions)

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

# 5. Data Quality Dimensions

| DQ Dimension | Dimensions | Facts | Description | Examples |
|---|---|---|---|---|
| Completeness | ✅ | ✅ | The required fields are populated | Required fields are not null |
| Uniqueness | ✅ | ✅ | PK uniqueness | PK uniqueness |
| Schema/Conformity | ✅ | ✅ | Primary keys and defined unique keys contain no duplicates | Correct columns and types |
| Referential Integrity | ✅ | ✅ | Foreign keys resolve to valid parent dimension records | dim_user(user_id) → fact_user_event(user_id) |
| Accepted values/domain | ✅ | ✅ | Values belong to approved domains, e.g. investment_status | investment_status: Redeemed, Matured, Active |
| Freshness | ✅ | ✅ | Data arrives within the defined SLA | Daily Incremental Loads |
| Temporal Consistency | ✅ | ✅ | Related timestamps follow valid chronological relationships | wallet_created_at < wallet_activated_at |
| Range Validation | ✅ | ✅ | Numeric and date values fall within valid ranges | amount_invested > 0 |
| Distribution Validation | ✅ | ✅ | Synthetic data distributions remain within expected statistical thresholds | Persona and Channel Distributions |
| Business Rule Validation | ✅ | ✅ | Domain specfic rules are validated | signup_completed event < kyc_completed event |
| Cross-Layer Reconciliation | ✅ | ✅ | Counts, amounts and metrics reconcile between pipeline layers | signup_completed event < kyc_completed event |
| Sequential Validation | - | ✅ | Events occur in valid chronological and lifecycle order | signup_completed event < kyc_completed event |


