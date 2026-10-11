# Source and access compliance

**Status: preliminary desk review, not legal advice. Re-check these sources before each collection release.** This document records what was checked and what remains unresolved; it does not assert blanket permission to republish collected data.

## Allowed endpoints in this project

- Greenhouse public Job Board API: [official Job Board API documentation](https://docs.greenhouse.io/job-board.html). Greenhouse documents public GET access to published job-board data without authentication. This project uses only GET requests to the public job-list endpoint.
- Lever public postings API: [official Lever Postings API documentation](https://github.com/lever/postings-api). Lever documents published postings as publicly viewable through its postings API. This project uses only GET requests to the public postings endpoint.

Publicly readable API data is not automatically licensed for bulk redistribution. The project's public repository must not contain full descriptions or raw snapshots. Store sensitive-to-redistribution source payloads locally/private; commit only source references, counts, and other derived aggregates unless permission is verified.

## Robots.txt and terms review

The discovery script checks `https://boards-api.greenhouse.io/robots.txt` and `https://api.lever.co/robots.txt` before probing the respective API hosts, and logs the outcome. A robots.txt file is a crawl preference signal, not a substitute for contractual terms or legal review. If robots.txt is unavailable or ambiguous, treat the status as unresolved and inspect the platform's current terms before expanding collection.

- Greenhouse: API documentation confirms public GET endpoints, but this is not itself a blanket data-reuse license. Review the current [Greenhouse terms](https://www.greenhouse.com/terms-of-service) and any applicable API-specific terms before public redistribution.
- Lever: API documentation describes public postings and the intended job-site use. Review current [Lever terms](https://www.lever.co/terms) and any applicable API-specific terms before public redistribution.
- Automated access restrictions for other job sites are out of scope; do not scrape them.

## Politeness controls

- User-Agent identifies the project and includes `https://github.com/vaishnavi-kalmegh/job-listing-tracker`.
- Global request spacing is at least one second between requests.
- Transient failures use bounded exponential backoff.
- HTTP 403 or 429 permanently pauses requests to that API host for the remainder of the run.
- Probe count is capped, and each candidate has at most three evidence-backed token candidates.
- No guessed token enumeration.

## Evidence log

A discovery run writes `reports/discovery_run.json` locally. It records timestamps, source URLs, endpoint outcomes, HTTP status/error categories, robots.txt observations, and parser status. This file is intentionally ignored by Git because it may contain run-level details; summarize relevant findings in `reports/feasibility.md` without copying raw job content.

## Remaining checks before recurring collection

1. Re-check the current platform terms and any API-specific reuse restrictions.
2. Confirm robots.txt responses and interpret relevant disallow rules for the API paths.
3. Confirm retention and deletion practices for private raw payloads.
4. Obtain legal/platform clarification if reuse or public display of derived information is uncertain.
