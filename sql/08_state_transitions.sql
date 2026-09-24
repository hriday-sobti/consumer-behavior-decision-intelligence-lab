-- ============================================================================
-- 08_state_transitions.sql: State Transition Aggregates & History
-- ============================================================================

DROP TABLE IF EXISTS analytics.customer_state_history CASCADE;
DROP TABLE IF EXISTS analytics.state_transition_matrix CASCADE;

CREATE TABLE analytics.customer_state_history (
    transition_id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    previous_month VARCHAR(7) NOT NULL,
    current_month VARCHAR(7) NOT NULL,
    previous_state VARCHAR(32) NOT NULL,
    current_state VARCHAR(32) NOT NULL,
    is_state_changed BOOLEAN NOT NULL
);

CREATE INDEX idx_csh_customer ON analytics.customer_state_history(customer_id);
CREATE INDEX idx_csh_months ON analytics.customer_state_history(previous_month, current_month);

CREATE TABLE analytics.state_transition_matrix (
    previous_month VARCHAR(7) NOT NULL,
    current_month VARCHAR(7) NOT NULL,
    previous_state VARCHAR(32) NOT NULL,
    current_state VARCHAR(32) NOT NULL,
    customer_count INTEGER NOT NULL,
    customer_share NUMERIC(6, 4) NOT NULL,
    PRIMARY KEY (previous_month, current_month, previous_state, current_state)
);
