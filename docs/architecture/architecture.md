# Architecture

FastAPI is the application boundary; SQLAlchemy persists the relational knowledge graph. Collectors implement `DataSourceAdapter`, produce normalized items, and the evidence service persists provenance. Jobs are represented by `ScanJob` with PENDING/RUNNING/COMPLETED/FAILED/CANCELLED states.

The demo uses deterministic fixtures, so CI is independent of external providers. PostgreSQL and Redis are provisioned in Compose; the local fallback is SQLite and synchronous execution.
