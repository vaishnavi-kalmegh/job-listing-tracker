# Job Repost & Listing-Lifetime Tracker

A research pipeline for measuring **observed listing history** and identifying **likely reposts** among public Greenhouse and Lever job boards. It does not infer employer intent, fraud, or “ghost jobs”.

## Current status: Phase 2 — collector scaffold and daily workflow

Phase 1 passed with the owner-reported baseline of 32 verified boards and 507 jobs across the five city buckets. The collector now stores all role categories, adds title-only role labels, writes aggregate daily summaries, and has a daily/manual GitHub Actions workflow. Live collector verification and automated test results remain pending until the private data repository and Actions secret are configured and the workflow is run.

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

## Tech role labels and analysis scope

The collector classifies titles plus available department/team metadata into Software Engineering, Data/ML/AI, DevOps/Cloud/SRE/Infra, QA/Test, Security, IT Support/Systems, Product/Design (tech-adjacent), Non-Tech, or Unclassified. Descriptions are not inputs to role classification. All roles remain in the collection database; tech-only analysis filters to is_tech = 1. Non-Tech and Unclassified jobs are counted separately as excluded from analysis. Entry-level is a separate flag, never a collection filter.

Run the title review sample locally after a successful collector run:

```bash
python -m discovery.sample_role_review
```

Fill reports/role_review.csv with tech, non-tech, or unclassified in review_label, then run:

```bash
python -m discovery.score_role_review
```

The sample is gitignored and should not be committed publicly. No precision is reported until human labels exist.

## Private storage and daily workflow

Follow [the private data repository setup guide](docs/private_data_setup.md) to create the private job-listing-data repository and add the DATA_REPO_TOKEN secret. Then run **Actions → Daily job collection → Run workflow** once. The workflow schedules daily collection at 02:00 IST, stores SQLite snapshots in the private repository, and commits only aggregate reports to this public repository.

## Measurement language

`observed_duration = last_seen - first_seen`. These are the first and last times our collector observed a listing, not its true publish or close timestamps. Disappearance does not establish that a job was filled, fake, or intentionally left online.

## Interview preparation

Be ready to explain how a candidate becomes a verified board, why token evidence matters, why a zero-job response differs from a failed request, how location buckets are assigned, and why a feasibility gate should precede model development.

## Phase gates

- [x] Phase 1 scaffold and discovery workflow authored.
- [x] Phase 1 feasibility review (owner-reported: 32 verified boards, 507 five-city jobs).
- [x] Phase 2 collector scaffold, title-only role labels, robots enforcement, tests authored, and daily/manual workflow authored.
- [ ] Phase 2 live API run, automated test results, and private-repository push — pending user setup and workflow execution.
- [ ] Phase 3 tech-only repost matching, same-company pair blocking, and evaluation — wait for explicit approval after Phase 2 verification.
- [ ] Phase 4 tech-only dashboard and deployment — wait for explicit approval after Phase 3.
