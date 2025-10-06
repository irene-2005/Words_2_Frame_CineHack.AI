git clone https://github.com/your-org/your-repo.git 
docker compose up --build 
# Words2Frame

AI-powered production planning workspace that ingests film scripts, analyzes each scene, and surfaces tasks, budgets, and crew assignments through a unified dashboard.

## Local Development

### Prerequisites

- Python 3.13 (via the provided `venv` is recommended)
- Node.js 18+
- npm 9+

### Backend

```powershell
cd Words_2_Frame_CineHack.AI
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env  # update values as needed
python -m uvicorn app.main:app --reload
```

The API becomes available at `http://127.0.0.1:8000` with docs at `/docs`.

### Frontend

```powershell
cd word2frame
npm ci
copy .env.example .env.local  # set REACT_APP_API_BASE_URL
npm start
```

The React app runs on `http://localhost:3000` by default.

## Testing

- Backend: `python -m pytest`
- Frontend: `npm test`

## Deployment

Production deployment guidelines for Vercel + Render are documented in [`DEPLOYMENT.md`](DEPLOYMENT.md). Follow them to make the stack globally accessible with CI/CD via GitHub.
