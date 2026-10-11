# Discovery workflow

1. Run `python -m discovery.gather_candidates` to extract candidate names from the listed public company/startup lists. It does not discover board tokens and does not probe APIs.
2. Use `discovery/search_queries.md` to manually find public board URLs for those candidates and add each candidate to `seeds.csv`. The source URL must itself show the relevant token (for example, `https://boards.greenhouse.io/acme` for token `acme`).
3. Run `python -m discovery.discover --max-probes 60`.
4. Run `python -m discovery.report`.

The candidate list is evidence of a company's presence on a public list, not evidence that it has a Greenhouse or Lever board. Only a token explicitly supported by a public board URL is eligible for probing. Do not fill tokens by guessing variants.

The script validates API schemas, paginates in bounded pages, keeps failed/incomplete probes distinct from verified boards, counts jobs only when a fetch is complete, and never writes descriptions to public output. Robots and API outcomes are written to the local ignored run log.
