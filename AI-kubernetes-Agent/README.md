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

Expected health response:

```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

## Environment

Backend variables are documented in `backend/.env.example`:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
KUBECONFIG_PATH=
```

Frontend variables are documented in `frontend/.env.example`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
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
