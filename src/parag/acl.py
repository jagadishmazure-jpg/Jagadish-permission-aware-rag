"""ACL resolution (inheritance, groups, explicit deny) and an on-behalf-of (OBO) style signed token."""
import base64, hashlib, hmac, json, time
from .corpus import FOLDERS, GROUPS

def principals(user: str, groups=GROUPS) -> set[str]:
    return {f"user:{user}"} | {g for g, members in groups.items() if user in members}

def effective_acl(doc, folders=FOLDERS) -> set[str]:
    return set(doc.own_acl) if doc.own_acl is not None else set(folders[doc.folder])

def can_read(user: str, doc, groups=GROUPS, folders=FOLDERS) -> bool:
    p = principals(user, groups)
    if p & doc.deny:
        return False
    return bool(p & effective_acl(doc, folders))

KEY = b"lab-only-signing-key"   # production: key vault / IdP-issued token

def issue_obo(user: str, ttl: int = 300, now=None) -> str:
    body = json.dumps({"sub": user, "exp": (time.time() if now is None else now) + ttl}).encode()
    sig = hmac.new(KEY, body, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(body).decode() + "." + sig

def verify_obo(token: str, now=None) -> str:
    b64, sig = token.rsplit(".", 1)
    body = base64.urlsafe_b64decode(b64)
    if not hmac.compare_digest(sig, hmac.new(KEY, body, hashlib.sha256).hexdigest()):
        raise PermissionError("bad signature")
    claims = json.loads(body)
    if claims["exp"] < (time.time() if now is None else now):
        raise PermissionError("token expired")
    return claims["sub"]
