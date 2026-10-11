# Job Repost & Listing-Lifetime Tracker

A research pipeline for measuring **observed listing history** and identifying **likely reposts** among public Greenhouse and Lever job boards. It does not infer employer intent, fraud, or “ghost jobs”.

## Current status: Phase 1 — company discovery

The repository is being built phase-by-phase. Phase 1 is the feasibility gate; collection, matching, and dashboard code are intentionally not started. Run the discovery workflow below to generate verified board counts from live API responses. No live verification totals are claimed in this initial commit.

## Scope

- Cities: Pune, Hyderabad (including Secunderabad), Bengaluru, Delhi NCR, and Mumbai.
- Separate non-city buckets: `India - Remote/Other` and `Unclassified`.
- Allowed job sources only: Greenhouse public Job Board API and Lever public postings API.
- Tokens must come from documented public board URLs or manually edited seeds. At most three evidence-backed token candidates per company and a hard run-wide probe cap.
- No LinkedIn, Naukri, Indeed, Glassdoor, or other job-site scraping.

## Phase 1: discover and verify boards

Use Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

1. Edit `discovery/seeds.csv`. Each row must include a company, a source URL, and any token explicitly evidenced by that source. Do not guess tokens.
2. Review `discovery/search_queries.md` for manual public-web searches. Add candidates and their source URLs to the seed file; search-engine result pages are not scraped automatically.
3. Run `python -m discovery.discover --max-probes 60` (the cap is configurable, but never unlimited).
4. Inspect `data/boards.csv` and `reports/feasibility.md`. The report distinguishes verified zero-job boards from failed/incomplete probes. A failed probe is not a verified board.

The script makes requests at no more than one per second, uses bounded retries with backoff, checks each API host's robots.txt, and stops probing a host after HTTP 403 or 429. It records probe outcomes and source evidence so the run is auditable.

## Measurement language

`observed_duration = last_seen - first_seen`. These are the first and last times our collector observed a listing, not its true publish or close timestamps. Disappearance does not establish that a job was filled, fake, or intentionally left online.

## Interview preparation

Be ready to explain how a candidate becomes a verified board, why token evidence matters, why a zero-job response differs from a failed request, how location buckets are assigned, and why a feasibility gate should precede model development.

## Phase gates

- [x] Phase 1 scaffold and discovery workflow authored.
- [ ] Phase 1 live run and feasibility review.
- [ ] Phase 2 daily collector — requires explicit approval after Phase 1.
- [ ] Phase 3 labelled pairs and model evaluation — requires explicit approval after Phase 2.
- [ ] Phase 4 dashboard and deployment — requires explicit approval after Phase 3.
