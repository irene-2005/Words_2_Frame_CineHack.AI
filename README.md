
# 🎬 **Words2Frame — The AI-Powered Film Production System**

**Team Members:**
* **Athira** — AI/ML
* **Ann** — Frontend 
* **Irene** — Backend 
  

---

### 🚀 **Elevator Pitch**

Words2Frame is an **AI-integrated film production management system** that automates everything from **script breakdown and budget prediction to crew and resource management** — empowering filmmakers to plan smarter and faster using real-time AI insights.

---

### 🧩 **Brief Description**

Words 2 Frame is an AI-powered integrated production management system that streamlines every stage of filmmaking—from pre-production to post-release. It features AI-based budget prediction, smart scheduling, real-time finance tracking, and an intuitive dashboard for efficient team collaboration.

Built with accessibility in mind, it includes colorblind-friendly themes and night-mode compatibility for an inclusive user experience. Future enhancements include AI chat assistants, weather-based shoot scheduling, and automated reminders via email or SMS.

Developed as a scalable startup concept, it aims to empower studios and creators worldwide.
Team: Ann (Frontend), Athira (AI), Irene (Backend).

Turning words into cinematic frames — powered by intelligence
---

### 🌐 **Live Demo**

**URL:** `http://203.0.113.12:3000`
**API Endpoints:** see `deployment/ENDPOINTS.md`

---

### ⚙️ **Quick Start (Local)**

1. **Clone the repo:**

```bash
git clone https://github.com/Words2Frame/Words_2_Frame_CineHack.AI.git
cd Words_2_Frame_CineHack.AI
```

2. **Create `.env` file from example and set required variables:**

```bash
cp .env.example .env
```

3. **Start with Docker Compose (recommended):**

```bash
docker compose up --build
```

4. **Open:**

```
http://localhost:3000
```

---

### 🧪 **Tests**

```bash
npm install
npm test
```

---

### 🔐 **Environment Variables**

* `PORT` — Port the server listens on
* `DATABASE_URL` — Database connection string (Firebase/Firestore)
* `FLASK_APP` — Main backend entry file (e.g., `api.py`)
* `MODEL_PATH` — Path to trained AI models
* `FIREBASE_CONFIG` — JSON credentials for Firebase integration

---

### ⚠️ **Known Limitations**

* Budget predictor model is in beta; accuracy may vary with small datasets.
* AI script breakdown may slow for scripts exceeding 200 pages.
* Multi-user live collaboration still under optimization for concurrent edits.

---

### 📜 **License**

MIT

---

