# Data policy

This repository is public. Do not commit full job descriptions, raw API responses, or raw daily snapshots unless redistribution permission is explicitly established.

## Phase 1
- Commit board metadata and aggregate counts only: platform, token, company name, evidence/source URL, total jobs, city counts, entry-level estimate, and verification timestamp.
- Keep the local discovery run log out of Git.
- Job descriptions may be fetched temporarily in memory to estimate entry-level relevance, but must not be written to public artifacts.

## Later phases (not implemented yet)
- Store raw payloads and full descriptions only in a private local location or private storage with access controls.
- Publish derived features, aggregate counts, and appropriately minimized labelled examples only after reviewing redistribution rights. Pair-labeling exports should use short snippets only if policy permits; otherwise use locally generated private exports and publish no raw text.
- Document retention periods, deletion, backups, and access control before enabling scheduled collection.
- Do not commit the SQLite database, raw snapshots, or description-bearing exports to this public repository.
- Public GitHub Actions workflows must not write descriptions or raw snapshots to repository history. Any later automation should publish only derived/aggregate data and must not expose secrets.

No automated collection is active in Phase 1. No data is currently being collected on a schedule.
