# Event-Driven Growth Analytics Platform

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

---

# BI Layer Strategy

The project uses Tableau Public as the visualization layer. Since Tableau Public is file-based, curated analytics datasets are exported daily from the data warehouse into versioned CSV/Parquet files.

This simulates a real-world semantic layer where downstream BI tools consume governed, pre-aggregated datasets rather than querying raw data sources directly.

**Ajibola Komolafe** — Data and Analytics Engineer
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo)