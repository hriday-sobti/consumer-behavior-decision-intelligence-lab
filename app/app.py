"""Consumer Behavior Decision Intelligence Lab (CBDIL) - Workbench Application.

Implements the 6 core analytical views:
  1. Overview: Executive KPIs, trends, concentration, stand-out observations
  2. Segments: Behavioral dimensions, profile cards, and comparative distributions
  3. Behavior Over Time: Longitudinal dynamics, active customer trend, state transitions
  4. Decision Signals: Signal inventory, severity breakdowns, customer drill-down
  5. Customer Explorer: Individual customer diagnostic card, timeline, and audit reasons
  6. Methodology & Controls: Audit gates, pipeline controls, lineage, limitations
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Application configuration
st.set_page_config(
    page_title="Consumer Behavior Decision Intelligence Lab",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main { background-color: #fcfcfc; }
    h1, h2, h3 { color: #1f2d3d; font-family: 'Segoe UI', -apple-system, sans-serif; }
    .stMetric { background-color: #f7f9fa; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; }
    .metric-sub { font-size: 0.82rem; color: #64748b; margin-top: 4px; }
    .callout-box { background-color: #f1f5f9; border-left: 4px solid #1f4e78; padding: 12px 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
    .warning-box { background-color: #fffbeb; border-left: 4px solid #d97706; padding: 12px 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = Path(__file__).resolve().parent.parent / "outputs" / "exports"

@st.cache_data
def load_data():
    c_df = pd.read_csv(DATA_DIR / "customer_summary.csv")
    s_df = pd.read_csv(DATA_DIR / "segment_summary.csv")
    m_df = pd.read_csv(DATA_DIR / "monthly_summary.csv")
    sig_df = pd.read_csv(DATA_DIR / "decision_signals.csv")
    t_df = pd.read_csv(DATA_DIR / "state_transitions.csv")
    ctrl_df = pd.read_csv(DATA_DIR / "data_controls.csv")
    cohort_df = pd.read_csv(DATA_DIR / "cohort_summary.csv")
    country_df = pd.read_csv(DATA_DIR / "country_summary.csv")
    return c_df, s_df, m_df, sig_df, t_df, ctrl_df, cohort_df, country_df

c_df, s_df, m_df, sig_df, t_df, ctrl_df, cohort_df, country_df = load_data()

# Sidebar Navigation & Global Filters
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Analytical View",
    ["1. Executive Overview", "2. Behavioral Segments", "3. Behavior Over Time", 
     "4. Decision Signals", "5. Customer Explorer", "6. Methodology & Controls"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Analytical Filters")

# Country filter
all_countries = ["All"] + sorted(c_df["primary_country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Country Origin", all_countries, index=0)

# Segment filter
all_segments = ["All"] + sorted(c_df["segment_name"].unique().tolist())
selected_segment = st.sidebar.selectbox("Behavioral Segment", all_segments, index=0)

# State filter
all_states = ["All"] + sorted(c_df["behavioral_state"].unique().tolist())
selected_state = st.sidebar.selectbox("Lifecycle State", all_states, index=0)

# Apply global filters to customer summary
filtered_c = c_df.copy()
if selected_country != "All":
    filtered_c = filtered_c[filtered_c["primary_country"] == selected_country]
if selected_segment != "All":
    filtered_c = filtered_c[filtered_c["segment_name"] == selected_segment]
if selected_state != "All":
    filtered_c = filtered_c[filtered_c["behavioral_state"] == selected_state]

# ==============================================================================
# VIEW 1: EXECUTIVE OVERVIEW
# ==============================================================================
if page == "1. Executive Overview":
    st.title("Customer Overview")
    st.markdown("Understand the aggregate scale, spend distribution, and structural dimensions of the customer base.")

    # Top Metrics
    total_cust = len(filtered_c)
    active_cust = len(filtered_c[filtered_c["behavioral_state"].isin(["ENGAGED", "EMERGING", "REACTIVATED"])])
    tot_val = filtered_c["total_value"].sum()
    tot_orders = filtered_c["lifetime_orders"].sum()
    aov = tot_val / tot_orders if tot_orders > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Customers", f"{total_cust:,}")
    kpi2.metric("Active Accounts", f"{active_cust:,}", f"{active_cust/total_cust:.1%}" if total_cust > 0 else "")
    kpi3.metric("Total Spend", f"£{tot_val:,.0f}")
    kpi4.metric("Total Orders", f"{tot_orders:,}")
    kpi5.metric("Average Order Value", f"£{aov:,.2f}")

    # Section: What Stands Out
    st.markdown("""
    <div class="callout-box">
        <strong>What stands out from empirical evidence:</strong><br>
        1. <strong>Value Concentration</strong>: The top 5% of eligible accounts generate <strong>53.8%</strong> of total historical purchase value.<br>
        2. <strong>High-Value Softening</strong>: <strong>261</strong> accounts in the top spend tier experienced a &ge; 25% drop in recent 90-day activity, representing £1.2M+ in spend exposure.<br>
        3. <strong>Single-Order Rate</strong>: <strong>31.5%</strong> of accounts transacted exactly once and never returned over 24 months.
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # Monthly Spend Trend
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(x=m_df["year_month"], y=m_df["total_value"], name="Gross Spend (£)", marker_color="#1f4e78"))
        fig_m.add_trace(go.Scatter(x=m_df["year_month"], y=m_df["total_orders"], name="Order Volume", yaxis="y2", line={"color": "#d97706", "width": 2}))
        fig_m.update_layout(
            title="Monthly Spend and Order Volume Trend",
            xaxis_title="Month", yaxis={"title": "Spend (£)"},
            yaxis2={"title": "Orders", "overlaying": "y", "side": "right"},
            template="plotly_white", height=380, legend={"x": 0.01, "y": 0.99}
        )
        st.plotly_chart(fig_m, width='stretch')

    with col_right:
        # Segment Value Contribution
        fig_s = px.bar(
            s_df, x="segment_name", y="total_value", color="segment_name",
            text="value_share", title="Total Value Contribution by Segment",
            labels={"segment_name": "Segment", "total_value": "Spend (£)"},
            template="plotly_white", height=380,
            color_discrete_sequence=["#1f4e78", "#2e8b57", "#94a3b8"]
        )
        fig_s.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_s.update_layout(showlegend=False)
        st.plotly_chart(fig_s, width='stretch')

    # Lower Grid: Value Concentration Lorenz curve & State Distribution
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        sorted_vals = np.sort(filtered_c["total_value"].values)
        if len(sorted_vals) > 0 and sorted_vals.sum() > 0:
            cum_vals = np.cumsum(sorted_vals) / np.sum(sorted_vals) * 100
            cum_custs = np.linspace(0, 100, len(cum_vals))
            fig_lor = go.Figure()
            fig_lor.add_trace(go.Scatter(x=cum_custs, y=cum_vals, mode="lines", name="Observed Lorenz Curve", line={"color": "#1f4e78", "width": 3}))
            fig_lor.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines", name="Parity", line={"color": "#cbd5e1", "dash": "dash"}))
            fig_lor.update_layout(
                title="Customer Value Concentration (Empirical Lorenz Curve)",
                xaxis_title="Cumulative Customer Percentile (%)",
                yaxis_title="Cumulative Spend Share (%)",
                template="plotly_white", height=360
            )
            st.plotly_chart(fig_lor, width='stretch')

    with col_c2:
        state_counts = filtered_c["behavioral_state"].value_counts().reset_index()
        state_counts.columns = ["State", "Count"]
        fig_state = px.bar(
            state_counts, x="State", y="Count", color="State",
            title="Current Behavioral Lifecycle State Distribution",
            template="plotly_white", height=360,
            color_discrete_sequence=["#1f4e78", "#94a3b8", "#d97706", "#2e8b57", "#dc2626"]
        )
        fig_state.update_layout(showlegend=False)
        st.plotly_chart(fig_state, width='stretch')

# ==============================================================================
# VIEW 2: BEHAVIORAL SEGMENTS
# ==============================================================================
elif page == "2. Behavioral Segments":
    st.title("Behavioral Segments")
    st.markdown("Examine how eligible accounts separate across value, cadence, catalog breadth, and recency dimensions.")

    # Segment Profile Table
    st.subheader("Segment Analytical Profiles")
    disp_cols = [
        "segment_name", "customer_count", "customer_share", "total_value", "value_share",
        "median_recency", "median_frequency", "average_order_value", "median_interpurchase_gap"
    ]
    st.dataframe(
        s_df[disp_cols].style.format({
            "customer_count": "{:,}",
            "customer_share": "{:.1%}",
            "total_value": "£{:,.0f}",
            "value_share": "{:.1%}",
            "median_recency": "{:,.0f}d",
            "median_frequency": "{:,.0f}",
            "average_order_value": "£{:,.2f}",
            "median_interpurchase_gap": "{:,.1f}d"
        }),
        width='stretch'
    )

    col1, col2 = st.columns(2)
    with col1:
        # Scatter: Recency vs Log Spend
        fig_scat = px.scatter(
            filtered_c, x="recency_days", y="total_value", color="segment_name",
            log_y=True, title="Recency vs Spend Separation",
            labels={"recency_days": "Recency (Days)", "total_value": "Total Spend (£, Log Scale)"},
            template="plotly_white", height=420,
            color_discrete_sequence=["#1f4e78", "#2e8b57", "#94a3b8", "#d97706"]
        )
        st.plotly_chart(fig_scat, width='stretch')

    with col2:
        # Box plot: Product Breadth by Segment
        fig_box = px.box(
            filtered_c, x="segment_name", y="product_count", color="segment_name",
            title="Catalog Breadth (Unique SKUs) by Segment",
            labels={"product_count": "Unique SKUs Purchased", "segment_name": "Segment"},
            template="plotly_white", height=420,
            color_discrete_sequence=["#1f4e78", "#2e8b57", "#94a3b8", "#d97706"]
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, width='stretch')

    # Narrative Segment Deep-Dive Cards
    st.subheader("Behavioral Characterization & Strategic Inquiries")
    for _, row in s_df.iterrows():
        with st.expander(f"Segment: {row['segment_name']} ({row['customer_count']:,} accounts | {row['value_share']:.1%} value)"):
            st.markdown(f"**Primary Pattern**: {row['primary_behavior']}")
            st.markdown(f"**Secondary Pattern**: {row['secondary_behavior']}")
            st.markdown(f"**Descriptive Interpretation**: {row['interpretation']}")
            st.markdown(f"**Key Decision Question**: *{row['possible_business_question']}*")

# ==============================================================================
# VIEW 3: BEHAVIOR OVER TIME
# ==============================================================================
elif page == "3. Behavior Over Time":
    st.title("Behavior Over Time & State Transitions")
    st.markdown("Track longitudinal dynamics, customer acquisition cohorts, and month-over-month state migration.")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        # Monthly Active Accounts by State Stacked
        st.subheader("Monthly Customer State Composition")
        fig_comp = go.Figure()
        states_to_plot = [
            ("ENGAGED", "#1f4e78"), ("EMERGING", "#2e8b57"),
            ("REACTIVATED", "#d97706"), ("SOFTENING", "#eab308"),
            ("DORMANT", "#94a3b8")
        ]
        for st_name, col in states_to_plot:
            metric_col = f"{st_name.lower()}_customers"
            if metric_col in m_df.columns:
                fig_comp.add_trace(go.Bar(x=m_df["year_month"], y=m_df[metric_col], name=st_name, marker_color=col))

        fig_comp.update_layout(barmode="stack", template="plotly_white", height=400, xaxis_title="Month", yaxis_title="Customer Count")
        st.plotly_chart(fig_comp, width='stretch')

    with col_t2:
        st.subheader("State Migration Matrix (Aggregated)")
        # Heatmap
        state_matrix = t_df.groupby(["previous_state", "current_state"])["customer_count"].sum().unstack(fill_value=0)
        state_prob = state_matrix.div(state_matrix.sum(axis=1), axis=0).fillna(0.0)

        fig_trans = px.imshow(
            state_prob, text_auto=".1%", aspect="auto",
            labels={"x": "Current State", "y": "Previous State", "color": "Transition Rate"},
            color_continuous_scale="Blues", height=400
        )
        st.plotly_chart(fig_trans, width='stretch')

    # Cohort Retention Matrix
    st.subheader("Acquisition Cohort Retention Matrix")
    cohort_pivot = cohort_df[cohort_df["cohort_index"] <= 12].pivot(
        index="cohort_month", columns="cohort_index", values="retention_rate"
    )
    fig_cohort = px.imshow(
        cohort_pivot, text_auto=".1%", aspect="auto",
        labels={"x": "Months Since Acquisition (Index)", "y": "Acquisition Cohort", "color": "Retention"},
        color_continuous_scale="Teal", height=450
    )
    st.plotly_chart(fig_cohort, width='stretch')

# ==============================================================================
# VIEW 4: DECISION SIGNALS
# ==============================================================================
elif page == "4. Decision Signals":
    st.title("Decision Signals & Action Strategies")
    st.markdown("Deterministic, rule-based behavioral signals highlighting accounts that warrant review or capacity protection.")

    sig_counts = sig_df["signal_name"].value_counts().reset_index()
    sig_counts.columns = ["Signal", "Count"]

    col_sig1, col_sig2 = st.columns([1, 2])
    with col_sig1:
        st.subheader("Signal Inventory")
        fig_pie = px.bar(
            sig_counts, x="Count", y="Signal", orientation="h",
            color="Signal", template="plotly_white", height=380,
            color_discrete_sequence=["#1f4e78", "#2e8b57", "#d97706", "#eab308", "#dc2626", "#8b5cf6"]
        )
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, width='stretch')

    with col_sig2:
        st.subheader("Signal Severity Breakdown")
        sev_counts = sig_df.groupby(["signal_name", "signal_strength"]).size().unstack(fill_value=0).reset_index()
        fig_sev = px.bar(
            sev_counts, x="signal_name", y=["High", "Medium", "Low"],
            title="Severity Distribution by Triggered Signal",
            barmode="stack", template="plotly_white", height=380,
            color_discrete_map={"High": "#dc2626", "Medium": "#f59e0b", "Low": "#94a3b8"}
        )
        st.plotly_chart(fig_sev, width='stretch')

    st.subheader("Triggered Customer Accounts Detail Table")
    selected_sig_type = st.selectbox("Filter by Triggered Signal", ["All"] + sorted(sig_df["signal_name"].unique().tolist()))
    
    view_sig_df = sig_df.copy()
    if selected_sig_type != "All":
        view_sig_df = view_sig_df[view_sig_df["signal_name"] == selected_sig_type]

    st.dataframe(
        view_sig_df[[
            "customer_id", "signal_name", "signal_strength", "segment",
            "behavioral_state", "evidence_metric_1", "evidence_metric_2",
            "explanation", "signal_limitation"
        ]],
        width='stretch'
    )

# ==============================================================================
# VIEW 5: CUSTOMER EXPLORER
# ==============================================================================
elif page == "5. Customer Explorer":
    st.title("Customer Diagnostic Explorer")
    st.markdown("Detailed behavioral audit card for any individual customer account.")

    cust_list = sorted(c_df["customer_id"].astype(str).unique().tolist())
    search_cid = st.selectbox("Select or Search Customer ID", cust_list, index=0)

    cust_row = c_df[c_df["customer_id"].astype(str) == str(search_cid)].iloc[0]
    cust_sigs = sig_df[sig_df["customer_id"].astype(str) == str(search_cid)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Segment", cust_row["segment_name"])
    c2.metric("Current State", cust_row["behavioral_state"])
    c3.metric("Lifetime Spend", f"£{cust_row['total_value']:,.2f}")
    c4.metric("Lifetime Orders", f"{cust_row['lifetime_orders']:,}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Recency", f"{cust_row['recency_days']} days")
    c6.metric("Average Order Value", f"£{cust_row['average_order_value']:,.2f}")
    c7.metric("Recent 90d Spend", f"£{cust_row['recent_90d_value']:,.2f}")
    c8.metric("Spend Momentum", f"{cust_row['value_momentum_pct']:+.1%}")

    st.subheader("Classification Audit")
    st.markdown(f"""
    <div class="callout-box">
        <strong>Classification Rationale for Account #{search_cid}:</strong><br>
        - <strong>Behavioral Segment</strong>: {cust_row['segment_name']} (based on log spend, order count, recency, SKU breadth, and momentum dimensions).<br>
        - <strong>Lifecycle State</strong>: {cust_row['behavioral_state']} (evaluated under deterministic precedence rules as of reference date).<br>
        - <strong>Primary Active Signal</strong>: {cust_row['primary_active_signal']}.
    </div>
    """, unsafe_allow_html=True)

    if not cust_sigs.empty:
        st.subheader("Active Decision Triggers")
        for _, s in cust_sigs.iterrows():
            st.markdown(f"""
            <div class="warning-box">
                <strong>Signal: {s['signal_name']} (Severity: {s['signal_strength']})</strong><br>
                <em>Evidence</em>: {s['evidence_metric_1']} | {s['evidence_metric_2']}<br>
                <em>Explanation</em>: {s['explanation']}<br>
                <em>Audit Limitation</em>: {s['signal_limitation']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No acute decision triggers currently active for this customer account.")

# ==============================================================================
# VIEW 6: METHODOLOGY & CONTROLS
# ==============================================================================
elif page == "6. Methodology & Controls":
    st.title("Methodology, Data Quality & Audit Controls")
    st.markdown("Complete lineage, systematic control evaluation, and boundary limitations.")

    st.subheader("Data Quality & Governance Control Layer")
    st.dataframe(
        ctrl_df[[
            "control_id", "control_name", "population_affected", "affected_pct",
            "severity", "status", "impact", "recommended_resolution"
        ]].style.map(
            lambda val: "background-color: #fee2e2; color: #991b1b;" if val == "FAIL"
            else ("background-color: #fef3c7; color: #92400e;" if val == "WARNING"
            else "background-color: #dcfce7; color: #166534;"),
            subset=["status"]
        ),
        width='stretch'
    )

    st.subheader("Analytical Lineage Architecture")
    st.markdown("""
    ```
    RAW WORKBOOK (online_retail_II.xlsx)
      │ (1,067,371 rows across Year 2009-2010 & Year 2010-2011)
      ▼
    DATA PROFILING & PRECEDENCE EVENT CLASSIFICATION
      │ (Class 1: Cancellation | Class 2: Reversal | Class 3: Valid Purchase | Class 4: Unusable)
      ▼
    DEDUPLICATION & STAGING LOADS (PostgreSQL: staging.raw_retail_transactions)
      │ (1,033,034 cleaned rows; 779,423 Class 3 Valid Purchases)
      ▼
    DIMENSIONS & FACTS (analytics.fact_order & fact_transaction)
      │ (36,969 validated orders; 5,878 distinct customer accounts)
      ▼
    5-DIMENSIONAL FEATURE ENGINEERING & RFM QUINTILES
      │ (Value, Activity, Breadth, Stability, Momentum; Reference Date: 2011-12-10)
      ▼
    K-MEANS BEHAVIORAL SEGMENTATION (K=3 chosen by 90% silhouette & >=5% share rule)
      │ (High-Value Stable | Emerging Engagement | Low-Activity / Long-Recency)
      ▼
    MONTHLY SNAPSHOTS & BEHAVIORAL LIFECYCLE STATES
      │ (Reactivated -> Emerging -> Dormant -> Softening -> Engaged)
      ▼
    DETERMINISTIC DECISION SIGNALS (6 Transparent Triggers) & STRATEGY CATALOG
    ```
    """)

    st.subheader("Locked Boundary Limitations")
    st.markdown("""
    1. **Retail vs Institutional Scope**: The dataset represents a commercial UK-based giftware retailer/wholesaler; findings cannot be generalized to consumer banking or credit card domains.
    2. **Wholesale Concentration**: Many accounts are commercial resellers, resulting in naturally lumpy, high-volume order intervals.
    3. **Observational Bounds**: No randomized marketing campaigns or promotional treatments are recorded; conclusions describe historical patterns without causal claims.
    4. **Psychology & Intent**: Segment membership reflects transactional history and does not represent customer sentiment, loyalty, or personal motivations.
    """)
