
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

Built using **Python Flask, React, and Firebase**, Words2Frame enables directors or production leads to upload scripts, automatically break them down scene-by-scene using NLP, generate predictive budget insights, and manage cast, crew, and production timelines seamlessly — all in one interactive dashboard.

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

Would you like me to add a **“Tech Stack + Architecture Diagram”** section (like most hackathon README files include) right after “Brief Description”? It makes your repo look more professional.
