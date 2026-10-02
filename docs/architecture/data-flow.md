# Data flow

1. User creates an authorized Scope.
2. ScopeControl normalizes the domain and gates active HTTP.
3. An adapter collects public observations.
4. Items are normalized/deduplicated by `(scope, kind, value)` while evidence rows remain append-only.
5. Correlation creates typed relationships with confidence/source/timestamp.
6. Reports expose observations and candidates with limitations.
