"""Synthetic corpus for a fictional company (Harborline Mutual) with SharePoint-like and Drive-like ACLs.

ACL model: a document inherits its folder ACL unless it breaks inheritance. Principals are users or groups.
Explicit deny wins over allow."""
from dataclasses import dataclass, field


@dataclass
class Doc:
    id: str
    source: str           # "sp" (SharePoint-like) | "drive" (Drive-like)
    folder: str
    text: str
    own_acl: set[str] | None = None      # None = inherit folder ACL
    deny: set[str] = field(default_factory=set)

FOLDERS = {
    "sp:/public": {"group:all-staff"},
    "sp:/hr": {"group:hr"},
    "sp:/finance": {"group:finance"},
    "sp:/exec": {"user:ceo", "user:cfo"},
    "drive:/eng": {"group:engineering"},
    "drive:/legal": {"group:legal"},
}
GROUPS = {
    "group:all-staff": {"ana", "ben", "chen", "dia", "eli", "ceo", "cfo", "fay"},
    "group:hr": {"ana"},
    "group:finance": {"ben", "cfo"},
    "group:engineering": {"chen", "dia"},
    "group:legal": {"eli"},
}

def build() -> list[Doc]:
    d = [
        Doc("pub-1", "sp", "sp:/public", "The office holiday schedule lists twelve paid holidays in 2026."),
        Doc("pub-2", "sp", "sp:/public", "Expense reports are due by the fifth business day of each month."),
        Doc("pub-3", "sp", "sp:/public", "The cafeteria menu rotates weekly and is posted on Mondays."),
        Doc("hr-1", "sp", "sp:/hr", "Salary band for senior analyst is 98,000 to 121,000 per year."),
        Doc("hr-2", "sp", "sp:/hr", "Employee Fay is on a performance improvement plan until March."),
        Doc("hr-3", "sp", "sp:/hr", "Parental leave policy grants sixteen weeks of paid leave.", own_acl={"group:all-staff"}),
        Doc("fin-1", "sp", "sp:/finance", "Q3 revenue was 41.2 million with a margin of 18 percent."),
        Doc("fin-2", "sp", "sp:/finance", "The acquisition budget for Project Tidewater is 60 million."),
        Doc("fin-3", "sp", "sp:/finance", "Vendor payment run happens every Thursday.", deny={"user:ben"}),
        Doc("ex-1", "sp", "sp:/exec", "Board approved layoffs of 120 roles in the claims division."),
        Doc("ex-2", "sp", "sp:/exec", "Project Tidewater target company is a regional reinsurer."),
        Doc("eng-1", "drive", "drive:/eng", "The claims API rate limit is 300 requests per minute."),
        Doc("eng-2", "drive", "drive:/eng", "Production database password rotation runs every 30 days."),
        Doc("eng-3", "drive", "drive:/eng", "The on-call rotation for claims API changes every Tuesday.", own_acl={"group:engineering", "user:ana"}),
        Doc("leg-1", "drive", "drive:/legal", "Pending litigation with a former broker seeks 4 million in damages."),
        Doc("leg-2", "drive", "drive:/legal", "Contract renewal terms for the claims platform end in June."),
    ]
    # Restricted near-duplicates ("distractors") that outrank public docs for common questions.
    # They make post-filtering lose recall: the top-k is full of docs the user then cannot see.
    topics = ["office holiday schedule paid holidays", "expense reports due business day", "cafeteria menu posted",
              "parental leave paid weeks", "claims API rate limit requests"]
    for i, t in enumerate(topics):
        for j in range(3):
            d.append(Doc(f"dx-{i}-{j}", "sp", "sp:/exec", f"Draft {j}: exec revision of {t} {t} under review."))
    return d
