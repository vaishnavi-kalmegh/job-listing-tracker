# Engineering Rules — Read at the Start of Every Phase

These rules are binding. Re-read this file before starting any phase.

1. Describe outputs only as **likely reposts**, **suspected matches**, and **observed duration**. Never claim to detect ghost jobs, fraud, or employer intent.
2. Use the exact metric name `observed_duration` for `last_seen - first_seen`. True publication and closure dates are unknown.
3. Use only Greenhouse's public Job Board API (`https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`) and Lever's public postings API (`https://api.lever.co/v0/postings/{company}?mode=json`) for job data. Do not scrape LinkedIn, Naukri, Indeed, Glassdoor, or sites whose terms forbid automated access.
4. Identify the client with a User-Agent that includes this repository URL. No more than one request per second. Retry transient errors with bounded exponential backoff. On HTTP 403 or 429, stop requests to that host for the rest of the run.
5. Never invent metrics. Any published number must come from real data and a reproducible repository script.
6. No LLM APIs, survival models, or scam classifiers.
7. Work one phase at a time. Stop after each phase, report results plainly, and wait for user approval before beginning the next phase.
8. Phase 1 token discovery must use documented public board URLs and editable seeds. Try at most 2–3 evidence-backed token candidates per company and enforce a run-wide probe cap. Never brute-force tokens. A valid API response with zero jobs is still a verified board.
9. Never infer a listing vanished from a failed or incomplete collection. Mark inactive only after a successful, complete fetch confirms absence. Distinguish timeouts, HTTP failures, pagination incompleteness, and parsing failures.
10. Prevent evaluation leakage: split by underlying vacancy groups, use a fixed seed, document class counts, and never tune on the held-out test set. If positive test examples are too few, report evaluation as inconclusive.
11. Public availability does not imply redistribution permission. Do not commit full descriptions or raw snapshots to this public repository unless redistribution is explicitly permitted. Keep raw data private and publish derived/aggregate data only.
12. Preserve timestamped observations; support disappearance and later return; define `observed_duration` as an observed interval, not true vacancy lifetime.
13. Validate API response schemas and pagination/completeness. Preserve records that cannot be normalized in an `Unclassified` bucket; never silently discard them.
14. Normalize city buckets exactly as documented in `discovery/locations.py`.
15. Compliance findings and unresolved legal/terms questions must be explicit in `docs/compliance.md`. Do not equate robots.txt permission with legal permission.
