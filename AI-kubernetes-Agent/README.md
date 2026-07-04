# AI Kubernetes Agent

An on-demand Kubernetes troubleshooting product: investigate real cluster failures, reason with AI, and view diagnoses in a protected dashboard.

## Architecture

```text
Frontend
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
LLM Reasoning (OpenRouter)
    ↓
Root Cause + Suggested Fix
    ↓
InsForge (Auth + History + Realtime)
    ↓
Frontend Diagnosis
```

## Features

- InsForge authentication (signup, login, email verification)
- Cluster picker — lists all contexts from your local kubeconfig
- One-click investigation with progress steps and realtime updates
- AI diagnosis via OpenRouter with rule-based fallback
- Investigation history persisted in InsForge
- Beginner-friendly error messages for kubectl, cluster, and API failures
- Test scenarios for CrashLoopBackOff, ImagePullBackOff, OOMKilled, and service selector mismatch

## Project Structure

```text
AI-kubernetes-Agent/
├── backend/
├── frontend/
├── docs/
├── test-scenarios/
├── docker-compose.yml
└── README.md
```

## Run with Docker

From this folder:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Set OPENROUTER_API_KEY in backend/.env
docker compose up --build
```

Docker mounts `~/.kube` into the backend so all clusters in your kubeconfig appear in the dashboard.

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health

### End-to-end workflow

```text
Login → Select cluster → Investigate Cluster
    → kubectl evidence → AI reasoning → diagnosis + history
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Service health |
| GET | `/clusters` | Yes | List kubeconfig contexts |
| POST | `/investigate` | Yes | Investigate selected cluster (`{ "context": "..." }`) |

## Test Real Kubernetes Failures

See `test-scenarios/README.md` for four intentional failure manifests:

1. CrashLoopBackOff — missing environment variable
2. ImagePullBackOff — wrong image tag
3. OOMKilled — low memory limits
4. Service selector mismatch

```bash
kubectl apply -f test-scenarios/01-crashloop-missing-env.yaml
# Investigate in dashboard, then clean up
kubectl delete namespace agent-test
```

## Environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Backend (`backend/.env`):

```env
INSFORGE_API_BASE_URL=https://wznstw3m.eu-central.insforge.app
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4o-mini
KUBECONFIG_PATH=
```

Frontend (`frontend/.env.local`):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_INSFORGE_BASE_URL=https://wznstw3m.eu-central.insforge.app
NEXT_PUBLIC_INSFORGE_ANON_KEY=
```

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Ensure your kubeconfig is available to the backend process (`~/.kube/config` or `KUBECONFIG_PATH`).
