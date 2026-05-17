# FinFlow Product Analytics Engineering Platform

Production-style SaaS analytics platform simulating scalable event-driven data pipelines with dbt, partitioned data lake architecture, incremental processing, and growth metrics modeling.

---

# Problem Statement

Modern startups generate massive volumes of user interaction data every day across web and mobile applications. However, many early-stage companies struggle to build scalable analytics systems capable of transforming raw event data into reliable business insights.

Without a properly designed analytics platform, organizations often face several challenges:

- Inability to track user engagement and retention accurately
- Slow dashboard performance caused by unpartitioned datasets
- Expensive full-refresh transformation workflows
- Inconsistent business metrics across teams
- Lack of automated daily data pipelines
- Difficulty analyzing conversion funnels and revenue growth drivers

---

# Project Objectives

This project aims to solve these challenges by designing and implementing a production-style event-driven growth analytics platform that simulates how modern SaaS startups collect, process, transform, and analyze user behavior data at scale.

The platform is designed to:

- Generate realistic daily user event data
- Ingest and store data in a partitioned raw data lake
- Implement incremental loading strategies for efficient processing
- Transform raw data into analytics-ready models using dbt
- Orchestrate automated daily workflows
- Deliver business-critical growth and retention metrics through dashboards

The project focuses on demonstrating modern analytics engineering practices commonly used in startup environments, including:

- Event-driven data modeling
- Partition-aware warehouse design
- Incremental ELT pipelines
- Workflow orchestration and automation
- Scalable fact and dimension modeling
- Product and growth analytics

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data generation | Python (Faker, NumPy, Pandas) |
| Compute & Orchestration | AWS EC2 (Linux), Git-based deployment |
| Storage | Amazon S3 |
| Warehouse | Snowflake / DuckDB |
| Transformation | dbt |
| Visualization | Tableau |

---

# Architecture Overview

## High-Level Architecture

```text
Python Event Generator
        ↓
Orchestration Layer (Airflow)
        ↓
Raw Data Lake (Partitioned by Event Date)
        ↓
Data Warehouse (Snowflake)
        ↓
dbt Transformation Layer
        ↓
Analytics Marts
        ↓
BI Dashboards (Tableau)
```

## Data Lakehouse Architecture

The project implements a Medallion-inspired transformation pattern using dbt within Snowflake, with raw data stored in S3.
```
Python scripts → S3 (data lake) → Snowflake → dbt (Bronze → Silver → Gold) → Tableau
```

- **Bronze** — raw ingested data
- **Silver** — cleaned, standardized, and enriched datasets
- **Gold** — aggregated, analytics-ready data marts

---
## Synthetic Data Generation

All datasets are fully synthetic, generated using custom Python modules built on Pandas and NumPy.

- A 3-year baseline dataset is first generated i.e. from 3 years ago up to yesterday.
- A scheduled DAG simulates a daily batch ingestion process by generating synthetic event data for the previous day at 9 AM and and writes it as a new partition in the historical dataset.
- The data simulates user activity within a fintech platform consisting of three core products:
    - An investment application
    - A bank transfer application
    - An agency banking application

Generated datasets are exported as Parquet files for efficient storage and downstream ingestion into S3 and Snowflake.

> The full data dictionary covering all fact & dimension tables, column definitions, data types, and grain is available in `docs/data_dictionary/`.


---

## Data Model
Star schema with 4 fact tables and 10 dimension tables.

| Table | Type | Grain | Approx. rows |
|---|---|---|---|
| `fact_transaction` | Fact | One row per transaction | ~900,000 |
| `fact_sale` | Fact | One row per line item per transaction | ~1,800,000 |
| `fact_clickstream` | Fact | One row per web session | ~14,000,000 |
| `fact_inventory` | Fact | One row per store × product × month | ~586,000 |
| `dim_date` | Dimension | One row per calendar date | ~3,650 |
| `dim_customer` | Dimension | One row per customer | ~150,000 |
| `dim_product` | Dimension | One row per SKU | 470 |
| `dim_store` | Dimension | One row per store | 50 |
| `dim_promotion` | Dimension | One row per promotion | 150 |
| `dim_campaign` | Dimension | One row per campaign | 120 |
| `dim_category` | Dimension | One row per category | 10 |
| `dim_subcategory` | Dimension | One row per subcategory | 28 |
| `dim_brand` | Dimension | One row per brand | 50 |
| `dim_location` | Dimension | One row per city | ~ 25 |

---

## BI Layer Strategy

The project uses Tableau Public as the visualization layer. Since Tableau Public is file-based, curated analytics datasets are exported daily from the data warehouse into versioned CSV/Parquet files.

This simulates a real-world semantic layer where downstream BI tools consume governed, pre-aggregated datasets rather than querying raw data sources directly.

**Ajibola Komolafe** — Data and Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo)