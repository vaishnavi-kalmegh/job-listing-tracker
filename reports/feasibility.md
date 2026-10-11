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
## Tech-only feasibility (latest collector run before expanded role rules)

**Baseline run:** 2026-10-11 21:54 UTC. All 32/32 boards completed, with 2,120 active listings. This section is the measured pre-rule-expansion baseline; the updated rules require a new collector run before revised counts can be claimed.

- Active jobs across the five cities: **507**.
- Active tech jobs across the five cities: **215** (Product/Design tech-adjacent is currently included in this count).
- Tech-only volume in the five cities clears approximately 300 jobs: **NO**.
- The 2,120 total includes all active jobs across the five city buckets plus India - Remote/Other and Unclassified location. It does not mean 2,120 jobs are physically in the five cities.
- Phase 1's 507 count was the five-city-only subset at the earlier discovery snapshot; the Phase 2 count of 507 five-city jobs happens to match that baseline in this run. Phase 2 additionally retains 1,613 listings outside those five city buckets.

### Active jobs by location bucket and is_tech

**is_tech = true** includes the seven tech categories, including the separate Product/Design (tech-adjacent) category. **false** means Non-Tech; **null** means role Unclassified.

| Location bucket | All active jobs | is_tech = true | is_tech = false | is_tech = null |
|---|---:|---:|---:|---:|
| Pune | 38 | 19 | 6 | 13 |
| Hyderabad | 111 | 49 | 5 | 57 |
| Bengaluru | 257 | 115 | 41 | 101 |
| Delhi NCR | 71 | 30 | 22 | 19 |
| Mumbai | 30 | 2 | 10 | 18 |
| India - Remote/Other | 122 | 44 | 52 | 26 |
| Unclassified location | 1,491 | 291 | 451 | 749 |
| **Total** | **2,120** | **550** | **587** | **983** |

### Product/Design remains a separate tag

**Product/Design (tech-adjacent)** remains a distinct role_category, with **126 active listings** in the baseline run. It is currently included in is_tech = true because it is tech-adjacent, but downstream analysis can exclude this category explicitly. The updated collector report will break Product/Design counts out by location bucket after the next successful run.

### Excluded from tech-only analysis

These records remain in collection history. Non-Tech and Unclassified roles are excluded from strict tech-only analysis.

| Exclusion | Active listings |
|---|---:|
| Non-Tech | 587 |
| Unclassified role | 983 |

### Expanded role-rule update status

The title/department/team rules have been broadened without using descriptions. **The post-update Unclassified count is not yet verified**: it will be calculated from the private database on the next successful manual/daily collector run. The previous count of 983 is the pre-update baseline and must not be presented as the new count.
<!-- TECH_FEASIBILITY_END -->
