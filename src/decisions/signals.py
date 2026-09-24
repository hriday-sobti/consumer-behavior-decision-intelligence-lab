"""Rule-based decision signals and strategy catalog engine.

Implements all 6 specified deterministic signals:
  SIGNAL A: HIGH_VALUE_SOFTENING
    historical value >= 80th percentile AND value_momentum <= -25%
  SIGNAL B: HIGH_FREQUENCY_LOW_VALUE
    frequency >= 80th percentile AND average_order_value <= 40th percentile
  SIGNAL C: EMERGING_BROADENING
    customer state = EMERGING AND product breadth is increasing
  SIGNAL D: HISTORICAL_VALUE_DORMANT
    historical value >= 80th percentile AND state = DORMANT
  SIGNAL E: BROAD_ENGAGEMENT_SOFTENING
    product breadth >= 70th percentile AND frequency_momentum <= -25%
  SIGNAL F: POSITIVE_MOMENTUM
    value_momentum >= +25% AND frequency_momentum >= +25%

Severity categories: High, Medium, Low based on threshold distance.
"""

from datetime import date

import pandas as pd

from src.logging_config import logger


def build_decision_signals(
    features_df: pd.DataFrame,
    clustered_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    reference_date: date
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generates transparent rule-based decision signals with severity and attached limitations."""
    logger.info("Evaluating rule-based decision signals across customer base...")

    # Latest behavioral state per customer from snapshots
    latest_snapshot = snapshots_df.sort_values("year_month").groupby("customer_id").last().reset_index()
    state_map = latest_snapshot.set_index("customer_id")["behavioral_state"].to_dict()

    # Segment map
    segment_map = clustered_df.set_index("customer_id")["segment_name"].to_dict()

    # Base dataframe for evaluation
    df = features_df.copy()
    df["segment_name"] = df["customer_id"].map(segment_map).fillna("Unsegmented (Insufficient History)")
    df["current_state"] = df["customer_id"].map(state_map).fillna("UNKNOWN")

    # Quantile thresholds
    val_p80 = df["total_value"].quantile(0.80)
    freq_p80 = df["transaction_count"].quantile(0.80)
    aov_p40 = df["average_order_value"].quantile(0.40)
    breadth_p70 = df["product_count"].quantile(0.70)

    logger.info(f"Signal Evaluation Thresholds: Value P80={val_p80:.2f}, Freq P80={freq_p80:.1f}, AOV P40={aov_p40:.2f}, Breadth P70={breadth_p70:.1f}")

    signal_records = []

    for _, row in df.iterrows():
        cid = row["customer_id"]
        seg = row["segment_name"]
        st = row["current_state"]
        tot_val = row["total_value"]
        tx_cnt = row["transaction_count"]
        aov = row["average_order_value"]
        p_cnt = row["product_count"]
        val_mom = row["value_change_pct"]
        freq_mom = row["frequency_change_pct"]
        breadth_mom = row["product_breadth_change_pct"]
        insufficient = row["insufficient_history"]

        # Limitation flag helper
        def get_limitation(extra_risk="", is_inelig=insufficient, rev_r=row["reversal_rate"], p90=row["prior_90d_value"]):
            risks = []
            if is_inelig:
                risks.append("Customer has insufficient longitudinal history (<2 orders or <90 days tenure).")
            if rev_r > 0.10:
                risks.append("Elevated customer reversal/return rate (>10% of total spend).")
            if p90 == 0:
                risks.append("Zero baseline in prior 90-day comparison window.")
            if extra_risk:
                risks.append(extra_risk)
            return " | ".join(risks) if risks else "Standard observational limitations apply; transactional patterns do not guarantee customer response."

        # SIGNAL A: HIGH_VALUE_SOFTENING
        # historical value >= 80th percentile AND value_momentum <= -25%
        if tot_val >= val_p80 and val_mom <= -0.25:
            # Severity based on drop distance: <= -45% -> High, -35% to -45% -> Medium, -25% to -35% -> Low
            if val_mom <= -0.45:
                sev = "High"
            elif val_mom <= -0.35:
                sev = "Medium"
            else:
                sev = "Low"
            
            signal_records.append({
                "signal_name": "HIGH_VALUE_SOFTENING",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"Historical Value: {tot_val:,.2f} (>= P80: {val_p80:,.2f})",
                "evidence_metric_2": f"Value Momentum: {val_mom*100:.1f}% (<= -25.0%)",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Customer is in the top spend quintile (spend {tot_val:,.2f}) but experienced a {val_mom*100:.1f}% contraction in recent 90-day spend.",
                "signal_limitation": get_limitation("Contraction could be caused by lumpy wholesale purchase cycles.")
            })

        # SIGNAL B: HIGH_FREQUENCY_LOW_VALUE
        # frequency >= 80th percentile AND average_order_value <= 40th percentile
        if tx_cnt >= freq_p80 and aov <= aov_p40:
            # Severity based on how deep AOV is below P40
            aov_ratio = aov / aov_p40 if aov_p40 > 0 else 1.0
            if aov_ratio <= 0.60:
                sev = "High"
            elif aov_ratio <= 0.80:
                sev = "Medium"
            else:
                sev = "Low"

            signal_records.append({
                "signal_name": "HIGH_FREQUENCY_LOW_VALUE",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"Order Frequency: {tx_cnt} orders (>= P80: {freq_p80:.0f})",
                "evidence_metric_2": f"AOV: {aov:,.2f} (<= P40: {aov_p40:,.2f})",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Highly frequent ordering behavior ({tx_cnt} lifetime orders) paired with modest average basket value ({aov:,.2f}).",
                "signal_limitation": get_limitation("Fulfillment overhead per order may erode margin without minimum basket thresholds.")
            })

        # SIGNAL C: EMERGING_BROADENING
        # customer state = EMERGING AND product breadth is increasing
        if st == "EMERGING" and breadth_mom > 0:
            if breadth_mom >= 0.50:
                sev = "High"
            elif breadth_mom >= 0.20:
                sev = "Medium"
            else:
                sev = "Low"

            signal_records.append({
                "signal_name": "EMERGING_BROADENING",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"State: EMERGING (Tenure: {row['customer_lifetime_days']} days)",
                "evidence_metric_2": f"Breadth Growth: +{breadth_mom*100:.1f}% unique SKUs",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Recently acquired customer is expanding across product categories (+{breadth_mom*100:.1f}% breadth in recent window).",
                "signal_limitation": get_limitation("Early purchasing breadth may reflect initial sample exploration rather than recurring catalog demand.")
            })

        # SIGNAL D: HISTORICAL_VALUE_DORMANT
        # historical value >= 80th percentile AND state = DORMANT
        if tot_val >= val_p80 and st == "DORMANT":
            # Severity based on recency days past 120
            rec = row["recency_days"]
            if rec >= 240:
                sev = "High"
            elif rec >= 180:
                sev = "Medium"
            else:
                sev = "Low"

            signal_records.append({
                "signal_name": "HISTORICAL_VALUE_DORMANT",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"Historical Value: {tot_val:,.2f} (>= P80: {val_p80:,.2f})",
                "evidence_metric_2": f"Inactivity: {rec} days since last purchase (> 120d)",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Tier-1 historical customer ({tot_val:,.2f} total spend) has lapsed into dormancy with {rec} days of elapsed inactivity.",
                "signal_limitation": get_limitation("Wholesaler may have discontinued lines or shifted supplier accounts entirely.")
            })

        # SIGNAL E: BROAD_ENGAGEMENT_SOFTENING
        # product breadth >= 70th percentile AND frequency_momentum <= -25%
        if p_cnt >= breadth_p70 and freq_mom <= -0.25:
            if freq_mom <= -0.45:
                sev = "High"
            elif freq_mom <= -0.35:
                sev = "Medium"
            else:
                sev = "Low"

            signal_records.append({
                "signal_name": "BROAD_ENGAGEMENT_SOFTENING",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"Catalog Breadth: {p_cnt} SKUs (>= P70: {breadth_p70:.0f})",
                "evidence_metric_2": f"Frequency Momentum: {freq_mom*100:.1f}% (<= -25.0%)",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Customer historically active across broad catalog ({p_cnt} SKUs) shows declining order cadence ({freq_mom*100:.1f}% recent order momentum).",
                "signal_limitation": get_limitation("May reflect consolidated bulk shipments rather than loss of underlying SKU demand.")
            })

        # SIGNAL F: POSITIVE_MOMENTUM
        # value_momentum >= +25% AND frequency_momentum >= +25%
        if val_mom >= 0.25 and freq_mom >= 0.25:
            if val_mom >= 0.50 and freq_mom >= 0.50:
                sev = "High"
            elif val_mom >= 0.35 and freq_mom >= 0.35:
                sev = "Medium"
            else:
                sev = "Low"

            signal_records.append({
                "signal_name": "POSITIVE_MOMENTUM",
                "customer_id": cid,
                "detected_date": reference_date,
                "evidence_metric_1": f"Spend Momentum: +{val_mom*100:.1f}% (>= +25.0%)",
                "evidence_metric_2": f"Order Momentum: +{freq_mom*100:.1f}% (>= +25.0%)",
                "segment": seg,
                "behavioral_state": st,
                "signal_strength": sev,
                "explanation": f"Customer shows synchronized double-digit expansion across recent 90d spend (+{val_mom*100:.1f}%) and order volume (+{freq_mom*100:.1f}%).",
                "signal_limitation": get_limitation("Short-term seasonal order spikes can temporarily inflate momentum percentages.")
            })

    signals_df = pd.DataFrame(signal_records)
    signals_df["signal_id"] = range(1, len(signals_df) + 1)
    
    # Reorder columns
    col_order = [
        "signal_id", "signal_name", "customer_id", "detected_date",
        "evidence_metric_1", "evidence_metric_2", "segment",
        "behavioral_state", "signal_strength", "explanation", "signal_limitation"
    ]
    signals_df = signals_df[col_order]

    logger.info(f"Generated {len(signals_df):,} total decision signal triggers across the customer base.")
    for s_name, cnt in signals_df["signal_name"].value_counts().items():
        logger.info(f"  - {s_name}: {cnt:,} accounts")

    # Decision Strategy Catalog
    strategies = [
        {
            "strategy_id": "STRAT-01",
            "strategy_name": "High-Value Account Outreach & Service Audit",
            "target_signal": "HIGH_VALUE_SOFTENING",
            "behavioral_evidence": "Top 20% historical spend tier accounts showing >= 25% drop in recent 90d transaction value.",
            "objective": "Investigate root causes of spend contraction among top-tier accounts to evaluate account retention viability.",
            "possible_action_category": "Direct Account Management Contact / Service Review",
            "primary_kpi": "90-day value recovery percentage",
            "secondary_kpi": "Order cadence stabilization rate",
            "guardrail_metric": "Return and reversal rate on subsequent orders",
            "eligibility_requirement": "Customer lifetime spend >= P80 with at least 2 historical orders.",
            "exclusion_rule": "Accounts with ongoing unresolved customer service claims or > 20% reversal rate.",
            "measurement_window": "90 Days post-contact",
            "status": "APPROVED_FOR_INVESTIGATION"
        },
        {
            "strategy_id": "STRAT-02",
            "strategy_name": "Basket Expansion & Minimum Tier Incentives",
            "target_signal": "HIGH_FREQUENCY_LOW_VALUE",
            "behavioral_evidence": "Frequent repeat order placement (>= P80 frequency) with depressed basket sizes (<= P40 AOV).",
            "objective": "Test order-consolidation thresholds or category bundling to improve gross margin per shipment.",
            "possible_action_category": "Tiered Volume Pricing / Minimum Order Incentive",
            "primary_kpi": "Average Order Value (AOV)",
            "secondary_kpi": "Gross transaction value per shipment",
            "guardrail_metric": "Overall order frequency (ensure order counts do not decline faster than value rises)",
            "eligibility_requirement": ">= 80th percentile order count and <= 40th percentile AOV.",
            "exclusion_rule": "Customers in single-item specialty parts categories with rigid replenishment needs.",
            "measurement_window": "60 Days post-launch",
            "status": "APPROVED_FOR_INVESTIGATION"
        },
        {
            "strategy_id": "STRAT-03",
            "strategy_name": "Onboarding Cross-Category Nurturing",
            "target_signal": "EMERGING_BROADENING",
            "behavioral_evidence": "Recently acquired customers (< 90 days tenure) who actively expand their SKU breadth.",
            "objective": "Accelerate cross-category familiarity during peak exploration window to establish recurring multi-category baskets.",
            "possible_action_category": "Targeted Catalog Sample Bundles / Cross-Selling Recommendations",
            "primary_kpi": "Repeat purchase rate within 60 days",
            "secondary_kpi": "Catalog breadth (distinct categories purchased)",
            "guardrail_metric": "Customer unsubscribes or return rates on sampled products",
            "eligibility_requirement": "Tenure <= 90 days with positive product breadth momentum.",
            "exclusion_rule": "Accounts with single unverified guest transactions.",
            "measurement_window": "60 Days post-onboarding",
            "status": "APPROVED_FOR_INVESTIGATION"
        },
        {
            "strategy_id": "STRAT-04",
            "strategy_name": "Tier-1 Dormancy Reactivation Campaign",
            "target_signal": "HISTORICAL_VALUE_DORMANT",
            "behavioral_evidence": "Accounts in top 20% lifetime spend with > 120 days since last purchase.",
            "objective": "Evaluate whether dormant high-value wholesale accounts can be re-engaged with updated seasonal catalogs.",
            "possible_action_category": "Dedicated Re-Engagement Offer / Account Manager Follow-Up",
            "primary_kpi": "Account reactivation rate (order placed within 60 days)",
            "secondary_kpi": "Incremental 90-day order value",
            "guardrail_metric": "Discount margin erosion / high-cost low-spend redemption",
            "eligibility_requirement": "Historical spend >= P80, inactivity > 120 days.",
            "exclusion_rule": "Accounts known to have ceased commercial operations.",
            "measurement_window": "60 Days post-outreach",
            "status": "APPROVED_FOR_INVESTIGATION"
        },
        {
            "strategy_id": "STRAT-05",
            "strategy_name": "Broad Catalog Engagement Retention",
            "target_signal": "BROAD_ENGAGEMENT_SOFTENING",
            "behavioral_evidence": "Catalog breadth >= 70th percentile with >= 25% decline in recent order frequency.",
            "objective": "Determine whether category churn or stock availability issues are depressing reorder frequency.",
            "possible_action_category": "Inventory Availability Notification / Replenishment Check",
            "primary_kpi": "Order frequency recovery",
            "secondary_kpi": "Active category retention rate",
            "guardrail_metric": "Cancellation rate on backordered SKUs",
            "eligibility_requirement": "Historical product count >= P70 and frequency momentum <= -25%.",
            "exclusion_rule": "Seasonal holiday-only catalog buyers outside peak season.",
            "measurement_window": "90 Days post-audit",
            "status": "APPROVED_FOR_INVESTIGATION"
        },
        {
            "strategy_id": "STRAT-06",
            "strategy_name": "High-Momentum VIP Capacity & Fulfillment Protection",
            "target_signal": "POSITIVE_MOMENTUM",
            "behavioral_evidence": "Synchronized growth: >= +25% in value momentum and >= +25% in frequency momentum.",
            "objective": "Ensure supply chain, inventory allocation, and fulfillment SLA stability for rapidly growing commercial buyers.",
            "possible_action_category": "Priority Inventory Allocation / Dedicated Support Desk",
            "primary_kpi": "Order fulfillment rate without backorders",
            "secondary_kpi": "Subsequent 90-day retention and spend continuity",
            "guardrail_metric": "Delivery delay rate and customer complaint incidents",
            "eligibility_requirement": "Value momentum >= +25% and frequency momentum >= +25%.",
            "exclusion_rule": "None; all high-momentum accounts receive fulfillment protection.",
            "measurement_window": "Ongoing quarterly monitoring",
            "status": "APPROVED_FOR_MONITORING"
        }
    ]
    strategies_df = pd.DataFrame(strategies)

    return signals_df, strategies_df
