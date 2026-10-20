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

The Phase 1 entry-level counts above are historical heuristic estimates, not a verified seniority field. Phase 2 stores entry_level as a title-based flag only; it never filters collection.
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

- Active jobs across the five cities: **488**.
- Active tech jobs across the five cities: **231**.
- Tech-only volume clears approximately 300 jobs: **NO**.
- Existing active listings moved from non-city buckets into the five cities by the updated location rules: **0**, including **0 tech jobs**.
- Counts below are active records in the private collection database; all roles are collected, and filtering is applied only for analysis.

| City | All active jobs | Tech-only jobs | Product/Design tag |
|---|---:|---:|---:|
| Pune | 35 | 15 | 2 |
| Hyderabad | 122 | 70 | 3 |
| Bengaluru | 241 | 114 | 13 |
| Delhi NCR | 60 | 29 | 2 |
| Mumbai | 30 | 3 | 0 |

### All active jobs by location bucket and is_tech

The is_tech field is true for technical roles and Product/Design (tech-adjacent), false for Non-Tech, and null for Unclassified roles. Product/Design remains separately counted and can be included or excluded downstream. Outside India means the location explicitly names a non-India country or a recognized non-India city; Unparsed means the location could not be determined conservatively.

| Location bucket | All active jobs | is_tech = true | is_tech = false | is_tech = null | Product/Design |
|---|---:|---:|---:|---:|---:|
| Pune | 35 | 15 | 7 | 13 | 2 |
| Hyderabad | 122 | 70 | 3 | 49 | 3 |
| Bengaluru | 241 | 114 | 38 | 89 | 13 |
| Delhi NCR | 60 | 29 | 18 | 13 | 2 |
| Mumbai | 30 | 3 | 12 | 15 | 0 |
| India - Remote/Other | 52 | 21 | 15 | 16 | 0 |
| Outside India | 1185 | 308 | 368 | 509 | 122 |
| Unparsed | 342 | 113 | 93 | 136 | 23 |

### Excluded from analysis

These records remain in collection history and are excluded from tech-only analysis.

| Location bucket | Non-Tech | Unclassified role |
|---|---:|---:|
| Pune | 7 | 13 |
| Hyderabad | 3 | 49 |
| Bengaluru | 38 | 89 |
| Delhi NCR | 18 | 13 |
| Mumbai | 12 | 15 |
| India - Remote/Other | 15 | 16 |
| Outside India | 368 | 509 |
| Unparsed | 93 | 136 |
<!-- TECH_FEASIBILITY_END -->
