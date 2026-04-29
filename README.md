# PicklePairs 🥒

Random pickleball team generator — create a room, share the code, and let the app split players into balanced teams instantly.

## Features

- **Instant rooms** — 4-character codes, no accounts required
- **Real-time updates** — WebSocket broadcasts when players join or teams are generated
- **Creator controls** — Only the room creator can generate teams or close the room
- **Persistent sessions** — Name and creator token stored in localStorage so page refreshes don't kick you out

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, CSS Modules |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Real-time | WebSockets |
| Hosting (backend) | Railway |
| Hosting (frontend) | Vercel / Netlify |

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally

### 1. Clone the repo

```bash
git clone https://github.com/GioLopera/PicklePairs.git
cd PicklePairs
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values (see Environment Variables below)

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### 3. Frontend setup

```bash
cd frontend-web

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your values

# Start dev server
npm run dev
```

App available at `http://localhost:5173`

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/picklepairs` |
| `SECRET_KEY` | 64-char hex string for secure tokens | `openssl rand -hex 32` |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |

### Frontend (`frontend-web/.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend REST API base URL | `http://localhost:8000` |
| `VITE_WS_URL` | Backend WebSocket base URL | `ws://localhost:8000` |

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check |
| `POST` | `/rooms/` | — | Create a new room |
| `GET` | `/rooms/{code}` | — | Get room details |
| `DELETE` | `/rooms/{code}` | Creator token | Close a room |
| `POST` | `/rooms/{code}/players` | — | Join a room |
| `GET` | `/rooms/{code}/players` | — | List players |
| `POST` | `/rooms/{code}/run` | Creator token | Generate teams |
| `GET` | `/rooms/{code}/results/latest` | — | Latest team result |
| `WS` | `/ws/{code}` | — | Real-time updates |

Creator token is passed via the `x-creator-token` request header.

---

## Project Structure

```
PicklePairs/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS + router registration
│   │   ├── models.py        # SQLAlchemy models (Room, Player, TeamResult)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── crud.py          # Database operations
│   │   ├── routers/         # Route handlers
│   │   └── websocket.py     # WebSocket connection manager
│   ├── alembic/             # Database migrations
│   ├── tests/               # Pytest test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend-web/
│   ├── src/
│   │   ├── pages/           # Home, Room, NotFound
│   │   ├── components/      # PlayerChecklist, TeamResult, ShareButton, Toast
│   │   ├── hooks/           # useRoom, useRoomSocket
│   │   └── styles/          # global.css design tokens
│   ├── public/              # Static assets (favicon, SVG)
│   └── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml           # Lint + test on every PR
└── README.md
```

---

## Deployment

### Backend → Railway

1. Connect the `PicklePairs` GitHub repo in Railway
2. Set the root directory to `backend`
3. Add environment variables in the Railway dashboard
4. Railway uses `railway.toml` — migrations run automatically on deploy

### Frontend → Vercel

1. Import the repo in Vercel
2. Set root directory to `frontend-web`
3. Add environment variables (`VITE_API_URL`, `VITE_WS_URL`) pointing to your Railway URL
4. Vercel detects Vite automatically — no extra config needed

### Custom Domain

Point your domain's DNS to Vercel (frontend) and optionally to Railway (backend subdomain, e.g. `api.yourdomain.com`).

---

## Contributing

1. Fork the repo and create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes and run tests: `cd backend && pytest`
3. Run the linter: `cd frontend-web && npm run lint`
4. Open a pull request — CI will run automatically

---

## License

MIT
