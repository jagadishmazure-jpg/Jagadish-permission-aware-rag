# Interview points
- Security trimming must happen before ranking, otherwise top-k is consumed by docs the user can't see.
- ACL snapshots go stale; live re-check or event-driven sync for sensitive content.
- Identity flows as a delegated token; the retriever never accepts a user id parameter.
- Eval labels come from the ACL engine, so the leakage test is exact, not judged.
- Explicit deny and broken inheritance are where naive ACL mirrors go wrong.
