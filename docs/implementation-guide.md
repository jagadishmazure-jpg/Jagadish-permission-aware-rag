# Implementation guide
1. **Inventory sources and their ACL models** (inheritance, groups, deny, sharing links). Write them as `can_read` rules with tests before indexing anything.
2. **Index ACLs with content.** Store allowed principals per chunk as a filterable field (e.g. a `group_ids` collection field in Azure AI Search, metadata filters in other vector stores).
3. **Filter in the query, not after.** Pass the user's principals as a filter so ranking only sees permitted chunks.
4. **Use delegated identity.** The app exchanges the user's token (OBO); never trust a user id from the request body.
5. **Keep ACLs fresh.** Subscribe to change notifications; for high-sensitivity sources add a live permission check on the final hits.
6. **Build the leakage eval from ACL truth.** Cross users × questions; gate CI on 0 leaks.
7. **Watch aggregation.** Review answers that combine many low-sensitivity snippets.
