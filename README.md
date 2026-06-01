# food_delivery_system
# Food Delivery Data Platform using Snowflake

## Project Overview

This project implements an end-to-end Data Engineering pipeline for a Food Delivery Platform using Snowflake. The solution follows a Medallion Architecture (Bronze, Silver, Gold) and automates data ingestion, validation, transformation, monitoring, and analytics reporting.

The pipeline processes order, customer, restaurant, agent, promotion, and payment data while enforcing business rules and referential integrity.

---

# Objectives

* Build a scalable cloud-native data platform.
* Automate ingestion and transformation workflows.
* Implement data quality validation and quarantine handling.
* Design dimensional models for analytics.
* Create business and operational dashboards using Streamlit in Snowflake.

---

# Architecture

ADLS → External Stage → Bronze Layer → Stream → Task → Stored Procedure → Silver Layer / Quarantine Layer → Gold Layer → Streamlit Dashboard

---

# Technology Stack

| Component           | Technology                     |
| ------------------- | ------------------------------ |
| Cloud Storage       | Azure Data Lake Storage (ADLS) |
| Data Warehouse      | Snowflake                      |
| Ingestion           | Snowpipe                       |
| Change Data Capture | Snowflake Streams              |
| Automation          | Snowflake Tasks                |
| Processing          | Snowflake Stored Procedures    |
| Data Modeling       | Star Schema                    |
| Dashboard           | Streamlit in Snowflake         |

---

# Data Layers

## Bronze Layer

Purpose:

* Store raw source data exactly as received.
* Preserve source records without transformation.

Tables:

* CUSTOMER_DETAILS
* RESTAURANT_DETAILS
* AGENT_DETAILS
* PROMOTION_DETAILS
* ORDER_DETAILS
* PAYMENT_DETAILS

---

## Silver Layer

Purpose:

* Data cleansing
* Standardization
* Validation
* Referential integrity enforcement

Tables:

* CUSTOMER_CLEAN
* RESTAURANT_CLEAN
* AGENT_CLEAN
* PROMOTION_CLEAN
* ORDER_CLEAN
* PAYMENT_CLEAN

Validation Rules:

* Mandatory field checks
* Positive amount validation
* Delivery distance validation
* Valid order status validation
* Valid order source validation
* Timestamp consistency validation
* Customer referential integrity
* Restaurant referential integrity
* Agent referential integrity
* Promotion referential integrity

---

## Quarantine Layer

Purpose:

* Store invalid records rejected during validation.

Examples:

* Missing ORDER_ID
* Missing CUSTOMER_ID
* Invalid ORDER_STATUS
* Invalid ORDER_SOURCE
* Negative amounts
* Invalid delivery timestamps
* Missing foreign key references

Benefits:

* Prevents bad data from reaching analytics.
* Enables auditing and root cause analysis.

---

## Gold Layer

Purpose:

* Business analytics and reporting.

### Fact Table

FACT_ORDERS

Measures:

* TOTAL_AMOUNT
* DISCOUNT_AMOUNT
* DELIVERY_FEE
* TAX_AMOUNT
* FINAL_AMOUNT
* PAYMENT_AMOUNT
* REFUND_AMOUNT

### Dimension Tables

DIM_CUSTOMER

DIM_RESTAURANT

DIM_AGENT

DIM_PROMOTION

DIM_DATE

This layer follows a Star Schema design.

---

# Stream and Task Automation

## Stream

STREAM_ORDER_DETAILS

Purpose:

* Capture incremental changes from ORDER_DETAILS.
* Enable CDC-based processing.

---

## Task

TASK_ORDER_PIPELINE

Purpose:

* Automatically process new order records.
* Trigger validation logic when stream receives data.

---

# Stored Procedure

PROCESS_ORDER_STREAM()

Responsibilities:

* Read incremental records from stream.
* Apply business validations.
* Insert valid records into Silver Layer.
* Insert invalid records into Quarantine Layer.
* Maintain automated processing workflow.

---

# Data Quality Framework

Implemented validations:

### Mandatory Fields

* ORDER_ID
* CUSTOMER_ID
* RESTAURANT_ID
* ORDER_STATUS
* ORDER_PLACED_AT

### Business Rules

* TOTAL_AMOUNT > 0
* FINAL_AMOUNT > 0
* DELIVERY_DISTANCE_KM > 0
* Valid ORDER_STATUS values
* Valid ORDER_SOURCE values

### Timestamp Rules

* ORDER_ACCEPTED_AT >= ORDER_PLACED_AT
* ORDER_DELIVERED_AT >= ORDER_ACCEPTED_AT

### Referential Integrity

* CUSTOMER_ID exists in CUSTOMER_CLEAN
* RESTAURANT_ID exists in RESTAURANT_CLEAN
* AGENT_ID exists in AGENT_CLEAN
* PROMO_CODE exists in PROMOTION_CLEAN

---

# Dashboard Features

## Tab 1 – Business Analytics

* Total Orders
* Total Revenue
* Average Order Value
* Unique Customers
* Revenue by City
* Orders by Cuisine
* Payment Analytics
* Monthly Revenue Trend
* Top Restaurants
* Delivery Performance

---

## Tab 2 – Data Quality Center

* Bronze Record Count
* Silver Record Count
* Quarantine Record Count
* Data Quality Score
* Validation Framework
* Quarantined Records Monitoring
* Pipeline Health Status

---

## Tab 3 – Pipeline Monitoring

* Stream Status
* Task Status
* Pipeline Components
* Record Flow Summary
* Architecture Overview
* Project Highlights

---

# Key Achievements

* Implemented Medallion Architecture.
* Automated data processing using Streams and Tasks.
* Built robust data quality validation framework.
* Implemented Quarantine Layer for bad records.
* Designed dimensional model for analytics.
* Developed Streamlit dashboard for business and operational monitoring.
* Achieved end-to-end automated data pipeline execution.

---

# Conclusion

The project successfully demonstrates a production-style Snowflake Data Engineering solution capable of ingesting, validating, processing, monitoring, and analyzing food delivery platform data using modern cloud data architecture principles.
#url
https://app.snowflake.com/lbpvuxz/rw43062/#/streamlit-apps/FOOD_DELIVERY_DB.PUBLIC.FOOD_DELIVERY_SYSTEM
