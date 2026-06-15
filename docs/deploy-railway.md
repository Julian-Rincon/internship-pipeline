# Deploy to Railway

## Prerequisites

- Railway account at railway.app
- GitHub repo connected: `Julian-Rincon/internship-pipeline`
- Railway CLI optional but helpful: `npm i -g @railway/cli`

---

## Backend

1. Create new project in Railway
2. Click **+ New Service → GitHub Repo** → select `internship-pipeline`, root: `backend/`
3. Add **PostgreSQL** plugin to the project
4. Add **Redis** plugin to the project
5. Set environment variables on the backend service:
   - `DATABASE_URL` — copy from PostgreSQL plugin's **Connect** tab
   - `REDIS_URL` — copy from Redis plugin's **Connect** tab
   - `SECRET_KEY` — generate: `openssl rand -hex 32`
6. After first deploy, run migrations via Railway shell:
   ```
   alembic upgrade head
   ```
7. Note the backend public URL (e.g. `https://internship-pipeline-backend.up.railway.app`)

---

## Frontend

1. Deploy to **Vercel** from GitHub repo, root: `frontend/`
2. Set environment variable:
   - `NEXT_PUBLIC_API_URL` = Railway backend URL from step 7 above
3. After deploy, note the Vercel URL (e.g. `https://internship-pipeline.vercel.app`)

---

## n8n (optional — daily digest reminders)

1. In Railway project, click **+ New Service → Docker Image** → `n8nio/n8n`
2. Set environment variables:
   - `N8N_BASIC_AUTH_ACTIVE=true`
   - `N8N_BASIC_AUTH_USER=admin`
   - `N8N_BASIC_AUTH_PASSWORD=<your-password>`
3. After deploy, open n8n at the Railway URL
4. **Import workflow**: Settings → Import → upload `n8n/workflows/internal-reminders-demo.json`
5. In the **HTTP Request** node, update the URL to your Railway backend URL
6. Add a **Telegram Bot** node with your bot token for daily digest delivery

---

## Jarvis Integration

Once backend is deployed, update Jarvis `.env`:

```
INTERNSHIP_PIPELINE_URL=https://internship-pipeline-backend.up.railway.app
```

This enables the `internship_digest` and `internship_meeting` skills to pull live data.
