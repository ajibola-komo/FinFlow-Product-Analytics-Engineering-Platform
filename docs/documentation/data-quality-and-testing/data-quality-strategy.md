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
  Snowflake Raw/dbt Bronze Layer
        │
        ▼
   dbt Silver Layer
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
| Snowflake and dbt Silver Layer | Relationships and business logic |
| Marts, Facts, and Dimensions | Business Rules and Analytical Correctness |
| BI | Metric Reconciliation |

# 5. Data Quality Dimensions

| DQ Dimension | Dimensions | Facts | Description | Examples |
|---|---|---|---|---|
| Completeness | ✅ | ✅ | The required fields are populated | Required fields are not null |
| Uniqueness | ✅ | ✅ | Records are unique according to the defined table grain and key constraints | `user_id` unique in `dim_user`; `event_id` unique in `fct_user_event` |
| Schema/Conformity | ✅ | ✅ | Data conforms to the expected schema, data types, formats, and structural definitions | Correct columns and types |
| Referential Integrity | ✅ | ✅ | Foreign keys resolve to valid parent dimension records | `fact_user_event.user_id` → `dim_user.user_id` |
| Accepted values/domain | ✅ | ✅ | Values belong to approved domains, e.g. investment_status | investment_status: Redeemed, Matured, Active |
| Freshness | ✅ | ✅ | Data arrives within the defined SLA | Daily Incremental Loads |
| Temporal Consistency | ✅ | ✅ | Related timestamps follow valid chronological relationships | `wallet_created_at` < `wallet_activated_at` |
| Range Validation | ✅ | ✅ | Numeric and date values fall within valid ranges | amount_invested > 0 |
| Distribution Validation | ✅ | ✅ | Synthetic data distributions remain within expected statistical thresholds | Persona and Channel Distributions and Mix must align with the defined project rules |
| Business Rule Validation | ✅ | ✅ | Domain-specific rules are validated | IF `fact_user_event.is_money_movement_activity` = `TRUE` `fact_user_event.transaction_id` IS NOT NULL |
| Cross-Layer Reconciliation | ✅ | ✅ | Counts, amounts and metrics reconcile between pipeline layers | - |
| Sequential / Event Lifecycle Integrity| - | ✅ | Events occur in valid chronological and lifecycle order | signup_completed event < kyc_completed event |

# 6. Data Quality Rules Catalogue

# 7. Layer Specific Testing Strategy

# 8. dbt Testing Strategy

# 9. Great Expectations Strategy

# 10. Python Data Generation Validation

# 11. Data Contracts and Schema Validation

# 12. Test Severity and Failure Handling

# 13. Data Quality Monitoring

# 14. CI/CD and Automated Test Execution

# 15. Exceptions, Assumptions and Known Limitations




