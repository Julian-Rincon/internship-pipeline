# n8n Internal Reminders Demo

This project includes a safe local n8n workflow export:

```text
n8n/workflows/internal-reminders-demo.json
```

## What It Does

- Starts from a Manual Trigger.
- Calls the backend inside Docker at `http://backend:8000/reminders/n8n-summary`.
- Formats a reminder summary in a Code node.
- Stops there.

It does not send email, outreach, Slack, Discord, LinkedIn messages or external webhooks.

## Import Steps

1. Start the local stack.
2. Open n8n at `http://localhost:5678`.
3. Import `n8n/workflows/internal-reminders-demo.json`.
4. Run the workflow manually.
5. Inspect the formatted output from the final Code node.

## URLs

- From n8n container to backend: `http://backend:8000`
- From local browser to n8n: `http://localhost:5678`
- From local browser to backend summary: `http://localhost:8000/reminders/n8n-summary`

## Limitations

This is local development only. There is no authentication on the reminders endpoint yet. Keep this workflow internal and inactive until a reviewed internal notification channel is configured.
