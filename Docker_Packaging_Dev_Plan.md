# TradingAgentsPlus — Docker Packaging Dev Plan

## 0. Goal & Success Criteria

**Goal:** Ship a "no-dev-tools required" local app that runs with:
- `docker compose up -d` (or a wrapper script `./run.sh` / `run.ps1`)
- Opens UI in browser at a single URL (e.g. `http://localhost:8080`)
- Backend auto-connects to Ollama, with clear readiness checks
- **No venv / pip / node installs required for end users**

**Success criteria:**
- Fresh machine + Docker installed → app runs in < 5 minutes
- Works on macOS + Windows + Linux (Compose)
- Models persist across restarts (volume for Ollama)

---

## 1. Architecture Decision (Recommended)

### 1.1 Services
Use Docker Compose with 3 services:
1. **ollama** (official Ollama image)
2. **backend** (Python API server via Uvicorn, built from `backend/`)
3. **frontend** (Vue built to static files + served by Nginx)

### 1.2 Networking
- **Internal Docker network**: backend calls `http://ollama:11434`
- **Exposed ports**:
    - `frontend: 8080` → user-facing UI
    - `backend`: optional expose `8000` (only if you want direct API access)
    - `ollama`: optional expose `11434` (only if you want power users to hit it directly)

### 1.3 Configuration
- Centralized `.env` (compose + backend reads it)
- Backend must accept:
    - `OLLAMA_BASE_URL=http://ollama:11434`
    - `BACKEND_PORT=8000`
    - any provider API keys (OpenAI/Anthropic/etc.) if you support them

---

## 2. Implementation Milestones

### Milestone A — Backend Container (1 Dockerfile + healthcheck)
**Tasks**
- [ ] Add `backend/Dockerfile`
- [ ] Ensure backend binds to `0.0.0.0` (not `127.0.0.1`)
- [ ] Add a `/health` endpoint if you don’t have one
- [ ] Add `HEALTHCHECK` in Dockerfile or Compose

**Deliverables**
- `backend/Dockerfile`
- `backend/.dockerignore`
- Backend supports env var `OLLAMA_BASE_URL`

**Notes**
- If you use `requirements.txt`, install from it.
- If you use `pyproject.toml`, pick one toolchain (plain pip or uv/poetry) and lock it.

### Milestone B — Frontend Production Build (no "npm run dev" for users)
*Your README currently suggests running Vue dev server. For end users, that’s the wrong shape; we want static build.*

**Tasks**
- [ ] Confirm frontend uses environment-based API base URL:
    - For Vue Vite: `VITE_API_BASE_URL=/api` (then Nginx can proxy)
- [ ] Add `frontend/Dockerfile` (multi-stage build):
    - **build stage**: `npm ci && npm run build`
    - **serve stage**: Nginx serving `/usr/share/nginx/html`

**Deliverables**
- `frontend/Dockerfile`
- `frontend/nginx.conf` to:
    - serve static UI
    - proxy `/api` → `http://backend:8000`

### Milestone C — Docker Compose Orchestration (one command)
**Tasks**
- [ ] Add root `docker-compose.yml`
- [ ] Add volumes:
    - `ollama` data volume (persists models)
    - optional backend cache volume if needed

**Deliverables**
- `docker-compose.yml`
- `.env.example` (compose-ready)

**Recommended Compose features**
- `depends_on` + healthchecks to avoid race conditions:
    - backend waits for ollama healthy
    - frontend can start anytime, but API must be reachable

### Milestone D — First-Run Model Bootstrap (optional but huge UX win)
*Problem: user starts stack but no model is pulled yet.*

**Two good options**
1. Add a one-time init service in compose that runs:
   `ollama pull llama3` (or your default model)
2. Or backend detects missing model and triggers a pull (more complex)

**Deliverables**
- optional `init-ollama` service in compose
- docs: “first run will download model (~X GB)”

### Milestone E — One-Click Scripts + Release Packaging
*Even with Compose, users love a single entry point.*

**Tasks**
- [ ] Add:
    - `run.sh` (mac/linux)
    - `run.ps1` (Windows)
- [ ] Each script should:
    - check Docker exists
    - run `docker compose up -d --build`
    - print the UI URL
    - optionally auto-open browser

**Deliverables**
- `run.sh`, `run.ps1`
- `README-QuickStart.md` (3 steps max)

---

## 3. File Plan (What you’ll add)

**At repo root:**
- `docker-compose.yml`
- `.env.example` (compose-friendly)
- `run.sh`
- `run.ps1`
- `README-QuickStart.md`

**In `backend/`:**
- `Dockerfile`
- `.dockerignore`

**In `frontend/`:**
- `Dockerfile`
- `nginx.conf` (or `default.conf`)

---

## 4. Testing Plan (must-pass checks)

**Local**
- `docker compose up --build`
- Open UI, run an analysis request end-to-end

**Edge cases**
- Restart stack: models still present (ollama volume works)
- Backend can reach ollama by service name
- Windows path/line endings don’t break scripts

**Smoke checks**
- `curl http://localhost:8080` returns UI HTML
- `curl http://localhost:8080/api/health` returns OK (proxied)
- `curl http://localhost:11434/api/tags` (optional) shows models

---

## 5. Opinionated Recommendations (to avoid future pain)
1. **Don’t ship the Vue dev server to end users.** Always ship built static files behind Nginx.
2. **Keep a single public entrypoint**: the frontend port only.
3. **Treat Ollama as an internal dependency by default** (don’t expose 11434 unless you want it).
4. **Put all config into one .env file**; don’t make users edit multiple places.
