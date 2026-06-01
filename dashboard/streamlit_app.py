import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Food Delivery Command Center",
    page_icon="🍔",
    layout="wide"
)

# ---------------------------------------------------
# SNOWFLAKE SESSION
# ---------------------------------------------------

session = get_active_session()

session.sql("USE ROLE ACCOUNTADMIN").collect()
session.sql("USE DATABASE FOOD_DELIVERY_DB").collect()
session.sql("USE SCHEMA GOLD").collect()

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title("🍔 Food Delivery Command Center")
st.markdown("### Real-Time Food Delivery Analytics Platform")

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "📊 Business Analytics",
    "🛡 Data Quality Center",
    "⚙ Pipeline Monitoring"
])

# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------


with tab1:

    st.header("📊 Business Analytics")

    # =====================================
    # KPI CARDS
    # =====================================

    kpi = session.sql("""
    SELECT
        COUNT(*) TOTAL_ORDERS,
        ROUND(SUM(FINAL_AMOUNT),2) TOTAL_REVENUE,
        ROUND(AVG(FINAL_AMOUNT),2) AVG_ORDER_VALUE,
        COUNT(DISTINCT CUSTOMER_SK) UNIQUE_CUSTOMERS
    FROM GOLD.FACT_ORDERS
    """).to_pandas()

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "📦 Total Orders",
        f"{int(kpi['TOTAL_ORDERS'][0]):,}"
    )

    c2.metric(
        "💰 Revenue",
        f"₹ {int(kpi['TOTAL_REVENUE'][0]):,}"
    )

    c3.metric(
        "👥 Customers",
        f"{int(kpi['UNIQUE_CUSTOMERS'][0]):,}"
    )

    c4.metric(
        "🛒 Avg Order Value",
        f"₹ {int(kpi['AVG_ORDER_VALUE'][0]):,}"
    )

    st.divider()

    # =====================================
    # REVENUE BY CITY
    # =====================================

    city_df = session.sql("""
    SELECT
        r.CITY,
        SUM(f.FINAL_AMOUNT) REVENUE
    FROM GOLD.FACT_ORDERS f
    JOIN GOLD.DIM_RESTAURANT r
        ON f.RESTAURANT_SK = r.RESTAURANT_SK
    GROUP BY r.CITY
    ORDER BY REVENUE DESC
    """).to_pandas()

    # =====================================
    # ORDERS BY CUISINE
    # =====================================

    cuisine_df = session.sql("""
    SELECT
        r.CUISINE_TYPE,
        COUNT(*) ORDERS
    FROM GOLD.FACT_ORDERS f
    JOIN GOLD.DIM_RESTAURANT r
        ON f.RESTAURANT_SK = r.RESTAURANT_SK
    GROUP BY r.CUISINE_TYPE
    ORDER BY ORDERS DESC
    """).to_pandas()

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("🏙 Revenue By City")
        st.bar_chart(
            city_df.set_index("CITY")
        )

    with col2:
        st.subheader("🍕 Orders By Cuisine")
        st.bar_chart(
            cuisine_df.set_index("CUISINE_TYPE")
        )

    st.divider()

    # =====================================
    # PAYMENT ANALYTICS
    # =====================================

    payment_df = session.sql("""
    SELECT
        PAYMENT_METHOD,
        COUNT(*) ORDERS
    FROM GOLD.FACT_ORDERS
    GROUP BY PAYMENT_METHOD
    ORDER BY ORDERS DESC
    """).to_pandas()

    st.subheader("💳 Orders Payment Method")

    st.bar_chart(
        payment_df.set_index("PAYMENT_METHOD")
    )

    st.divider()

    # =====================================
    # MONTHLY REVENUE TREND
    # =====================================

    trend_df = session.sql("""
    SELECT
        d.MONTH_NAME,
        d.MONTH_NUMBER,
        SUM(f.FINAL_AMOUNT) REVENUE
    FROM GOLD.FACT_ORDERS f
    JOIN GOLD.DIM_DATE d
        ON f.DATE_SK = d.DATE_SK
    GROUP BY
        d.MONTH_NAME,
        d.MONTH_NUMBER
    ORDER BY d.MONTH_NUMBER
    """).to_pandas()

    st.subheader("📈 Monthly Revenue Trend")

    st.line_chart(
        trend_df.set_index("MONTH_NAME")["REVENUE"]
    )

    st.divider()

    # =====================================
    # TOP RESTAURANTS
    # =====================================

    restaurant_df = session.sql("""
    SELECT
        r.RESTAURANT_NAME,
        SUM(f.FINAL_AMOUNT) REVENUE
    FROM GOLD.FACT_ORDERS f
    JOIN GOLD.DIM_RESTAURANT r
        ON f.RESTAURANT_SK = r.RESTAURANT_SK
    GROUP BY r.RESTAURANT_NAME
    ORDER BY REVENUE DESC
    LIMIT 10
    """).to_pandas()

    st.subheader("🏆 Top 10 Restaurants")

    st.dataframe(
        restaurant_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================
    # DELIVERY PERFORMANCE
    # =====================================

    delivery_df = session.sql("""
    SELECT
        ROUND(AVG(ESTIMATED_DELIVERY_TIME),2) EST_TIME,
        ROUND(AVG(ACTUAL_DELIVERY_TIME),2) ACT_TIME
    FROM GOLD.FACT_ORDERS
    """).to_pandas()

    est = float(delivery_df["EST_TIME"][0])
    act = float(delivery_df["ACT_TIME"][0])

    st.subheader("🚚 Delivery Performance")

    d1,d2,d3 = st.columns(3)

    d1.metric(
        "Estimated Time",
        f"{est:.1f} mins"
    )

    d2.metric(
        "Actual Time",
        f"{act:.1f} mins"
    )

    d3.metric(
        "Average Delay",
        f"{(act-est):.1f} mins"
    )

    pass

# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------

with tab2:

    st.header("🛡 Data Quality Center")
     

    # ==================================================
    # KPI SECTION
    # ==================================================

    bronze_df = session.sql("""
        SELECT COUNT(*) CNT
        FROM BRONZE.ORDER_DETAILS
    """).to_pandas()

    silver_df = session.sql("""
        SELECT COUNT(*) CNT
        FROM SILVER.ORDER_CLEAN
    """).to_pandas()

    quarantine_df = session.sql("""
        SELECT COUNT(*) CNT
        FROM QUARANTINE.BAD_ORDER_RECORDS
    """).to_pandas()

    bronze_count = int(bronze_df["CNT"][0])
    silver_count = int(silver_df["CNT"][0])
    quarantine_count = int(quarantine_df["CNT"][0])

    processed = silver_count + quarantine_count

    if processed > 0:
        dq_score = round((silver_count / processed) * 100, 2)
    else:
        dq_score = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📥 Bronze Records",
        f"{bronze_count:,}"
    )

    c2.metric(
        "✅ Silver Records",
        f"{silver_count:,}"
    )

    c3.metric(
        "❌ Quarantined",
        f"{quarantine_count:,}"
    )

    c4.metric(
        "🎯 Data Quality %",
        f"{dq_score}%"
    )

    st.divider()

    # ==================================================
    # GOOD VS BAD RECORDS
    # ==================================================

    st.subheader("📊 Good vs Bad Records")

    dq_chart = pd.DataFrame({
        "Record Type": [
            "Good Records",
            "Bad Records"
        ],
        "Count": [
            silver_count,
            quarantine_count
        ]
    })

    st.bar_chart(
        dq_chart.set_index("Record Type")
    )

    st.divider()

    # ==================================================
# VALIDATION FRAMEWORK
# ==================================================

    st.subheader("🔍 Data Validation Framework")
    
    validation_df = pd.DataFrame({
        "Validation Category": [
            "Mandatory Fields",
            "Referential Integrity",
            "Business Rules",
            "Timestamp Logic"
        ],
    
        "Validation Checks": [
            "ORDER_ID, CUSTOMER_ID, RESTAURANT_ID, ORDER_STATUS",
            "CUSTOMER_ID, RESTAURANT_ID, AGENT_ID, PROMO_CODE",
            "Amount > 0, Distance > 0, Valid Status & Source",
            "Accepted ≥ Placed, Delivered ≥ Accepted"
        ],
    
        "Status": [
            "✅ Implemented",
            "✅ Implemented",
            "✅ Implemented",
            "✅ Implemented"
        ]
    })
    
    st.dataframe(
        validation_df,
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # PIPELINE FLOW
    # ==================================================

    st.subheader("⚙ Pipeline Flow")

    st.markdown("""
    ```text
    ADLS
      ↓
    External Stage
      ↓
    Bronze Layer
      ↓
    Stream
      ↓
    Task
      ↓
    Stored Procedure
      ↓
    Silver Layer
      ↓
    Quarantine Layer
      ↓
    Gold Layer
    ```
    """)

    st.divider()

    # ==================================================
    # RECENT BAD RECORDS
    # ==================================================

    st.subheader("🚨 Recent Quarantined Records")

    bad_records = session.sql("""
        SELECT
            ORDER_ID,
            CUSTOMER_ID,
            RESTAURANT_ID,
            ORDER_STATUS,
            ORDER_SOURCE,
            SOURCE_FILE_NAME
        FROM QUARANTINE.BAD_ORDER_RECORDS
        LIMIT 20
    """).to_pandas()

    st.dataframe(
        bad_records,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==================================================
    # PIPELINE HEALTH
    # ==================================================

    st.subheader("💚 Pipeline Health")

    if dq_score >= 95:
        st.success(
            f"Excellent Data Quality ({dq_score}%)"
        )
    elif dq_score >= 85:
        st.warning(
            f"Moderate Data Quality ({dq_score}%)"
        )
    else:
        st.error(
            f"Data Quality Needs Attention ({dq_score}%)"
        )

# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------

with tab3:

    st.header("⚙ Pipeline Monitoring")

    # ==================================================
    # STREAM STATUS
    # ==================================================

    stream_df = session.sql("""
        SELECT SYSTEM$STREAM_HAS_DATA('PUBLIC.STREAM_ORDER_DETAILS')
        AS STREAM_HAS_DATA
    """).to_pandas()

    stream_status = str(stream_df["STREAM_HAS_DATA"][0])

    # ==================================================
    # TASK STATUS
    # ==================================================

    task_df = session.sql("""
        SHOW TASKS LIKE 'TASK_ORDER_PIPELINE'
    """).to_pandas()

    # Clean weird Snowflake column names
    task_df.columns = [
        c.replace('"', '').strip()
        for c in task_df.columns
    ]

    task_state = task_df.iloc[0]["state"]

    # ==================================================
    # KPI CARDS
    # ==================================================

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "📡 Stream Has Data",
            stream_status
        )

    with c2:
        st.metric(
            "⚙ Task Status",
            task_state
        )

    st.divider()

    # ==================================================
    # PIPELINE COMPONENTS
    # ==================================================

    st.subheader("🏗 Pipeline Components")

    component_df = pd.DataFrame({
        "Component": [
            "External Stage",
            "Bronze Layer",
            "Snowflake Stream",
            "Snowflake Task",
            "Stored Procedure",
            "Silver Layer",
            "Quarantine Layer",
            "Gold Layer"
        ],

        "Purpose": [
            "Landing Zone",
            "Raw Data Storage",
            "Incremental Change Capture",
            "Automation",
            "Validation Logic",
            "Clean Records",
            "Bad Records Storage",
            "Analytics Layer"
        ],

        "Status": [
            "✅ Active",
            "✅ Active",
            "✅ Active",
            "✅ Active",
            "✅ Active",
            "✅ Active",
            "✅ Active",
            "✅ Active"
        ]
    })

    st.dataframe(
        component_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==================================================
    # RECORD FLOW
    # ==================================================

    st.subheader("📊 Record Flow Summary")

    flow_df = session.sql("""
        SELECT
            (SELECT COUNT(*) FROM BRONZE.ORDER_DETAILS) AS BRONZE_COUNT,
            (SELECT COUNT(*) FROM SILVER.ORDER_CLEAN) AS SILVER_COUNT,
            (SELECT COUNT(*) FROM QUARANTINE.BAD_ORDER_RECORDS) AS QUARANTINE_COUNT
    """).to_pandas()

    st.dataframe(
        flow_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ==================================================
    # ARCHITECTURE OVERVIEW
    # ==================================================

    st.subheader("🏛 Architecture Overview")

    st.code("""
Azure Data Lake
        │
        ▼
  External Stage
        │
        ▼
   Bronze Layer
        │
        ▼
 Snowflake Stream
        │
        ▼
  Snowflake Task
        │
        ▼
 Stored Procedure
      ↙      ↘
     ▼        ▼
 Silver   Quarantine
     │
     ▼
   Gold Layer
     │
     ▼
 Streamlit Dashboard
    """, language="text")

    st.divider()

    # ==================================================
    # PROJECT HIGHLIGHTS
    # ==================================================

    st.subheader("🚀 Project Highlights")

    st.success("✔ End-to-End Snowflake Data Pipeline")
    st.success("✔ Incremental Processing using Streams")
    st.success("✔ Automated Processing using Tasks")
    st.success("✔ Stored Procedure Based Validation")
    st.success("✔ Quarantine Layer for Bad Records")
    st.success("✔ Star Schema Gold Layer")
    st.success("✔ Business Analytics Dashboard")
    st.success("✔ Data Quality Monitoring")