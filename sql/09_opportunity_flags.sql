-- ============================================================================
-- 09_opportunity_flags.sql: Decision Signals and Strategy Catalog
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_decision_signal CASCADE;
DROP TABLE IF EXISTS analytics.decision_strategy CASCADE;

CREATE TABLE analytics.customer_decision_signal (
    signal_id BIGSERIAL PRIMARY KEY,
    signal_name VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    detected_date DATE NOT NULL,
    evidence_metric_1 VARCHAR(128) NOT NULL,
    evidence_metric_2 VARCHAR(128) NOT NULL,
    segment VARCHAR(128) NOT NULL,
    behavioral_state VARCHAR(32) NOT NULL,
    signal_strength VARCHAR(16) NOT NULL CHECK (signal_strength IN ('High', 'Medium', 'Low')),
    explanation TEXT NOT NULL,
    signal_limitation TEXT NOT NULL
);

CREATE INDEX idx_cds_signal_name ON analytics.customer_decision_signal(signal_name);
CREATE INDEX idx_cds_customer ON analytics.customer_decision_signal(customer_id);
CREATE INDEX idx_cds_strength ON analytics.customer_decision_signal(signal_strength);

CREATE TABLE analytics.decision_strategy (
    strategy_id VARCHAR(32) PRIMARY KEY,
    strategy_name VARCHAR(255) NOT NULL,
    target_signal VARCHAR(128) NOT NULL,
    behavioral_evidence TEXT NOT NULL,
    objective TEXT NOT NULL,
    possible_action_category VARCHAR(255) NOT NULL,
    primary_kpi VARCHAR(128) NOT NULL,
    secondary_kpi VARCHAR(128) NOT NULL,
    guardrail_metric VARCHAR(128) NOT NULL,
    eligibility_requirement TEXT NOT NULL,
    exclusion_rule TEXT NOT NULL,
    measurement_window VARCHAR(64) NOT NULL,
    status VARCHAR(64) NOT NULL
);
