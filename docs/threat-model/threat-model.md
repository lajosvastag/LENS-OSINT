# Threat model

| Threat | Asset | Vector | Impact | Mitigation | Test |
|---|---|---|---|---|---|
| SSRF | worker/network | hostile URL | internal access | scope allowlist, DNS resolution, private/link-local/metadata blocks, timeout | `test_private_url_rejected` |
| Broken access control | tenant data | guessed IDs | disclosure | every query joins organization scope; RBAC | API isolation tests |
| Credential theft | auth | leaked password/token | account access | bcrypt, short-lived JWT, env secret, no password logs | login tests |
| API abuse | providers | uncontrolled collection | outage | adapters, rate/timeouts, background jobs | adapter tests |
| Malicious provider data | reports | injection in fields | misleading output | normalized values, factual language, escaping in UI | report tests |
| Privilege escalation | organization | role tampering | unauthorized scans | server-side RBAC | role tests |
| Secret leakage | repo/logs | committed key | compromise | `.env`, CI secret scanning policy | review |
| Worker compromise | jobs | provider payload | lateral movement | isolation, no shell execution, allowlisted HTTP | security tests |
| Report injection | CSV/UI | formula/script payload | client impact | escaping/rendering policy before export | report tests |
