# I&E Manager — Full Stack Project
### Smart Income & Expense Management System
**Frontend (HTML/CSS/JS) + Backend (Python/Flask) + Database (SQLite)**

---

## Project Structure

```
ie-manager-fullstack/
│
├── frontend/
│   └── index.html           ← Complete frontend (all pages in one file)
│
└── backend/
    ├── app.py               ← Flask entry point — RUN THIS
    ├── config.py            ← App configuration
    ├── requirements.txt     ← Python packages to install
    ├── Procfile             ← For deployment (Render/Railway)
    ├── .env                 ← Secret keys (do not share this file)
    ├── ie_manager.db        ← SQLite database (auto-created on first run)
    │
    ├── models/
    │   └── database.py      ← User + Transaction table definitions
    │
    ├── routes/
    │   ├── auth_routes.py         ← /api/auth/* endpoints
    │   ├── transaction_routes.py  ← /api/transactions/* endpoints
    │   └── analytics_routes.py   ← /api/analytics/* endpoints
    │
    └── utils/
        ├── auth_utils.py    ← JWT tokens, password hashing
        ├── analytics.py     ← Pandas analytics engine
        └── validators.py    ← Input validation
```

---

## Technology Stack

| Layer        | Technology          | Why                                 |
|--------------|---------------------|-------------------------------------|
| Frontend     | HTML5 + CSS3 + JS   | Clean, responsive UI                |
| Backend      | Python + Flask      | REST API framework                  |
| Database     | SQLite              | Embedded DB, no server needed       |
| ORM          | SQLAlchemy          | Python classes → DB tables          |
| Auth         | JWT + Werkzeug      | Token-based auth, hashed passwords  |
| Analytics    | Pandas + NumPy      | Data processing & insights          |
| Charts       | Chart.js            | Interactive visualizations          |

---

## ════════════════════════════════════
## STEP-BY-STEP SETUP (LOCAL)
## ════════════════════════════════════

### STEP 1 — Install Python
Download Python 3.10+ from: https://python.org
✅ Check: open terminal and type `python --version`

---

### STEP 2 — Set up the backend

Open terminal/command prompt:

```bash
# Go into the backend folder
cd ie-manager-fullstack/backend

# Install all required Python packages
pip install -r requirements.txt
```

---

### STEP 3 — Run the backend server

```bash
# Make sure you are in the backend folder
cd ie-manager-fullstack/backend

# Start the Flask server
python app.py
```

You should see:
```
✅ Database ready.
🚀 I&E Manager Backend running at http://localhost:5000
```

Leave this terminal open. The backend is now running.

---

### STEP 4 — Open the frontend

1. Open the `frontend/` folder
2. Double-click `index.html`
3. It opens in your browser at something like `file:///...index.html`

OR run a simple local server (recommended):

```bash
# In a NEW terminal
cd ie-manager-fullstack/frontend
python -m http.server 8080
```
Then open: **http://localhost:8080**

---

### STEP 5 — Use the app

1. Click **Create account**
2. Register with name, email, password
3. You are automatically logged in
4. Add transactions → see charts update → check insights!

---

## ════════════════════════════════════
## DEPLOY TO THE INTERNET (FREE)
## ════════════════════════════════════

### BACKEND DEPLOYMENT — Render.com (Recommended, Free)

1. Create free account at: **https://render.com**

2. Push backend to GitHub:
```bash
cd ie-manager-fullstack/backend
git init
git add .
git commit -m "Initial backend"
# Create repo on github.com, then:
git remote add origin https://github.com/YOURUSERNAME/ie-manager-backend.git
git push -u origin main
```

3. On Render:
   - Click **New → Web Service**
   - Connect your GitHub repo
   - Set these fields:
     - **Build command:** `pip install -r requirements.txt`
     - **Start command:** `gunicorn app:app`
   - Add **Environment Variables:**
     - `SECRET_KEY` → any random string (e.g. `my-secret-key-abc123`)
     - `JWT_SECRET_KEY` → any random string (e.g. `jwt-key-xyz789`)
   - Click **Deploy**

4. You get a URL like: `https://ie-manager.onrender.com`

5. **Update frontend:** open `frontend/index.html`, find line:
   ```javascript
   const API_BASE = "http://localhost:5000/api";
   ```
   Change to:
   ```javascript
   const API_BASE = "https://ie-manager.onrender.com/api";
   ```

---

### FRONTEND DEPLOYMENT — Netlify (Free, instant)

1. Go to: **https://netlify.com** → Sign up free
2. Drag your `frontend/` folder onto the Netlify dashboard
3. Done! You get a live URL like: `https://ie-manager.netlify.app`

---

### ALTERNATIVE BACKEND — Railway.app (Free tier)

1. Go to: **https://railway.app**
2. New Project → Deploy from GitHub
3. Add environment variables (same as Render)
4. Auto-deploys on every push

---

## All API Endpoints

### Auth (`/api/auth`)
| Method | Path       | What it does               |
|--------|------------|----------------------------|
| POST   | /register  | Create new account         |
| POST   | /login     | Sign in, receive JWT token |
| GET    | /profile   | Get your profile           |
| PUT    | /profile   | Update name or password    |

### Transactions (`/api/transactions`)
| Method | Path          | What it does               |
|--------|---------------|----------------------------|
| GET    | /             | List all (filter + pages)  |
| POST   | /             | Add new transaction        |
| GET    | /<id>         | Get one transaction        |
| PUT    | /<id>         | Edit transaction           |
| DELETE | /<id>         | Delete transaction         |
| GET    | /export       | Download as CSV file       |
| GET    | /categories   | Get valid categories       |

### Analytics (`/api/analytics`)
| Method | Path             | What it does                    |
|--------|------------------|---------------------------------|
| GET    | /dashboard       | All data (summary+charts+more)  |
| GET    | /summary         | Totals + savings rate           |
| GET    | /pie             | Expense by category             |
| GET    | /bar             | Income vs Expense vs Investment |
| GET    | /trend           | Monthly trend data              |
| GET    | /insights        | Behavioral insights text        |
| GET    | /health          | Health score 0-100              |
| GET    | /top-categories  | Ranked spending categories      |

---

## Database Schema (SQLite)

```
USERS TABLE
─────────────────────────────────────────
id          INTEGER  PRIMARY KEY
name        TEXT     NOT NULL
email       TEXT     NOT NULL UNIQUE
password    TEXT     NOT NULL  (hashed, never plain text)
created_at  DATETIME

TRANSACTIONS TABLE
─────────────────────────────────────────
id          INTEGER  PRIMARY KEY
user_id     INTEGER  FOREIGN KEY → users.id
description TEXT     NOT NULL
amount      REAL     NOT NULL
category    TEXT     NOT NULL
type        TEXT     NOT NULL  (income | expense | investment)
date        DATE     NOT NULL
created_at  DATETIME
```

---

## Quick Test (after backend is running)

Test register via terminal:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"pass123"}'
```

Expected response:
```json
{"message": "Account created.", "token": "eyJ...", "user": {...}}
```
