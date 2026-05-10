# Discovery Sources

Discovery sources are controlled public ATS board configurations. They are not generic scraping and they are not outreach.

## Supported Sources

- Greenhouse: `source_key` is the board token.
- Lever: `source_key` is the Lever site.
- Ashby: `source_key` is the Ashby job board name.

## Run Behavior

When a source runs, the backend:

- Performs one unauthenticated HTTP GET request to the known ATS JSON endpoint.
- Uses a clear local-development User-Agent.
- Uses a timeout.
- Does not retry aggressively.
- Does not crawl linked pages.
- Limits intake to 50 items per source.
- Keeps only likely internship or early-career titles.
- Creates or reuses `JobPosting` records by URL.
- Creates `DiscoveryCandidate` records with `pending_review` status.

## Review Requirement

ATS intake never creates final companies directly. A human must review and approve each candidate from `/discovery`.

## Safety Boundaries

Do not add LinkedIn, Apollo, Hunter, email sending, outreach, LLM matching, paid APIs, credentials or secrets to this layer.
