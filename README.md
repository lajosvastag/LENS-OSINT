# LENS — OSINT Asset Intelligence Platform

Plataforma defensiva de OSINT para inventário verificável de ativos digitais em escopos explicitamente autorizados. O projeto preserva a distinção entre **observação**, **inferência** e **candidato a vulnerabilidade**.

## Quick start

```bash
cp .env.example .env
docker compose up --build
# API: http://localhost:8000/docs
# UI:  http://localhost:3000
```

Sem Docker, backend local:

```bash
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Demo determinística: `POST /api/v1/demo/seed` cria organização, escopo e dados sintéticos sem APIs externas. Login demo: `admin@lens.local` / `ChangeMe123!` (altere em ambiente real).

## Fases entregues

- v0.1-v0.4: monorepo, Docker, API, modelos, auth/RBAC, ScopeControl e SSRF.
- v0.5-v0.7: adapters DNS/CT/RDAP/HTTP/Shodan opcional, evidências, deduplicação e jobs.
- v0.8-v1.0: UI dashboard/inventory/grafo/timeline, relatórios JSON/CSV, correlação explícita, CVE candidato.
- v1.1-v1.2: estrutura de alertas, hardening, threat model e CI/CD.

## Limitações deliberadas

A coleta ativa só é permitida para domínios no escopo e URLs aprovadas. O modo demo não acessa a internet. NVD/KEV/Shodan são adapters isolados e não são necessários para os testes. Nenhuma correspondência tecnológica afirma vulnerabilidade: o resultado é sempre candidato e carrega evidências/confiança.

## Rotas principais

- `POST /api/v1/demo/seed` — dataset sintético reproduzível.
- `POST /api/v1/auth/login` — JWT com RBAC.
- `GET /api/v1/assets`, `/graph`, `/timeline`, `/vulnerabilities` — inventário e inteligência.
- `GET /api/v1/reports/json`, `/csv`, `/pdf` — relatórios auditáveis.
- `POST /api/v1/security/validate-url` — validação de destino com ScopeControl/SSRF.
- Adapters isolados: DNS, CT, RDAP, HTTP metadata e Shodan opcional.
