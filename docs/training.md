# Training module: permission-aware retrieval
**Audience:** AI engineers, half a day to one day.
## Learning objectives
1. Explain why post-filtering is safe but hurts recall, and why pre-filtering is preferred.
2. Model inheritance, groups and explicit deny correctly.
3. Pass identity via OBO token, never via request body.
4. Generate a leakage eval from ACL ground truth and gate on zero leaks.
5. Detect and mitigate stale ACL snapshots.
## Labs
| # | Lab | Done when |
|---|---|---|
| 1 | Run `run_eval.py`; explain each mode's numbers | Can explain why post_filter recall drops |
| 2 | Add a sharing link ("anyone in org with link") | New ACL rule + tests |
| 3 | Add a nested group (group in group) | `principals` resolves transitively, tests pass |
| 4 | Make the stale-ACL test pass in `pre_filter` by adding an ACL change event | Event handler re-syncs one doc |
| 5 | Add 10 more distractors; observe recall | Numbers regenerated in README |
## Capstone
Replace BM25 with a small local vector index that supports metadata filters, keep 0 leaks across all tests, and report recall@3 for pre_filter vs post_filter with the README regenerated.
