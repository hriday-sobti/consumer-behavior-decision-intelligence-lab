# Data Directory Architecture

This directory preserves the data lifecycle of the Consumer Behavior Decision Intelligence Lab (CBDIL):

- `raw/`: Immutable source datasets downloaded directly from verified provenance archives (UCI Online Retail II). Files here are read-only and never modified in place.
- `interim/`: Intermediate parquet/staging caches generated during event classification and validation stages.
- `processed/`: Validated analytical datasets partitioned and optimized for PostgreSQL loading and dashboard ingestion.
