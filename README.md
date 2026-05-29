# FinFlow Product Analytics Engineering Platform

Event-driven fintech analytics platform combining analytics engineering and product analytics to model user behavior, retention, growth, and financial activity at scale.

---

# Problem Statement

Modern fintech products generate large volumes of user behavioral and transactional data across multiple channels including mobile applications, payment systems, and investment platforms. Every user action from onboarding and account funding to transfers, investments, and daily engagement produces event-level data that needs to be captured, processed, and converted into meaningful business insights.

In many early-stage and scaling fintech companies, building a reliable and scalable analytics system is still a major challenge.

Without a well-designed analytics platform, teams typically face issues such as:

- Data being spread across multiple products and systems, which makes it difficult to get a unified view of the customer
- Inconsistent definitions of key metrics like revenue, active users, and retention across teams
- Slow query performance due to unoptimized data models and storage structures
- Heavy reliance on full refresh processes that do not scale with growing data volumes
- Limited visibility into customer behaviour across the full lifecycle and across products
- Difficulty accurately tracking funnels, retention, and cross-product adoption
- Lack of automated and reliable pipelines for daily data ingestion and transformation

This project is designed to address these challenges by building a production-style fintech product analytics and analytics engineering platform that simulates how modern digital financial systems collect, process, model, and analyze large-scale event-driven data across multiple products.

---

# Project Objectives

This project aims to design and implement a production-style **fintech product analytics** and analytics engineering platform that simulates how modern digital financial systems collect, process, model, and analyze behavioral and transactional data.

The platform is built to achieve the following objectives:

- Generate realistic synthetic event streams for a multi-product fintech platform, modeling customer behavior across wallet funding, payments, savings, investments, and other money movement activities.
- Model end-to-end customer journeys to support product analytics use cases such as retention, funnels, and cross-product engagement
- Design a scalable data architecture with historical backfills and incremental daily ingestion patterns
- Implement a partitioned data lake structure and transform raw data into analytics-ready models using dbt
- Build consistent product and growth metrics to enable reliable reporting and decision-making
- Support core analytics use cases including cohort analysis, funnel analysis, and user behavior tracking
- Simulate automated daily data pipelines using scheduled orchestration workflows
- Deliver curated datasets optimized for BI dashboards and business insights in Tableau
- Demonstrate best practices in analytics engineering including modular modeling, incremental processing, and scalable ELT design

The project focuses on demonstrating modern analytics engineering and product analytics practices commonly used in startup environments, including:

- Event-driven data modeling for capturing user behavior across product interactions
- Partition-aware warehouse design for scalable and efficient data storage
- Incremental ELT pipelines for optimized processing of growing data volumes
- Workflow orchestration and automation for reliable daily data ingestion
- Scalable dimensional modeling using fact and dimension tables
- Product and growth analytics to support insights on retention, funnels, and engagement

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data generation | Python (Faker, NumPy, Pandas) |
| Workflow Orchestration| Airflow |
| Compute & Infrastructre| AWS EC2 (Linux), Git-based deployment |
| Storage | Amazon S3 |
| Warehouse | Snowflake / DuckDB |
| Transformation | dbt |
| Visualization | Power BI |

---

# Product or Platform Event Flow

![Event Flow Diagram](Event-Driven-Growth-Analytics-Platform\docs\images\event_flow_diagram.png)

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
BI Dashboards (Power BI)
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
- The data simulates user activity within a fintech platform consisting of two core products:
    - A digital savings product
    - A digital investment product

The dataset is low-medium frequency but behaviour rich.

Generated datasets are exported as Parquet files for efficient storage and downstream ingestion into S3 and Snowflake.

> The full data dictionary covering all fact & dimension tables, column definitions, data types, and grain is available in `docs/data_dictionary/`.


---

## Data Model
Star schema with 4 fact tables and 10 dimension tables.

| Table | Type | Grain | Approx. rows |
|---|---|---|---|
| `fact_transactions` | Fact | One row per transaction | 8_000_000|

---

## BI Layer Strategy

The project uses Tableau Public as the visualization layer. Since Tableau Public is file-based, curated analytics datasets are exported daily from the data warehouse into versioned CSV/Parquet files.

This simulates a real-world semantic layer where downstream BI tools consume governed, pre-aggregated datasets rather than querying raw data sources directly.

**Ajibola Komolafe** — Data and Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo)