"""BM25 index with an ACL snapshot stored per chunk (as a connector sync would)."""
import math
import re
from collections import Counter

from .acl import effective_acl

STOP = {"the", "a", "is", "of", "for", "what", "in", "and", "to", "was", "are", "with", "by", "on", "how", "many", "which", "who", "when", "does"}

def toks(t):
    return [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP]

class Index:
    def __init__(self, docs, folders=None):
        self.docs = {d.id: d for d in docs}
        self.sync_acls(folders)
        self.tf = {d.id: Counter(toks(d.text)) for d in docs}
        self.df = Counter(w for c in self.tf.values() for w in c)
        self.avg = sum(sum(c.values()) for c in self.tf.values()) / len(docs)

    def sync_acls(self, folders=None):
        """Snapshot ACLs at sync time. If source ACLs change and sync isn't rerun, the snapshot is stale."""
        from .corpus import FOLDERS
        f = folders or FOLDERS
        self.acl = {i: (effective_acl(d, f), set(d.deny)) for i, d in self.docs.items()}

    def score(self, q, did, k1=1.5, b=0.75):
        tf, n, L = self.tf[did], len(self.docs), sum(self.tf[did].values())
        s = 0.0
        for w in toks(q):
            if w in tf:
                idf = math.log(1 + (n - self.df[w] + 0.5) / (self.df[w] + 0.5))
                s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * L / self.avg))
        return s

    def search(self, q, allowed=None, k=3):
        ids = [i for i in self.docs if allowed is None or allowed(i)]
        scored = sorted(((self.score(q, i), i) for i in ids), reverse=True)
        return [i for s, i in scored[:k] if s > 0]
