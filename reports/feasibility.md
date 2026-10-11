# Phase 1 feasibility report

## Baseline before Phase 1b

The following numbers were supplied by the project owner from the prior Phase 1 run; this repository does not contain the prior run's raw evidence log, so they are recorded as user-provided baseline rather than independently recomputed here.

- Verified boards: 8
- Jobs in five target cities: 117
- Estimated entry-level jobs: 12
- Pune entry-level estimates: 0
- Hyderabad jobs: 0

This baseline fails the approximate 300-job volume gate and has a serious geographic coverage gap.

## Phase 1b current status

**NOT YET MEASURED — the expanded live discovery run has not been executed from this environment.**

The seed registry has been expanded with additional public board URLs found through web search, prioritizing Pune and Hyderabad. These are candidates, not verified boards. A token is considered eligible only when the public source URL visibly evidences that token. The discovery run must still validate each candidate via the official API.

No after-expansion board count, job count, entry-level count, or heuristic precision is claimed in this report. Run the following from a local clone:

```bash
python -m pip install -r requirements.txt
pytest
python -m discovery.discover --max-probes 60
python -m discovery.report
python -m discovery.sample_entry_level --sample-size 30
```

Review `reports/entry_level_review.csv`, fill `review_label` with true/false based on human judgement, then run:

```bash
python -m discovery.score_entry_level_review
```

The sample script selects up to 30 predicted-positive and 30 predicted-negative titles using a fixed random seed. Precision cannot honestly be calculated until the reviewer labels the predicted-positive sample; the script does not fabricate ground truth.

## Required findings after a live run

The generated report must state:
- Number of verified boards, including valid zero-job boards.
- Total jobs in the five target cities.
- Entry-level estimates per city.
- India - Remote/Other and Unclassified kept separate from the five-city total.
- Failed, blocked, invalid, and incomplete probes separately.
- Whether the volume clears the approximate 300-job gate and whether city coverage remains badly skewed.

## Decision rule

Do not proceed to model work if the target-city volume is below approximately 300 or city/entry-level coverage is badly skewed. Expand evidence-backed sources, especially Pune and Hyderabad, rather than inventing numbers. A failed request is not a zero-job board, and a valid complete zero-job response is still a verified board.
