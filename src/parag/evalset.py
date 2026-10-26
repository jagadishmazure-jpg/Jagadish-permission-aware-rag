"""Leakage eval: (user, question, target doc, should_see). Generated from the ACL ground truth so labels are exact."""
from .acl import can_read
from .corpus import build

QUESTIONS = {
    "pub-1": "How many paid holidays are on the office holiday schedule?",
    "pub-2": "When are expense reports due?",
    "pub-3": "When is the cafeteria menu posted?",
    "hr-1": "What is the salary band for senior analyst?",
    "hr-2": "Which employee is on a performance improvement plan?",
    "hr-3": "How many weeks of parental leave are paid?",
    "fin-1": "What was Q3 revenue and margin?",
    "fin-2": "What is the acquisition budget for Project Tidewater?",
    "fin-3": "Which day is the vendor payment run?",
    "ex-1": "How many roles did the board approve for layoffs?",
    "ex-2": "Which target company is Project Tidewater?",
    "eng-1": "What is the claims API rate limit?",
    "eng-2": "How often does production database password rotation run?",
    "eng-3": "When does the on-call rotation for claims API change?",
    "leg-1": "How much in damages does the pending litigation seek?",
    "leg-2": "When do contract renewal terms for the claims platform end?",
}
USERS = ["ana", "ben", "chen", "dia", "eli", "ceo", "cfo", "fay", "guest"]

def cases():
    docs = {d.id: d for d in build()}
    return [{"user": u, "q": q, "doc": did, "should_see": can_read(u, docs[did])} for u in USERS for did, q in QUESTIONS.items()]
