# Phase 1 feasibility report

Generated from local discovery run at 2026-10-11T21:04:39.367555+00:00.
All counts below are derived from verified, complete API responses in this run.

- **Verified boards:** 32 (valid zero-job boards count as verified).
- **Jobs in the five target cities:** 507.
- **Entry-level jobs across the five cities:** 21.
- **API probes attempted:** 34.
- **Failed, blocked, invalid, or incomplete probes:** 2.
- **Feasibility decision:** Enough data to continue to Phase 2

## Before vs after expansion

| Metric | Before Phase 1b (owner-provided) | After Phase 1b (this run) |
|---|---:|---:|
| Verified boards | 8 | 32 |
| Jobs in five target cities | 117 | 507 |
| Estimated entry-level jobs | 12 | 21 |
| Pune entry-level jobs | 0 | 1 |
| Hyderabad jobs | 0 | 111 |

| City | Jobs | Entry-level estimate |
|---|---:|---:|
| Pune | 38 | 1 |
| Hyderabad | 111 | 6 |
| Bengaluru | 257 | 10 |
| Delhi NCR | 71 | 2 |
| Mumbai | 30 | 2 |

## Interpretation

Entry-level counts are heuristic estimates based on titles and descriptions; they are not a verified seniority field.
A board probe that fails, is blocked, returns invalid JSON, or cannot be completely paginated is not treated as a verified zero-job board.
This report uses target-city counts only. India - Remote/Other and Unclassified are kept separate and are not counted toward the five-city threshold.
If volume is below approximately 300 jobs or any city has no observed entry-level roles, expand evidence-backed candidate sources and manually inspect more public board URLs. Do not brute-force tokens.

## Probe outcomes

| Platform | Company | Token | Verified | Status | HTTP |
|---|---|---|---|---|---:|
| lever | Mindtickle | mindtickle | True | ok | 200 |
| lever | Acceldata | acceldata | True | ok | 200 |
| lever | 100ms | 100ms | True | ok | 200 |
| lever | Doxel | doxel | True | ok | 200 |
| lever | Sprinto | Sprinto | True | ok | 200 |
| lever | Level AI | levelai | True | ok | 200 |
| lever | Weekday | weekdayworks | True | ok | 200 |
| greenhouse | Cialfo | cialfo | True | ok | 200 |
| lever | Cprime | cprime | True | ok | 200 |
| lever | Dun & Bradstreet | dnb | True | ok | 200 |
| lever | Sonatype | sonatype | True | ok | 200 |
| lever | Matillion | matillion | True | ok | 200 |
| lever | Brillio | brillio-2 | True | ok | 200 |
| lever | Veeva Systems | veeva | True | ok | 200 |
| lever | Entrata | entrata | True | ok | 200 |
| lever | Allata | Allata | True | ok | 200 |
| lever | Perforce | perforce | True | ok | 200 |
| lever | Coupa | coupa | True | ok | 200 |
| lever | FloQast | floqast | True | ok | 200 |
| lever | Smart Working Solutions | smart-working-solutions | True | ok | 200 |
| lever | Resilinc | resilinc | True | ok | 200 |
| lever | ION Group | ion | True | ok | 200 |
| lever | BlueMatrix | BlueMatrix | True | ok | 200 |
| lever | Keyloop | keyloop | True | ok | 200 |
| lever | Egen | egen | True | ok | 200 |
| lever | ValGenesis | valgenesis | True | ok | 200 |
| lever | Zeta | zeta | True | ok | 200 |
| lever | Outreach | outreach | True | ok | 200 |
| lever | Omni Design Technologies | omnidesigntech | True | ok | 200 |
| lever | JumpCloud | jumpcloud | True | ok | 200 |
| greenhouse | Berkadia India | berkadiaindia | False | http_error: status=404 | None |
| greenhouse | Modernizing Medicine | modernizingmedicineinc | False | http_error: status=404 | None |
| greenhouse | Tide | tide | True | ok | 200 |
| greenhouse | Sony Music Careers Asia Middle East | sonymusicasiacareers | True | ok | 200 |

<!-- TECH_FEASIBILITY_START -->
## Tech-only feasibility (latest successful collector history)

**Pending live collector run.** Phase 1 established 32 verified boards and 507 jobs across the five city buckets, but the repository does not contain the title-level source data needed to produce defensible tech-only counts. No tech-only volume claim is made until the collector runs against the private database.

| City | All active jobs | Tech-only jobs |
|---|---:|---:|
| Pune | Pending | Pending |
| Hyderabad | Pending | Pending |
| Bengaluru | Pending | Pending |
| Delhi NCR | Pending | Pending |
| Mumbai | Pending | Pending |

### Excluded from analysis

Non-Tech and Unclassified jobs remain in collection history. They are excluded from tech-only analysis and will be counted separately after a successful collector run.

| City/bucket | Non-Tech | Unclassified |
|---|---:|---:|
| Pune | Pending | Pending |
| Hyderabad | Pending | Pending |
| Bengaluru | Pending | Pending |
| Delhi NCR | Pending | Pending |
| Mumbai | Pending | Pending |
| India - Remote/Other | Pending | Pending |
| Unclassified | Pending | Pending |

<!-- TECH_FEASIBILITY_END -->
