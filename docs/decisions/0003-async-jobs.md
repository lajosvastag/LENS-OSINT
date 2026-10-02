# ADR 0003 — Celery boundary, deterministic demo execution

Celery is configured as the production boundary for long-running scans. The demo endpoint executes the same collection contract synchronously so local acceptance is deterministic without Redis or external APIs. A future scan service can enqueue the adapter orchestration without changing the domain model.
