# ADR 0002: Live permission check for sensitive sources
Status: accepted. Context: snapshot ACLs leak after a permission change until re-sync (reproduced in tests). Decision: `live_check` mode for HR, legal and exec sources; accepted cost is one permission lookup per hit.
