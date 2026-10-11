# Alternative public job-board API research

Research date: 2026-10-12. This is a preliminary technical and terms review, not legal advice. No platform below has been added to the collector. User approval is required before adding any new source.

## Summary

| Platform | Official documentation | What the documented endpoint returns | Access and terms assessment | Recommendation |
|---|---|---|---|---|
| Ashby | https://developers.ashbyhq.com/docs/public-job-posting-api | Public Job Posting API returns currently published postings for a board, including title, location, department/team, employment type, job URL and other fields when available. Endpoint: `GET https://api.ashbyhq.com/posting-api/job-board/{JOB_BOARD_NAME}`. | The endpoint is explicitly described as public and intended for a company's own careers page. Documentation does not, by itself, grant blanket permission for bulk collection or redistribution. Review Ashby's current terms and any applicable restrictions before use. | Technically promising; hold pending terms/reuse review and explicit approval. |
| SmartRecruiters | https://developers.smartrecruiters.com/docs/endpoints | Public Posting API `GET /v1/companies/{companyIdentifier}/postings` lists active postings published by a company; posting detail is available at `/postings/{postingId}`. Pagination and location filters are documented. | Official docs identify a Posting API that can expose public data without authentication. API use is governed by SmartRecruiters' API Policy, which points to SAP API Policy; this is not a blanket redistribution license. Review current policy and restrictions before recurring collection. | Technically promising; hold pending policy review and explicit approval. |
| Workable | https://workable.readme.io/reference/jobs and https://workable.readme.io/reference/jobs-1 | The account API `GET https://www.workable.com/api/accounts/{subdomain}` returns public jobs for an account. The authenticated `/{subdomain}.workable.com/spi/v3/jobs` endpoint returns account jobs, paging information, and job states; it requires a customer API token and `r_jobs` scope. | Public account endpoint exists, but terms must be read for automated reuse and redistribution. The authenticated SPI is designed for account customers and should not be treated as a general anonymous discovery API. Public job-board terms are distinct from API access rights. | Possible public endpoint candidate; do not add until terms and usage restrictions are verified. |
| Recruitee / Tellent | https://docs.recruitee.com/reference/intro-to-careers-site-api and https://docs.recruitee.com/reference/authentication-1 | Careers Site API can list company offers; current docs require a Careers Site API token in `X-Careers-Sites-Token`. The broader ATS API uses bearer-token authentication. | Not an anonymous public API: authentication/token provision is required. The docs describe customer-managed access and don't grant general third-party collection rights. Public job pages or XML feeds are not automatically permission to scrape them. | Do not add to anonymous discovery pipeline. Reconsider only with documented authorization and terms review. |

## Source notes

- Ashby docs: https://developers.ashbyhq.com/docs/public-job-posting-api
- SmartRecruiters docs: https://developers.smartrecruiters.com/docs/endpoints and https://developers.smartrecruiters.com/docs/authentication
- Workable docs: https://workable.readme.io/reference/jobs-1 and https://help.workable.com/hc/en-us/articles/115012771647-Using-the-Workable-API-to-create-a-careers-page
- Recruitee docs: https://docs.recruitee.com/reference/intro-to-careers-site-api and https://docs.recruitee.com/reference/authentication-1
- SmartRecruiters API policy context: https://developers.smartrecruiters.com/docs/the-smartrecruiters-platform
- Workable terms: https://www.workable.com/terms and job board terms: https://jobs.workable.com/terms

## Decision requested

Ashby and SmartRecruiters appear most promising technically, but neither should be enabled until the current legal/terms review is completed. Workable's public account endpoint warrants further terms review. Recruitee requires a token for the documented Careers Site API and is not suitable as an anonymous source under current documentation. **No alternative platform is added without user approval.**
