# FinFlow Product Analytics Engineering Platform - Synthetic Data Generation Rules

> **Last Updated:** July 2026

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
![Data Warehouse Architecture](../images/finflow_data_warehouse_architecture.png)

### Data Volumes
**Initial Batch Load**
| Table | Type | Grain | Approx. rows |
|---|---|---|---|
| `dim_date` | dimension | One record per calendar date | ~3,650 rows |
| `dim_event_type` | dimension | One record per distinct event type | 16 rows |
| `dim_product` | dimension | One record per distinct product offering | 2 rows |
| `dim_plan` | dimension | One record per product plan variant | 4 rows |
| `dim_user` | dimension | One record per registered user | ~500K rows |
| `dim_wallet` | dimension | One record per user wallet account (one wallet per user) | ~500K rows |
| `dim_transaction_type` | dimension | One record per distinct transaction type | 6 rows |
| `fact_user_event` | fact | One record per user generated event occurence | ~45M+ rows |
| `fact_investment_position` | fact | One record per investment position created by a user  | ~1.3M+ rows |
| `fact_transaction` | fact | One record per money movement transaction within the application | ~9M+ rows |
| `fact_wallet_balance` | snapshot fact | One record per wallet account | ~500k+ rows |

**Daily Incremental Loads**
| Table | Approx. rows |
|---|---|
|`dim_user` |300 - 500 |
|`dim_wallet` (creation) |300 - 500 (exact number of new users created)|
|`dim_wallet` (activation) |100 - 150 (Newly created users), 200 (Existing Users) |
|`fact_user_event`|4000 - 8000 |
|`fact_investment_position`|200 - 800 |
|`fact_transaction` |2500 - 6000 |
|`fact_wallet_balance` |2500 - 3000 |

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
| Synthetic Data Generation    | Python (Numpy, Pandas) |
| Operational Processing Layer   | DuckDB |
| Cloud Data Lake    | Azure Blob Storage |
| Compute & Infrastructure   | Azure Virtual Machines, Docker |
| Cloud Data Warehouse    | Snowflake |
| Transformation   | dbt Core |
| Workflow Orchestration    | Apache Airflow |
| BI & Reporting    | Power BI |

### Key Assumptions

- One wallet per customer.
- All transactions are denominated in GBP.
- The platform operates exclusively in the United Kingdom and Ireland.
- Wallet activation represents the first successful wallet funding event.
- Historical data is generated using persona-driven behavioral models.
- Customer behavior varies based on persona, acquisition channel, and lifecycle stage.

---
## 2. Business Definitions (Source of Truth)
> This section defines how the business interprets data, independent of implementation.

### 2.1. Users
A **user** is an individual who registers for and engages with FinFlow's products and services. Users may exist in one of the following lifecycle states:

- **Registered User**: A user who has successfully created an account but has not yet completed all onboarding requirements required to activate their account. This includes pending KYC verification and wallet funding.
- **KYC Completed User**: A user who has successfully completed KYC verification but is yet to initiate the initial wallet funding or deposit required to activate their account
- **Activated User**: A user who has successfully completed KYC verification and activated their account by completing their first wallet funding transaction. Activated users are eligible to access and engage with FinFlow's product offerings.

To enable realistic behavioural simulation, users are assigned to a customer persona during data generation. Customer personas represent the foundational segmentation layer within the FinFlow synthetic data generation framework. Each generated user is assigned a persona based on predefined distribution weights. Personas determine key user attributes including:
- `Age Range`
- `Reported Annual Income`
- `Acquisition Channel Propensity`
- `Wallet Activation Likelihood`
- `Time-to-first-funding Behaviour`
- `Behavioural Segment Assignment`

Behavioural segments derived from personas are then used to simulate downstream customer actions such as application logins, wallet funding activity, product adoption, investment creation, and retention patterns.

The platform models the following customer personas:
| Persona       | Age Group     | Income Range  | Distribution  |
| ---------| ------------- | --------------| --------------|
| `Starter Investor` | 18 - 30 | £18,000 - £50,000 | 25% |
| `Goal-Oriented Saver` | 25 - 55 | £25,000 - £90,000 | 30% |
| `Wealth Builder` | 25 - 60 | £40,000 - £150,000 | 25% |
| `Active Investor` | 25–65 | £60,000 - £120,000 | 10% |
| `Capital Preserver` | 45+ | £70,000 - £150,000 | 10% |

The platform models the following behavioural segments:
| Behaviour Segment       | Description    |
| ---------| ------------- | 
| High Engagement High Balance (HEHB) | Frequent platform usage with consistently high wallet and investment balances. Typically exhibits strong product adoption and investment activity. |
| High Engagement Low Balance (HELB) | Very active users who engage frequently with the platform but maintain relatively smaller balances and contribution amounts. |
| Moderate Engagement High Balance (MEHB) | Users who engage periodically but maintain larger balances and investment positions. |
| Moderate Engagement Low Balance (MELB) | Average users with moderate platform activity and relatively smaller balances. |
| Low Engagement High Balance (LEHB) | Users who rarely interact with the platform but maintain significant savings or investment holdings. |
| Low Engagement Low Balance (LELB) | Infrequent users with low balances and minimal product activity. Represents the highest churn-risk segment. |

The personas influence the behavioural segments as follows:
Behavioural segments are assigned probabilistically based on the user's persona. This relationship ensures that generated customer behaviour remains consistent with the expected characteristics of each persona.

| Persona | HEHB | HELB | MEHB | MELB | LEHB | LELB |
|----------|-----:|-----:|-----:|-----:|-----:|-----:|
| Starter Investor | 2% | 55% | 3% | 20% | 0% | 20% |
| Goal-Oriented Saver | 3% | 15% | 10% | 45% | 7% | 20% |
| Wealth Builder | 20% | 5% | 45% | 10% | 15% | 5% |
| Active Investor | 70% | 5% | 15% | 5% | 5% | 0% |
| Capital Preserver | 5% | 0% | 35% | 0% | 60% | 0% |


### 2.2. Wallets & Investment Positions

- A **wallet** is a customer-owned account used to hold cash balances within the FinFlow platform. Wallets serve as the primary source and destination for money movement activities, including deposits, withdrawals, transfers, and investment funding transactions.

    Funds held within a wallet are considered **uninvested cash balances** and remain available for future transactions or investment activities.

- An **investment position** represents a customer's active or historical investment in a specific product, fund, or investment vehicle offered by FinFlow. Investment positions track the lifecycle of invested funds from creation through maturity and redemption.

    Investment positions maintain a historical record of investment activity, including:
    - Initial investment amount
    - Investment start date
    - Investment tenure
    - Associated plan and product
    - Investment value at creation
    Funds allocated to an investment position are considered **actively invested** and are no longer available within the customer's wallet balance until redeemed, matured, or withdrawn according to product rules.

### 2.3. User Events

A **User Event** denotes a captured timestamped user action within the application. Finflow's event taxonomy is as follows:

- signup_completed
- app_login
- kyc_completed
- review_plan_options
- wallet_funded
- plan_selected
- savings_plan_created
- investment_plan_created
- review_current_investment
- request_early_withdrawal
- wallet_withdrawal
- investment_vests
- investment_proceeds_wallet_transfer
- assets_sale
- wallet_funding_failed
- withdrawal_failed

### 2.4. Transactions

A **transaction** captures and tracks every money movement within the application. Within the FinFlow application
context, transactions are generated for the following activities:
- **Wallet Funding** – Transfer of funds from an external bank account or payment source into a user's FinFlow wallet.
- **Wallet Withdrawal** – Transfer of funds from a user's FinFlow wallet to an external bank account.
- **Investment Position Funding** – Transfer of funds from a user's wallet into a savings or investment position.
- **Investment Proceeds Wallet Transfer** – Transfer of principal and accrued returns from a matured or withdrawn_early investment position back into the user's wallet.

Transactions serve as the primary source for:
- Wallet balance calculations
- Assets Under Management (AUM) reporting
- Funding and withdrawal analytics
- Investment contribution analysis
- Cash flow reporting
- Customer financial behaviour analysis

Each transaction records the amount, transaction type, source account, transaction timestamp, and transaction status.

---

## 3. Data Generation Framework (Simulation Rules)
### 3.1 Data Generation Principles

The FinFlow synthetic dataset is generated using deterministic business rules designed to emulate realistic customer behaviour within a digital wealth management platform.

The generation framework follows the following principles:

- Business-driven rather than random generation.
- Customer behaviour is influenced by persona assignment.
- Event generation follows lifecycle progression rules.
- Financial transactions must satisfy balance and product constraints.
- Historical records are preserved to support trend analysis.
- Daily incremental loads simulate real operational activity.

### 3.2 Customer Lifecycle Simulation

Customers progress through the following lifecycle stages:

Acquisition
→ Onboarding
→ Activation
→ Consideration
→ Adoption
→ Engagement
→ Retention

Not all users successfully progress through every stage.
Transition probabilities are influenced by customer persona and behavioural segment.

### 3.3 Persona Assignment Logic

Each generated user is assigned a persona using weighted probability distributions.

The persona determines:

- Age range
- Income range
- Acquisition channel
- Wallet activation likelihood
- Funding behaviour
- Behavioural segment assignment

### 3.4 Behavioural Simulation Logic

Behavioural segments drive customer activity generation.

The following attributes are influenced by behavioural segment:

- Monthly login frequency
- Deposit frequency
- Product adoption likelihood
- Investment frequency
- Retention probability
- Withdrawal probability

| Behaviour Segment | Login Frequency (per Month) | Deposit Frequency (per Month) | Investment Frequency (per Month) | Typical Behaviour |
|-------------------|----------------------------|------------------------------|----------------------------------|-------------------|
| High Engagement High Balance | 20 – 40 | 2 – 4 | 1 – 4 | Frequent platform usage, multiple active products, highest balances and retention. |
| High Engagement Low Balance | 15 – 35 | 1 – 3 | 0 – 1 | Frequent engagement but lower balances and smaller contributions. |
| Moderate Engagement High Balance | 6 – 15 | 1 – 2 | 1 – 2 | Periodic platform usage with larger balances and long-term investment behaviour. |
| Moderate Engagement Low Balance | 4 – 12 | 0 – 2 | 0 – 1 | Average users with moderate product adoption and contribution levels. |
| Low Engagement High Balance | 1 – 5 | 0 – 1 | 0 – 1 | Infrequent platform usage but maintains substantial balances and longer holding periods. |
| Low Engagement Low Balance | 0 – 3 | 0 – 1 | 0 | Minimal platform activity, low balances, and highest churn risk. |

### 3.5. Event Generation Rules

### signup_completed

Trigger:
- A  prospective customer successfully completes account registration.

Business Rule:
- User must be at least 18 years old.
- User must be assigned a valid customer persona.
- User must be assigned an acquisition channel.
- User is created with a unique user ID.
- A wallet is automatically provisioned for the user at account creation.
- Newly created wallets are initially unactivated.
- KYC completion and wallet activation are not required at signup.
- Each user can only complete account registration once.

Generated Tables:
- dim_user
- dim_wallet
- fact_user_event
- fact_wallet_balance

### app_login

Trigger:
- A registered user successfully authenticates and logs into the application.

Business Rules:
- User must have successfully completed account registration.
- User account must exist in the system.
- User may be in a Registered, KYC Completed, or Activated state.
- Multiple login events may be generated by the same user over time.

Generated Tables:
- fact_user_event

### kyc_completed

Trigger:
- A registered user successfully completes identity verification (KYC)

Business Rules:
- User must have successfully completed account registration.
- User account must exist in the system.
- KYC can only be completed once per user.
- User transitions from Registered User status to KYC Completed User status.
- KYC completion does not automatically activate the user's account.
- Wallet funding must occur before account activation.

Generated Tables:
- dim_user
- fact_user_event


### wallet_funded

Trigger:
- User must have completed KYC
- User must be logged into the application

Business Rule:
- User must have completed KYC verification.
- Wallet funding transfers funds from an external account into the user's wallet.
- The first successful wallet funding activates the user's account.
- A transaction record is generated to capture the funding activity.
- Users may perform multiple wallet funding transactions over time.

Generated Tables:
- fact_user_event
- fact_transaction
- dim_wallet
- fact_wallet_balance

### review_plan_options

Trigger:
- User must be logged into the application

Business Rule:
- This is an action that precedes investment plan creation
- It could also be a general user action that does not end up in a plan creation

Generated Tables:
- fact_user_event

### plan_selected

Trigger:
- User must be logged into the application
- User must have reviewed possible plan options
- User must have completed identity verification (KYC)
- User's account must be activated by completing an initial wallet funding

Business Rule:
- User selects a specific savings or investment plan.
- Plan selection does not transfer funds.
- Plan selection does not create a funded investment position.
- A user may select multiple plans over time.
- This event represents progression from Consideration to Adoption.

Generated Tables:
- fact_user_event

### savings_plan_created

Trigger:
- User must be logged into the application.
- User must have reviewed available plan options.
- User must have completed identity verification (KYC).
- User account must be activated through successful wallet funding.
- User must have selected a savings plan.
- User wallet balance must be sufficient to fund the selected plan.

Business Rule:
- User creates and funds a savings plan.
- Funds are transferred from the user's wallet to a new savings position.
- Funding amount must be greater than zero.
- The savings position is created with an Active status.
- A transaction record is generated to capture the transfer of funds.
- This event represents successful product adoption and financial commitment by the user.
- A user may create multiple savings plans over time. 

Generated Tables:
- fact_investment_position
- fact_user_event
- fact_transaction
- fact_wallet_balance

### investment_plan_created

Trigger:
- User must be logged into the application.
- User must have reviewed available plan options.
- User must have completed identity verification (KYC).
- User account must be activated through successful wallet funding.
- User must have selected an investment plan.
- User wallet balance must be sufficient to fund the selected plan.

Business Rule:
- User creates and funds an investment plan.
- Funds are transferred from the user's wallet to a new investment position.
- Funding amount must be greater than zero.
- The investment position is created with an Active status.
- A transaction record is generated to capture the transfer of funds.
- This event represents successful product adoption and financial commitment by the user.
- A user may create multiple investment plans over time. 

Generated Tables:
- fact_investment_position
- fact_user_event
- fact_transaction
- fact_wallet_balance

### review_current_investment
Trigger:
- User must be logged into the application.
- User must have completed identity verification (KYC).
- User account must be activated through successful wallet funding.
- User must have at least one active savings or investment position.

Business Rule:
- Only users with active investment positions can trigger this event
- Users may review their portfolio multiple times throughout the lifecycle of an investment position.
- Reviewing an investment does not alter balances, returns, tenure, or investment status.
- This event represents ongoing customer engagement with FinFlow products.
- Multiple review events may be generated by the same user over time.

Generated Tables:
- fact_user_event

### request_early_withdrawal
Trigger:
- User must be logged into the application.
- User must have completed identity verification (KYC).
- User account must be activated through successful wallet funding.
- User must have at least one active savings or investment position.
- The selected plan must permit early withdrawal.

Business Rule:
- Only active investment positions that allow early withdrawal can trigger this event
- The investment position must not have reached its maturity date.
- An early withdrawal penalty may be applied based on the selected plan.
- The investment position transitions from Active to Terminated status.
- Investment proceeds remain within the investment position until they are transferred back to the user's wallet.
- This event represents a potential churn-risk signal and reduced product retention.
- A user may perform multiple early withdrawals over time across different investment positions.

Generated Tables:
- fact_user_event

### investment_vests
Trigger:
- User must have at least one active savings or investment position.
- The investment position must have reached its maturity date.
- This is a system generated event, it does not require any user login

Business Rule:
- This event is automatically generated when an investment reaches its maturity date.
- No user action is required to trigger this event.
- Only active investment positions and plans with a pre-defined tenure period can vest.
- Vested investments become eligible for proceeds transfer back to the user's wallet.
- This event represents successful completion of an investment lifecycle.

Generated Tables:
- fact_user_event

### investment_proceeds_wallet_transfer
Trigger:
- An investment position has either matured (vested) or been terminated (withdrwan early) through an approved early withdrawal.

Business Rule:
- Principal and accrued returns are transferred from the investment position to the user's wallet.
- Applicable early withdrawal penalties are deducted prior to transfer.
- A transaction record is created to capture the transfer of funds.
- The transfer amount must be greater than zero.

Generated Tables:
- fact_user_event
- fact_transaction
- fact_investment_position
- fact_wallet_balance

### wallet_withdrawal
Trigger:
- User must be logged into the application.
- User account must be activated through successful wallet funding.
- User wallet balance must be sufficient to support the withdrawal amount.

Business Rule:
- Funds are transferred from the user's wallet to an external bank account.
- Withdrawal amount must not exceed the available wallet balance.
- A transaction record is created to capture the movement of funds.
- Users may perform multiple wallet withdrawals over time.
- This event represents customer liquidity activity.

Generated Tables:
- fact_user_event
- fact_transaction

### assets_sale
Trigger:
- User must be logged into the application.
- User must have at least one active investment position.
- The investment position must contain sellable assets.

Business Rule:
- User liquidates some or all assets held within an investment position.
- Asset sale proceeds remain within the investment position until transferred to the user's wallet.
- Asset sales may occur multiple times throughout the lifecycle of an investment.
- A successful asset sale may subsequently trigger an investment_proceeds_wallet_transfer event.
- This event represents portfolio management and liquidity activity.

Generated Tables:
- fact_user_event

### wallet_funding_failed
Trigger:
- User must be logged into the application.
- User must have completed account registration.
- User must initiate a wallet funding attempt.

Business Rule:
- Wallet funding transaction fails before funds are credited to the wallet.
- Failure may occur due to insufficient funds, payment provider issues, bank declines, network issues, or fraud checks.
- No wallet balance update occurs.
- Multiple failed funding attempts may occur before a successful wallet funding.
- A successful retry may subsequently trigger a `wallet_funded` event.
- This event is used to measure funding friction and activation drop-off.

Generated Tables:
- fact_user_event
- fact_transaction

### withdrawal_failed
Trigger:
- User must be logged into the application.
- User must initiate a wallet withdrawal request.

Business Rule:
- Withdrawal request fails before funds are successfully transferred to the user's destination account.
- Failure may occur due to insufficient wallet balance, invalid account details, payment processor issues, fraud controls, or compliance restrictions.
- Wallet balance remains unchanged.
- User may retry the withdrawal at a later time.
- A successful retry may subsequently trigger a wallet_withdrawal event.
- This event is used to monitor withdrawal reliability and customer experience.

Generated Tables:
- fact_user_event
- fact_transaction


### Transaction Generation Rules

Transactions are generated only when triggered by qualifying user events.

Transaction Types:

- Wallet Funding
- Wallet Withdrawal
- Investment Funding
- Investment Proceeds Transfer

---

## 4. Dimensional Modelling Framework

### 4.1 Warehouse Architecture

The analytics warehouse follows a Medallion Architecture:

Bronze → Raw Source Data
Silver → Cleansed & Validated Data
Gold → Analytics & Reporting Layer

### 4.2 Star Schema Design

The Gold layer follows Kimball dimensional modelling principles.

fact_user_event
 ├── dim_user
 ├── dim_date
 └── dim_event_type

fact_transaction
 ├── dim_user
 ├── dim_wallet
 └── dim_date

fact_investment_position
 ├── dim_user
 ├── dim_plan
 ├── dim_product
 └── dim_date

 fact_wallet_balance
    ├── dim_user
    ├── dim_wallet
    └── dim_date

 ### 4.3 Fact Grain Table

 ### fact_user_event

Grain:
One record per user event occurrence.

### fact_transaction

Grain:
One record per financial transaction.

### fact_investment_position

Grain:
One record per investment position.

### fact_wallet_balance

Grain:
One record per user wallet account.

### 4.4 Slowly Changing Dimensions
The platform uses Type 1 dimensions.

Historical tracking is handled through fact tables rather than dimensional versioning.

### 4.5 Data Lineage

Python
↓
Parquet
↓
Azure Blob Storage
↓
Snowflake Bronze
↓
Snowflake Silver
↓
Snowflake Gold
↓
Power BI

---

## 5. Product & Funnel Analysis Framework

### 5.1. Customer Lifecycle Funnel
→ Acquisition
→ Onboarding
→ Activation
→ Consideration
→ Adoption
→ Engagement
→ Retention
→ Churn

The events modeled by event stage on the platform is as follows:

| Stage         | Event                     |
| ------------- | ------------------------- |
| Acquisition   | signup_completed          |
| Onboarding    | kyc_completed             |
| Activation    | wallet_funded             |
| Consideration | review_plan_options       |
| Consideration | plan_selected             |
| Adoption      | savings_plan_created      |
| Adoption      | investment_plan_created   |
| Engagement    | app_login                 |
| Engagement    | review_current_investment |
| Retention     | investment_vests          |
| Retention     | wallet_withdrawal         |
| Churn         | request_early_withdrawal  |

### 5.2. Product Adoption Framework

### Savings Adoption

signup
→ kyc_completed
→ wallet_funded
→ savings_plan_created

### Investment Adoption

signup
→ kyc_completed
→ wallet_funded
→ investment_plan_created

### 5.3. Retention Framework

Retention is measured using:

- Day 7 retention
- Day 30 retention
- Day 90 retention
- Monthly active users

### 5.4. Executive KPI Categories

Growth KPIs
- Signups
- Activation Rate

Engagement KPIs
- Monthly Active Users
- Login Frequency

Product KPIs
- Product Adoption Rate

Financial KPIs
- AUM
- Net Deposits
- Average Wallet Balance

Retention KPIs
- Retention Rate
- Churn Rate


---

## 6. Business Metric Definitions

All business metrics and KPI definitions can be found on `docs/metrics/metrics_definition.md`

---

## 7. Design Principles

- Business definitions **precede** technical implementation
- Fact tables strictly adhere to grain
- Dimensions are reusable and consistent
- Metrics are standardized across all layers
- Simulation logic is clearly separated from business logic
---
## 8. Data Refresh and Cadence
| Component                        | Cadence       | Description                                                                              |
| ---------------------------------| ------------- | ----------------------------------------------------------------------------------------|
| User Generation & Updates                 | Daily         | Generate new users and update kyc activation status. |
| Wallet Updates                   | Daily         | Create new wallets and update wallet activation status based on user activity.          |
| Events & Transaction Generation  | Daily         | Generate customer activity events, deposits, withdrawals, transfers, and investment transactions. |
| dbt Model Refresh                | Daily         | Incremental dbt transformations and loading newly generated data                  |
| Power BI Semantic Model Refresh | Daily | Refresh Power BI semantic models after dbt model execution. |
| Dashboard Refresh | Daily | Refresh Power BI reports and dashboards. |

### Refresh Sequence

1. Generate synthetic source data using Python
2. Validate and stage datasets in DuckDB
3. Persist raw data to Azure Blob Storage
4. Load data into Snowflake
5. Execute dbt transformations
6. Run data quality validations
7. Refresh Power BI semantic models
8. Refresh Power BI dashboards and reports

### Refresh Dependencies

The daily refresh process follows a strict dependency chain:

1. Python Data Generation
2. DuckDB Validation & Staging
3. Azure Blob Storage Load and Partitioning
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
| fact_investment_position | Incremental | Load newly created savings and investment positions. |
| fact_transaction | Incremental | Load newly generated financial transactions. |
| fact_wallet_balance | Incremental | Load wallet balance updates. |

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
This document is authored and maintained by [Ajibola Komolafe](https://www.linkedin.com/in/ajibola-komo/) as part of a solo portfolio project. All business rules, simulation logic, and metric definitions reflect intentional design decisions made by the author.

---
## 10. Conclusion
This framework enables:
- End-to-end product analytics across acquisition, activation, engagement, retention, and investment behavior.
- Scalable analytics architecture leveraging Azure Blob Storage, Snowflake, dbt, Airflow, and Power BI.
- A scalable analytics engineering workflow built on synthetic but business-realistic data.
- Dimensional modeling, metric governance, and semantic reporting best practices.
- Portfolio-ready dashboards and analytical use cases spanning product, growth, operations, and executive reporting.
- Realistic simulation of event-driven customer and investment behavior. 
---

## Project Links
[LinkedIn](https://www.linkedin.com/in/ajibola-komo/) · [GitHub](https://github.com/ajibola-komo/FinFlow-Product-Analytics-Engineering-Platform) ·
[Power BI](https://) · [Kaggle Dataset](https://www.kaggle.com/datasets/ajibsss/)



