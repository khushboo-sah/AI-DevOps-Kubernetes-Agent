# AI Kubernetes Agent

An on-demand troubleshooting foundation for investigating Kubernetes issues with a FastAPI orchestrator and a Next.js frontend.

This setup intentionally does not include Kubernetes inspection, AI reasoning, OpenRouter calls, InsForge data features, authentication, or realtime updates yet.

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
LLM Reasoning (OpenRouter via InsForge)
    ↓
Root Cause + Suggested Fix
    ↓
Frontend Diagnosis
```

## Project Structure

```text
AI-kubernetes-Agent/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── kubernetes/
│       ├── ai/
│       ├── services/
│       └── models/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   └── types/
├── docs/
├── prompts/
├── docker-compose.yml
└── README.md
```

## Run with Docker

From this folder:

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- Kubernetes investigation and diagnosis: `POST http://localhost:8000/investigate`

Expected health response:

```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

Example investigation request:

```bash
curl -X POST http://localhost:8000/investigate
```

The investigation endpoint uses `kubectl` internally to collect evidence from
the active Kubernetes context, then sends that evidence to the AI Kubernetes
Agent for Senior SRE-style diagnosis. OpenRouter credentials are read from
environment variables and are never hardcoded. If no cluster, kubeconfig, or
OpenRouter key is available, the response still returns structured evidence and
a fallback diagnosis with error details.

The frontend dashboard uses InsForge for:

- Authentication and session handling
- Realtime investigation progress events
- Recent investigation history stored in the `investigations` table
- Persisted progress steps stored in the `investigation_progress` table

## Environment

Copy the example files and fill in secrets before running locally or with Docker:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Set `OPENROUTER_API_KEY` in `backend/.env` for AI diagnosis. Docker Compose loads `backend/.env` automatically.

Backend variables are documented in `backend/.env.example`:

```env
INSFORGE_API_BASE_URL=https://wznstw3m.eu-central.insforge.app
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
KUBECONFIG_PATH=
```

Frontend variables are documented in `frontend/.env.example`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_INSFORGE_BASE_URL=https://wznstw3m.eu-central.insforge.app
NEXT_PUBLIC_INSFORGE_ANON_KEY=anon_c2b40b3499dce755117cd876b8f3e418df36fb323173b5358435d10f732c35fa
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
