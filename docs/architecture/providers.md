# Provider adapters

All external providers implement `DataSourceAdapter` and return normalized `CollectedItem` objects. Provider payloads never cross into the domain model directly. Network adapters use bounded timeouts; active HTTP collection requires a `ScopeControl` and validates the resolved destination before the request.

- Certificate Transparency: public crt.sh JSON interface; names are observations only.
- RDAP: standards-based rdap.org redirect service; incomplete/404 records are handled as empty observations.
- HTTP metadata: one low-impact request, no crawling, redirects disabled, scope and SSRF validation required.
- Shodan: optional and returns `provider_unavailable` without an API key.
