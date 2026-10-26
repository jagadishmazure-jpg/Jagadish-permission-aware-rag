# Threat model
| Threat | Control | Gap |
|---|---|---|
| Spoofed identity (S) | Signed, expiring OBO token | Lab HMAC key; use IdP-issued tokens |
| Sensitive info disclosure (OWASP LLM02) | Pre-filter trimming, deny-wins, refusal | Aggregation of allowed snippets |
| Stale permissions | `live_check`, re-sync | Group cache staleness not modelled |
| Vector/embedding weaknesses (LLM08) | ACL stored with every chunk | Embedding inversion not addressed |
| Prompt injection inside documents (LLM01) | Out of scope | See Jagadish-prompt-injection-evals |
