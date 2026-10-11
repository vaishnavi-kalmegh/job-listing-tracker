# Phase 1 feasibility report

**Status: NOT YET MEASURED — live discovery has not been run from this repository environment.**

No board verification totals or job-volume metrics are claimed in this initial report. The checked-in `data/boards.csv` currently contains only its header, so it is not evidence that zero boards exist; it means no live verification run has populated the file yet.

Run:

```bash
python -m pip install -r requirements.txt
python -m discovery.discover --max-probes 60
```

Then regenerate this report from the saved local run output:

```bash
python -m discovery.report
```

## Required findings

The generated report will state:
- Number of verified boards, including valid boards that currently return zero jobs.
- Total observed jobs in the five target cities.
- Entry-level estimates by city.
- Separate India - Remote/Other and Unclassified counts.
- Failed, blocked, and incomplete probes, kept distinct from verified boards.
- Whether the dataset clears the approximate 300-job feasibility threshold and whether city/entry-level coverage is badly skewed.

## Decision rule

Continue only if observed volume and city/entry-level balance are adequate. If fewer than about 300 jobs occur across the five cities, or entry-level opportunities are badly skewed, report that the feasibility gate has failed and revise candidate sourcing rather than concealing the gap. A successful API response with an empty jobs list is a verified board with zero jobs; a timeout, 403/429, invalid JSON, or malformed response is not a zero-job result.
