# ADR 0001 — PostgreSQL relationships before Neo4j

**Decision:** store graph nodes as assets and edges as relationships in PostgreSQL.

**Reason:** the MVP needs auditability, transactions and a small graph. Neo4j adds operational surface without a demonstrated need.
