"""Three retrieval modes:
- naive:        no trimming (the bug we want to catch)
- post_filter:  retrieve top-k globally, then drop forbidden docs (safe, but loses recall)
- pre_filter:   security-trim the candidate set using the indexed ACL snapshot, then rank (recommended)
- live_check:   pre_filter + re-check each hit against the source ACL at query time (defends against stale sync)
"""
from .acl import principals, verify_obo
from .corpus import FOLDERS, GROUPS


def _allowed_snapshot(index, p):
    def f(did):
        acl, deny = index.acl[did]
        return not (p & deny) and bool(p & acl)
    return f

def retrieve(index, token: str, query: str, mode: str = "pre_filter", k: int = 3, groups=GROUPS, folders=FOLDERS):
    user = verify_obo(token)              # identity comes from the token, never from the request body
    p = principals(user, groups)
    if mode == "naive":
        return index.search(query, None, k)
    if mode == "post_filter":
        return [d for d in index.search(query, None, k) if _allowed_snapshot(index, p)(d)]
    hits = index.search(query, _allowed_snapshot(index, p), k)
    if mode == "live_check":
        from .acl import can_read
        hits = [d for d in hits if can_read(user, index.docs[d], groups, folders)]
    return hits

def answer(index, hits) -> str:
    """Extractive 'generator': returns the top passage text, or a refusal. Stands in for an LLM grounded only on hits."""
    return index.docs[hits[0]].text if hits else "I can't find that in documents you have access to."
