-- ============================================================================
-- Consumer Behavior Decision Intelligence Lab (CBDIL)
-- 00_database_setup.sql: Schemas, Extensions, and Core Permissions
-- ============================================================================

-- Create isolated schemas as defined in Part 8
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS reporting;

COMMENT ON SCHEMA staging IS 'Staging layer for raw and semi-cleaned transaction loads.';
COMMENT ON SCHEMA analytics IS 'Dimensional, fact, and customer behavioral modeling layer.';
COMMENT ON SCHEMA reporting IS 'Aggregated summary views and decision-support reporting layer.';
