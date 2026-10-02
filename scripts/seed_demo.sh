#!/usr/bin/env bash
set -euo pipefail
curl -fsS -X POST http://localhost:8000/api/v1/demo/seed
