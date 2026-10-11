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

16. Collect all roles from every verified Greenhouse/Lever board in the five city buckets plus India - Remote/Other and Unclassified. Never drop a listing because its role category is non-tech or unclear.
17. Role labels are deterministic and based only on title plus API-provided department/team fields. Never pass description/body text to the role classifier. Persist role_category and nullable is_tech: true for the seven tech/tech-adjacent categories, false for Non-Tech, null for Unclassified. Entry-level is a separate title-based flag, never a collection filter.
18. Tech-only analysis is a strict filter (is_tech = 1). The repost matcher, its candidate-labeling set, metrics, and dashboard must use tech-only records. Candidate pairs must be blocked within the same underlying company; do not let same-company pairs leak across train/test splits.
19. Non-Tech and Unclassified records must be counted in a separate "excluded from analysis" table while remaining in collection history. Public reports must be aggregate-only; human review CSVs containing titles stay local/ignored.
20. Store the raw SQLite database and dated snapshots only in the private data repository. The public repository may contain code, aggregate summaries, and city/category counts, but no raw database, titles, descriptions, job URLs, or per-company fetch errors.
21. Daily collector summaries must report attempted and successfully fetched boards, errors/incomplete fetches, new and vanished jobs, and active counts by role_category. Failed, blocked, schema-invalid, parsing-invalid, or incomplete snapshots must never mark jobs inactive.
