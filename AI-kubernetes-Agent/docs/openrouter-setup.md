# How to Get an OpenRouter API Key

The AI Kubernetes Agent uses [OpenRouter](https://openrouter.ai/) to run LLM reasoning (root cause analysis, suggested fixes). You need an API key in `backend/.env`.

> **Note:** Project prompts mention "OpenRouter via InsForge." InsForge handles **auth, database, and realtime** in this app. The OpenRouter key is still set manually in `backend/.env` today — it is not auto-fetched from InsForge.

## Step 1 — Create an OpenRouter account

1. Open [https://openrouter.ai](https://openrouter.ai)
2. Sign up (Google, GitHub, or email)

## Step 2 — Add credits (if required)

1. Go to [https://openrouter.ai/credits](https://openrouter.ai/credits)
2. Add a small balance (many models have free tiers; `openai/gpt-4o-mini` is inexpensive)

## Step 3 — Create an API key

1. Open [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Click **Create Key**
3. Copy the key — it starts with `sk-or-v1-...`
4. Store it somewhere safe; you may not see it again

## Step 4 — Add the key to this project

```bash
cd AI-kubernetes-Agent
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-paste-your-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

## Step 5 — Restart the backend

```bash
docker compose down
docker compose up --build
```

Check logs for:

```text
OpenRouter API key is configured
```

## Without a key

The app still works. Investigations run, but diagnosis uses **rule-based fallback** instead of AI. You will see:

```text
AI reasoning is unavailable because OPENROUTER_API_KEY is not configured
```

## Keys used in this project

| Key | Where | Purpose |
|-----|-------|---------|
| `OPENROUTER_API_KEY` | `backend/.env` | AI diagnosis (OpenRouter) |
| `NEXT_PUBLIC_INSFORGE_ANON_KEY` | `frontend/.env.local` | Login/signup (InsForge) |
| InsForge session token | Browser after login | Backend API auth |

These are different keys for different services.
