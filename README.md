# 🎬 Words2Frame — The AI-Powered Film Production System

**Team Members**

- Athira — AI/ML
- Ann — Frontend
- Irene — Backend

---

## 🚀 Elevator Pitch

Words2Frame is an AI-integrated film production management platform that automates script breakdowns, budget prediction, crew allocation, and scheduling—helping filmmakers plan smarter and faster with real-time insights.

## 🧩 What It Does

The system supports the entire production pipeline, from ingesting raw scripts to surfacing actionable dashboards. Accessibility features (color-blind-friendly palette, high-contrast mode) are built in, and the roadmap includes AI chat assistance, weather-aware scheduling, and automated reminders.

---

## ⚙️ Local Development

### Prerequisites

- Python 3.13 (using the provided `venv` is recommended)
- Node.js 18+
- npm 9+

### Backend (FastAPI)

```powershell
cd Words_2_Frame_CineHack.AI
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # update values as needed
python -m uvicorn app.main:app --reload
```

The API becomes available at `http://127.0.0.1:8000` with interactive docs at `/docs`.

### Frontend (React)

```powershell
cd word2frame
npm ci
copy .env.example .env.local  # set REACT_APP_API_BASE_URL
npm start
```

The React app runs on `http://localhost:3000` by default.

---

## 🧪 Testing

- Backend: `python -m pytest`
- Frontend: `npm test`

---

## 🔐 Environment Variables

Create environment files from the provided examples and set:

- `DATABASE_URL` — Override to point at your production database (defaults to local SQLite).
- `SUPABASE_URL`, `SUPABASE_KEY` — Required for live Supabase authentication.
- `SUPABASE_TESTING` — Set to `1` for local development to bypass Supabase checks.
- `REACT_APP_API_BASE_URL` — Frontend base URL for the backend API.

Additional variables (e.g., model paths, third-party keys) should be injected via hosting provider dashboards rather than committed to the repo.

---

## 🚢 Deployment

Global deployment instructions for Vercel (frontend) and Render (backend) live in [`DEPLOYMENT.md`](DEPLOYMENT.md). The repository also includes:

- `.github/workflows/ci.yml` — Continuous integration running pytest and the React build.
- `render.yaml` — Render service definition for the FastAPI backend + PostgreSQL.
- `word2frame/vercel.json` — Vercel configuration for the React app.

Follow the guide to hook the repository to GitHub, configure environment variables, and enable automatic redeployments.

---

## ⚠️ Known Limitations

- Budget predictions can vary on small datasets.
- Very large scripts (>200 pages) may take longer to process.
- Real-time multi-user collaboration is still being optimized.

---

## 📜 License

MIT
