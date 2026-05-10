# ATS Source Examples

These examples are fictional and show how to identify `source_key` values for controlled public ATS intake. Do not add credentials or private URLs.

## Greenhouse

Pattern:

```text
https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
```

Fictional example:

```text
https://boards-api.greenhouse.io/v1/boards/exampleboard/jobs?content=true
```

Use:

```text
source_type = greenhouse
source_key = exampleboard
```

## Lever

Pattern:

```text
https://api.lever.co/v0/postings/{site}?mode=json
```

Fictional example:

```text
https://api.lever.co/v0/postings/example-company?mode=json
```

Use:

```text
source_type = lever
source_key = example-company
```

## Ashby

Pattern:

```text
https://api.ashbyhq.com/posting-api/job-board/{job_board_name}?includeCompensation=false
```

Fictional example:

```text
https://api.ashbyhq.com/posting-api/job-board/example-company?includeCompensation=false
```

Use:

```text
source_type = ashby
source_key = example-company
```

## Safety Notes

- Use public unauthenticated ATS JSON endpoints only.
- Do not add LinkedIn, Apollo, Hunter or arbitrary website pages.
- Do not add secrets, tokens, cookies or credentials.
- Running a source creates pending discovery candidates only. Human review is still required.
