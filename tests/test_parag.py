import pytest

from parag.acl import can_read, effective_acl, issue_obo, principals, verify_obo
from parag.corpus import FOLDERS, build
from parag.evalset import USERS, cases
from parag.index import Index
from parag.retrieve import answer, retrieve

DOCS = {d.id: d for d in build()}

@pytest.fixture(scope="module")
def idx():
    return Index(build())

# --- ACL semantics
def test_principals_include_groups():
    assert "group:hr" in principals("ana") and "user:ana" in principals("ana")

def test_inherit_folder_acl():
    assert effective_acl(DOCS["hr-1"]) == {"group:hr"}

def test_broken_inheritance():
    assert can_read("ben", DOCS["hr-3"]) and not can_read("ben", DOCS["hr-1"])

def test_explicit_deny_wins():
    assert can_read("cfo", DOCS["fin-3"]) and not can_read("ben", DOCS["fin-3"])

def test_user_level_grant():
    assert can_read("ana", DOCS["eng-3"]) and not can_read("ana", DOCS["eng-1"])

def test_unknown_user_sees_nothing():
    assert not any(can_read("guest", d) for d in DOCS.values())

# --- OBO token
def test_obo_roundtrip():
    assert verify_obo(issue_obo("ana")) == "ana"

def test_obo_tampered():
    t = issue_obo("ana"); body, sig = t.rsplit(".", 1)
    with pytest.raises(PermissionError):
        verify_obo(body + "." + "0" * len(sig))

def test_obo_expired():
    with pytest.raises(PermissionError):
        verify_obo(issue_obo("ana", ttl=1, now=0), now=10)

# --- retrieval
@pytest.mark.parametrize("mode", ["post_filter", "pre_filter", "live_check"])
@pytest.mark.parametrize("user", USERS)
def test_no_leaks_for_safe_modes(idx, mode, user):
    for c in [c for c in cases() if c["user"] == user]:
        hits = retrieve(idx, issue_obo(user), c["q"], mode)
        assert all(can_read(user, DOCS[h]) for h in hits), (mode, c)

def test_naive_mode_leaks(idx):
    """Known-bad baseline kept visible: naive retrieval leaks HR data to engineering."""
    hits = retrieve(idx, issue_obo("chen"), "What is the salary band for senior analyst?", "naive")
    assert "hr-1" in hits

def test_pre_filter_beats_post_filter_recall(idx):
    q = "How many paid holidays are on the office holiday schedule?"
    assert "pub-1" in retrieve(idx, issue_obo("dia"), q, "pre_filter")
    assert "pub-1" not in retrieve(idx, issue_obo("dia"), q, "post_filter")

def test_refusal_when_nothing_visible(idx):
    hits = retrieve(idx, issue_obo("guest"), "What was Q3 revenue and margin?", "pre_filter")
    assert hits == [] and "can't find" in answer(idx, hits)

def test_answer_grounded_in_visible_doc(idx):
    hits = retrieve(idx, issue_obo("ben"), "What was Q3 revenue and margin?", "pre_filter")
    assert "41.2" in answer(idx, hits)

def test_stale_acl_leaks_until_resync():
    i = Index(build()); changed = dict(FOLDERS); changed["drive:/eng"] = {"user:chen"}
    q = "What is the claims API rate limit?"
    assert "eng-1" in retrieve(i, issue_obo("dia"), q, "pre_filter", folders=changed)       # known failure
    assert "eng-1" not in retrieve(i, issue_obo("dia"), q, "live_check", folders=changed)   # defended
    i.sync_acls(changed)
    assert "eng-1" not in retrieve(i, issue_obo("dia"), q, "pre_filter", folders=changed)

def test_identity_from_token_only(idx):
    with pytest.raises(PermissionError, match="malformed token"):
        retrieve(idx, "not-a-token", "anything")

def test_eval_set_has_both_labels():
    cs = cases()
    assert any(c["should_see"] for c in cs) and any(not c["should_see"] for c in cs) and len(cs) == 144
