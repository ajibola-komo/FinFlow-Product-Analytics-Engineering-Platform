# FinFlow Product Analytics Engineering Platform - Synthetic Data Generation Rules

> **Last Updated:** June 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Definitions (Source of Truth)](#2-business-definitions-source-of-truth)
3. [Data Generation Framework (Simulation Rules)](#3-data-generation-framework-simulation-rules)
4. [Dimensional Modelling Framework](#4-dimensional-modelling-framework)
5. [Product & Funnel Analysis Framework](#5-marketing--funnel-analysis-framework)
6. [Business Metric Definitions](#6-business-metric-definitions)
7. [Design Principles](#7-design-principles)
8. [Data Refresh & Cadence](#8-data-refresh-and-cadence)
9. [Document Ownership](#9-document-ownership)
10. [Conclusion](#10-conclusion)

---
## 1. Executive Summary
### Project Objective
FinFlow simulates a digital wealth management platform operating in the United Kingdom and Ireland. The platform offers savings and investment products and generates realistic customer, wallet, transaction, and investment activity data to support analytics engineering, business intelligence, and product analytics use cases.

The platform is built to achieve the following objectives:

- Generate realistic synthetic event streams for a multi-product fintech platform, modeling customer behavior across wallet funding, payments, savings, investments, and other money movement activities.
- Model end-to-end customer journeys to support product analytics use cases such as retention, funnels, and cross-product engagement
- Design a scalable data architecture with historical backfills and incremental daily ingestion patterns
- Implement a partitioned data lake structure and transform raw data into analytics-ready models using dbt
- Build consistent product and growth metrics to enable reliable reporting and decision-making
- Support core analytics use cases including cohort analysis, funnel analysis, and user behavior tracking
- Simulate automated daily data pipelines using scheduled orchestration workflows
- Deliver curated datasets optimized for BI dashboards and business insights in Power BI
- Demonstrate best practices in analytics engineering including modular modeling, incremental processing, and scalable ELT design

### Architecture
![Data Warehouse Architecture](docs/images/finflow_data_warehouse_architecture.png)

### Data Volumes
**Initial Batch Load**
| Table | Type | Grain | Approx. rows |
|---|---|---|---|
| `dim_date` | dimension | One record per calendar date | ~3,650 rows |
| `dim_event_type` | dimension | One record per distinct event type | 12 rows |
| `dim_product` | dimension | One record per distinct product offering | 2 rows |
| `dim_plan` | dimension | One record per product plan variant | 4 rows |
| `dim_user` | dimension | One record per registered user | ~500K rows |
| `dim_wallet` | dimension | One record per user wallet account (one wallet per user) | ~500K rows |
| `fact_user_event` | fact | One record per user generated event occurence | ~12M rows |
| `fact_investment_position` | fact | One record per investment position created by a user  | ~1.1M rows |
| `fact_transaction` | fact | One record per money movement transaction within the application | ~5M rows |

**Daily Incremental Loads**
| Table | Approx. rows |
|---|---|
|`dim_user` |300 - 500 |
|`dim_wallet` (creation) |300 - 500 (exact number of new users created)|
|`dim_wallet` (activation) |100 - 150 (Newly created users), 200 (Existing Users) |
|`fact_user_event`|4000 - 8000 |
|`fact_investment_position`|200 - 800 |
|`fact_transaction` |2500 - 6000 |

### Key Analytics Use Cases
- Onboarding & Activation Analytics
- Engagement Analytics
- Retention and Churn Analytics
- Conversion Funnel Analytics
- Product Adoption Analytics
- Customer Segmentation
- Operational Monitoring
- Executive Reporting & Decision Support


### Technologies Used
The platform is built on a modern analytics engineering stack:
| Layer               | Technology                  |
| ------------------- | ------------- |
| Data Generation    | Python (Numpy, Pandas) |
| Local Processing    | DuckDB |
| Data Lake    | Amazon S3 |
| Data Warehouse    | Snowflake |
| Transformation   | dbt(core) |
| Orchestration    | Apache Airflow |
| BI & Reporting    | Power BI |

### Key Assumptions

- One wallet per customer.
- All transactions are denominated in GBP.
- The platform operates exclusively in the United Kingdom and Ireland.
- Wallet activation represents the first successful wallet funding event.
- Historical data is generated using persona-driven behavioral models.
- Customer behavior varies based on persona, acquisition channel, and lifecycle stage.

---
## 8. Data Refresh and Cadence
| Component                        | Cadence       | Description                                                                              |
| ---------------------------------| ------------- | ----------------------------------------------------------------------------------------|
| User Generation                  | Daily         | Generate new users, customer attributes, persona assignments, and acquisition channels. |
| Wallet Updates                   | Daily         | Create new wallets and update wallet activation status based on user activity.          |
| Events & Transaction Generation  | Daily         | Generate customer activity events, deposits, withdrawals, transfers, and investment transactions. |
| dbt Model Refresh                | Daily         | Incremental dbt transformations and loading newly generated data                  |
| Power BI Semantic Model Refresh | Daily | Refresh Power BI semantic models after dbt model execution. |
| Dashboard Refresh | Daily | Refresh Power BI reports and dashboards. |

### Refresh Sequence

1. Generate synthetic source data using Python
2. Validate and stage datasets in DuckDB
3. Persist raw data to Amazon S3
4. Load data into Snowflake
5. Execute dbt transformations
6. Run data quality validations
7. Refresh Power BI semantic models
8. Refresh Power BI dashboards and reports

### Refresh Dependencies

The daily refresh process follows a strict dependency chain:

1. Python Data Generation
2. DuckDB Validation & Staging
3. Amazon S3 Load and Partitioning
4. Snowflake Load
5. dbt Model Refresh
6. Data Quality Checks
7. Power BI Semantic Model Refresh
8. Dashboard Refresh

Downstream refreshes are not executed until upstream processes complete successfully.

### Data Availability SLA
All generated data is expected to be available for reporting by 09:00 GMT+1 each day.

### Loading Strategy

| Dataset | Load Type | Description |
|----------|-----------|-------------|
| dim_user | Incremental | Load newly generated customers and updates. |
| dim_wallet | Incremental | Load newly created or activated wallets. |
| fact_user_event | Incremental | Load newly generated customer events. |
| fact_investment_position | Incremental | Load daily position snapshots and updates. |
| fact_transaction | Incremental | Load newly generated financial transactions. |

Historical records are preserved to support trend analysis, cohort analysis, retention reporting, and executive KPI reporting.

### Data Quality Validation

The following validation checks are executed prior to loading data:

- User IDs must be unique.
- Wallet IDs must be unique.
- Email addresses must be unique.
- Activated users must have completed KYC.
- Activated wallets must have an activation timestamp.
- Wallet activation dates must occur after wallet creation dates.
- No unexpected null values are permitted in mandatory fields.

---
## 9. Document Ownership
This document is authored and maintained by [Ajibola Komolafe](https://www.linkedin.com/in/ajibola-k-4ba921123/) as part of a solo portfolio project. All business rules, simulation logic, and metric definitions reflect intentional design decisions made by the author.

---
## 10. Conclusion
This framework enables:
- End-to-end product analytics across acquisition, activation, engagement, retention, and investment behavior.
- Scalable analytics architecture leveraging Amazon S3, Snowflake, dbt, Airflow, and Power BI.
- A scalable analytics engineering workflow built on synthetic but business-realistic data.
- Dimensional modeling, metric governance, and semantic reporting best practices.
- Portfolio-ready dashboards and analytical use cases spanning product, growth, operations, and executive reporting.
- Realistic simulation of event-driven customer and investment behavior. 
---

## Project Links
[LinkedIn](https://www.linkedin.com/in/ajibola-k-4ba921123/) · [GitHub](https://github.com/ajibola-komo/FinFlow-Product-Analytics-Engineering-Platform) ·
[Power BI](https://) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/)



