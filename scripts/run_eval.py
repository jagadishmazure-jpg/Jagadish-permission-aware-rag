"""MEASURED on a SYNTHETIC corpus: leakage and recall per retrieval mode, plus a stale-ACL scenario."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from parag.acl import issue_obo
from parag.corpus import FOLDERS, build
from parag.evalset import cases
from parag.index import Index
from parag.retrieve import retrieve


def run(mode, idx, cs, folders=FOLDERS):
    leak = recall = neg = pos = 0
    for c in cs:
        hits = retrieve(idx, issue_obo(c["user"]), c["q"], mode, folders=folders)
        if c["should_see"]:
            pos += 1; recall += c["doc"] in hits
        else:
            neg += 1; leak += c["doc"] in hits
    return leak, neg, recall, pos

def main():
    idx, cs = Index(build()), cases()
    m, detail = {}, {}
    for mode in ["naive", "post_filter", "pre_filter", "live_check"]:
        leak, neg, rec, pos = run(mode, idx, cs)
        detail[mode] = {"leaks": leak, "should_not_see": neg, "recall_hits": rec, "should_see": pos}
        m[f"{mode}: leak rate"] = f"{leak}/{neg} ({leak / neg:.1%})"
        m[f"{mode}: recall@3"] = f"{rec}/{pos} ({rec / pos:.1%})"
    # stale ACL: engineering folder restricted to chen only AFTER the index synced
    changed = dict(FOLDERS); changed["drive:/eng"] = {"user:chen"}
    stale_cases = [c for c in cs if c["user"] == "dia" and c["doc"] in ("eng-1", "eng-2")]
    for mode in ["pre_filter", "live_check"]:
        leak = sum(c["doc"] in retrieve(idx, issue_obo(c["user"]), c["q"], mode, folders=changed) for c in stale_cases)
        m[f"stale ACL ({mode}): leaks"] = f"{leak}/{len(stale_cases)}"
    idx.sync_acls(changed)
    leak = sum(c["doc"] in retrieve(idx, issue_obo(c["user"]), c["q"], "pre_filter", folders=changed) for c in stale_cases)
    m["stale ACL after re-sync (pre_filter): leaks"] = f"{leak}/{len(stale_cases)}"
    out = {"label": "MEASURED on a SYNTHETIC corpus", "sample": f"16 docs, 9 users, {len(cs)} user-question cases",
           "metrics": m, "detail": detail}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "results.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(m, indent=2))

if __name__ == "__main__":
    main()
