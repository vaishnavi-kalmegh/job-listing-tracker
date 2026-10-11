# Manual candidate discovery searches

Use these links to find candidate companies and public board URLs. Search result pages are reviewed manually; the script does not scrape search engines or enumerate guessed tokens. For each candidate, record the source URL and only tokens directly evidenced by a public board URL or an editable seed.

## Public company/startup lists

- [Wikipedia: List of companies of India](https://en.wikipedia.org/wiki/List_of_companies_of_India)
- [Wikipedia: List of unicorn startup companies](https://en.wikipedia.org/wiki/List_of_unicorn_startup_companies)
- [Public Indian startup list on GitHub](https://github.com/edebashis/Startups-In-India-2024)

## Public job board search queries

- [Greenhouse boards mentioning Pune](https://www.google.com/search?q=site%3Aboards.greenhouse.io+Pune)
- [Greenhouse boards mentioning Hyderabad](https://www.google.com/search?q=site%3Aboards.greenhouse.io+Hyderabad)
- [Greenhouse boards mentioning Bengaluru/Bangalore](https://www.google.com/search?q=site%3Aboards.greenhouse.io+%28Bengaluru+OR+Bangalore%29)
- [Greenhouse boards mentioning Delhi NCR](https://www.google.com/search?q=site%3Aboards.greenhouse.io+%28Delhi+OR+Gurgaon+OR+Noida%29)
- [Greenhouse boards mentioning Mumbai](https://www.google.com/search?q=site%3Aboards.greenhouse.io+Mumbai)
- [Lever boards mentioning Pune](https://www.google.com/search?q=site%3Ajobs.lever.co+Pune)
- [Lever boards mentioning Hyderabad](https://www.google.com/search?q=site%3Ajobs.lever.co+Hyderabad)
- [Lever boards mentioning Bengaluru/Bangalore](https://www.google.com/search?q=site%3Ajobs.lever.co+%28Bengaluru+OR+Bangalore%29)
- [Lever boards mentioning Delhi NCR](https://www.google.com/search?q=site%3Ajobs.lever.co+%28Delhi+OR+Gurgaon+OR+Noida%29)
- [Lever boards mentioning Mumbai](https://www.google.com/search?q=site%3Ajobs.lever.co+Mumbai)

## Seed format

- `company_name`: human-readable company name.
- `source_url`: public source proving the company or board URL exists.
- `greenhouse_token` / `lever_token`: only fill if the token is explicitly visible in a documented public board URL. Leave blank otherwise.
- `notes`: evidence context, not speculation.

Candidates discovered from public lists without a board URL may be added with an empty token; they are not probed until evidence-backed tokens are supplied.
