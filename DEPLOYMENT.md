# Global Deployment Guide

This guide explains how to deploy the Words2Frame application so the React frontend and FastAPI backend are publicly accessible. The recommended setup is **Vercel** for the frontend and **Render** for the backend with a managed PostgreSQL database. Adapt as needed for your preferred providers (Railway, AWS, etc.).

---

## 1. Prerequisites

- A Git provider account (GitHub recommended).
- Vercel account connected to your Git provider.
- Render account with access to deploy a Python web service and provision PostgreSQL.
- Local copies of the `.env` files with secrets removed before committing.

---

## 2. Repository Structure

```
Words_2_Frame_CineHack.AI/
├── app/                 # FastAPI backend
├── word2frame/          # React frontend (Create React App)
├── requirements.txt     # Python dependencies
├── package.json         # React project manifest (inside word2frame/)
├── render.yaml          # Render deployment descriptor
├── word2frame/vercel.json
├── .env.example
└── DEPLOYMENT.md
```

---

## 3. Environment Variables

Duplicate `.env.example` and populate the following values:

### Backend (`Render` → **Environment → Environment Variables**)

| Key | Description |
| --- | --- |
| `DATABASE_URL` | Render automatically injects the PostgreSQL connection string once you link the managed database. |
| `SUPABASE_URL` | Supabase project URL. Required if you are using Supabase auth in production. |
| `SUPABASE_KEY` | Supabase service role or anon key. |
| `SUPABASE_TESTING` | Remove in production unless you intend to bypass Supabase auth. |

### Frontend (`Vercel` → **Project Settings → Environment Variables**)

| Key | Description |
| --- | --- |
| `REACT_APP_API_BASE_URL` | Public URL of the deployed backend (e.g. `https://words2frame-api.onrender.com`). |

Create two environments on Vercel:
- **Preview** (applies to preview deployments generated from pull requests).
- **Production** (applies to the production branch, usually `main`).

---

## 4. Backend Deployment (Render)

1. Push the repository to GitHub (instructions in section 6).
2. In Render, click **New → Web Service** and choose the repo.
3. When prompted, Render will detect `render.yaml`. Confirm the service creation.
4. Modify service parameters if desired (instance size, region, etc.).
5. Provision a **PostgreSQL** instance:
   - Render → **New → PostgreSQL**.
   - After creation, go to the new database dashboard and click **Connect**. Copy the `Internal Database URL`.
6. In the web service settings, add an environment variable `DATABASE_URL` with the value from step 5.
7. Trigger a deploy. Render executes:
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. After the deploy succeeds, note the public URL (e.g., `https://words2frame-api.onrender.com`).
9. Optional: add a health check route `/` already provided by FastAPI.

### Database migration

The application auto-creates missing tables on startup thanks to `Base.metadata.create_all(...)`. No manual migration step is required for the initial deploy.

---

## 5. Frontend Deployment (Vercel)

1. Connect your GitHub repo to Vercel and import the project. Choose the `word2frame` folder when Vercel asks for the project root.
2. During setup:
   - Framework preset: **Create React App**
   - Build command: `npm run build`
   - Output directory: `build`
   - Install command: `npm ci`
3. Add the environment variable `REACT_APP_API_BASE_URL` pointing to the Render backend URL. Do this for both Production and Preview environments.
4. Deploy. Vercel will automatically build and serve the optimized React bundle. The production URL looks like `https://words2frame.vercel.app`.
5. Verify the frontend loads and calls the backend URL from step 4. CORS is already configured to allow all origins; tighten it later if needed.

---

## 6. GitHub Workflow

1. Initialize a new repository:
   ```bash
   git init
   git remote add origin https://github.com/<your-org>/words2frame.git
   git add .
   git commit -m "Initial public release"
   git push -u origin main
   ```
2. Configure branch protections on `main` if desired.
3. Enable automatic redeployments:
   - **Render** and **Vercel** both watch the connected Git branches and redeploy on push by default.
4. Continuous Integration is already wired via `.github/workflows/ci.yml`:
   - Runs Python tests and builds the React app on every push/PR.
   - Extend this workflow with linting or deployment triggers as needed.
5. Contributors can now fork or create pull requests, and each push triggers Preview deploys on Vercel.

---

## 7. Post-Deployment Validation

1. **Backend**: Visit `https://<render-app>.onrender.com/docs` to access interactive API docs. Run `/projects/default`, `/projects/{id}/analyze_script`, and `/projects/{id}/reports` using sample data.
2. **Frontend**: Navigate to the Vercel URL. Confirm data loads, uploads function, and dashboards render.
3. **AI Features**: Upload the demo script provided in `uploads/` to ensure analysis works. Render persistently stores generated scenes in PostgreSQL.
4. **Error Tracking**: Optionally integrate Sentry or Logtail by adding their environment variables.

---

## 8. Maintenance Tips

- Rotate Supabase keys regularly and store them securely (e.g., in Vercel/Render secret managers).
- Schedule database backups from Render's dashboard.
- For large file uploads, consider migrating to an object store (S3, R2) and storing only references in the database.
- Monitor costs: Render free tiers sleep after inactivity. Upgrade to keep the API always on.

With these steps complete, the Words2Frame project is publicly accessible with CI/CD hooks from GitHub.
