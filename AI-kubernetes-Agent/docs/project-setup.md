# Project Setup Notes

This repository currently contains the foundation for the AI Kubernetes Troubleshooting Agent.

Implemented:

- FastAPI backend with `GET /health`
- `POST /investigate` Kubernetes evidence collection and diagnosis endpoint
- Backend CORS, logging, and environment-based settings
- Backend modules for API, core, Kubernetes, AI, services, and models
- Next.js frontend with TypeScript, Tailwind CSS, Axios, and React Query
- Frontend dashboard modules for components, services, hooks, and types
- InsForge authentication for the protected dashboard
- InsForge realtime progress events during investigations
- InsForge investigation history table with user-scoped RLS policies
- Dockerfiles for backend and frontend
- Docker Compose wiring for ports `8000` and `3000`
- Kubectl-based inspectors for pods, logs, events, deployments, services, and endpoints
- AI Kubernetes Agent with prompt building, OpenRouter client, fallback root-cause analysis, fix recommendations, and confidence scoring

Deferred:

- Advanced investigation history filtering
- Charts and analytics
