# Team Onboarding

This guide explains how a student team should use the app for internship pipeline coordination. Use fictional/demo records for practice. Do not commit real personal data, secrets or credentials.

## 1. Add Team Members

Open `/users` and create one user per team member.

Each member should complete their progressive profile:

- name and email
- role
- profile status
- GitHub handle
- portfolio URL
- CV URL
- target roles
- target countries and regions
- target company types
- preferred industries
- technical interests
- strong skills
- learning goals
- internship goals

Profiles are used for team visibility only. There is no authentication or permissions layer yet.

## 2. Register ATS Sources

Open `/discovery/sources`.

Add public ATS sources only:

- Greenhouse: use the board token as `source_key`
- Lever: use the Lever site as `source_key`
- Ashby: use the job board name as `source_key`

Add a clear name, optional company hint, country and region. Do not add credentials, private endpoints or arbitrary web pages.

## 3. Run Sources

From `/discovery/sources`, run a single source or all enabled sources.

The system performs one public unauthenticated GET request per source, keeps likely internship or early-career titles, creates job postings and creates discovery candidates with `pending_review` status.

## 4. Review Discovery Candidates

Open `/discovery`.

Review each candidate before it becomes an official company. Check:

- company name
- source
- detected role
- job URL
- careers URL
- country and region
- confidence score

Approve candidates that belong in the team pipeline. Reject candidates that are irrelevant, duplicated in context or not appropriate.

Approving creates or links a company. Rejecting keeps the candidate out of the active company list.

## 5. Claim Companies

Open a company detail page from `/companies`.

Use the team coordination panel to claim the company for a user. Add ownership notes when useful. Claimed companies can be moved to `claimed`, `paused` or `done`, or released back to `unclaimed`.

Claiming is coordination metadata only. It is not access control.

## 6. Create Applications

Open `/applications`.

Create applications manually and link them to:

- company
- user
- optional contact

Keep status, next action, due date and notes up to date. This is the main tracker for team activity.

## 7. Use Reminders

Open `/reminders`.

Use reminders to find:

- overdue application actions
- application actions due today
- upcoming application actions
- pending discovery candidates
- stale claimed companies

Reminders are internal visibility only. They do not send email or outreach.

## 8. Outreach Policy

All outreach and contacting remains manual and human-reviewed. The app does not send emails, LinkedIn messages or external notifications to candidates, recruiters or companies.

Do not add LinkedIn scraping, Apollo, Hunter, email senders, LLM matching, embeddings, paid APIs or secrets without a separate review and explicit approval.
