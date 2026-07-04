# Project Setup Notes

This repository currently contains the foundation for the AI Kubernetes Troubleshooting Agent.

Implemented:

- FastAPI backend with `GET /health`
- `POST /investigate` Kubernetes evidence collection endpoint
- Backend CORS, logging, and environment-based settings
- Backend modules for API, core, Kubernetes, AI, services, and models
- Next.js frontend with TypeScript, Tailwind CSS, Axios, and React Query
- Placeholder frontend modules for components, services, hooks, and types
- Dockerfiles for backend and frontend
- Docker Compose wiring for ports `8000` and `3000`
- Kubectl-based inspectors for pods, logs, events, deployments, services, and endpoints

Deferred:

- AI reasoning and OpenRouter integration
- InsForge backend features
- Authentication
- Realtime updates
