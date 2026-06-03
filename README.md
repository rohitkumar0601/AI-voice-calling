# Atlas CRM — voice agent (React + FastAPI + Postgres + Vapi)

A sales-CRM voice assistant. You talk to it in the browser; it answers
questions about contacts, deals, and the pipeline by calling a FastAPI
backend that reads **PostgreSQL**. The same backend serves the React
dashboard, so the voice agent and the UI never disagree.

```
Browser mic ──voice──▶ Vapi ──webhook──▶ FastAPI ──SQL──▶ PostgreSQL
                                            ▲
React dashboard ───────── REST / JSON ──────┘
```

Scope: **CRM / sales, query-only, in-browser.** The agent can look things up
but intentionally cannot create or change records.

---

## Quickstart (Docker)

```bash
cp .env.example .env        # optional: add your Vapi keys for live voice
docker compose up --build
```

This starts three services:

| Service  | URL                     | Notes                              |
|----------|-------------------------|------------------------------------|
| db       | localhost:5432          | Postgres 16 (crm / crm / crm)      |
| backend  | http://localhost:8000   | FastAPI; auto-creates + seeds tables |
| frontend | http://localhost:5173   | React dashboard                    |

Open http://localhost:5173. The dashboard works immediately. The **Talk to
CRM** button is enabled once Vapi keys are set (see below).

---

## Enabling live voice

Voice audio runs **browser ↔ Vapi cloud**. Only the *tool-call webhook* needs
your backend to be reachable from Vapi's servers, so during local dev expose
it with a tunnel:

```bash
ngrok http 8000             # gives https://<id>.ngrok.app
```

Then register the assistant (its tools point at your webhook):

```bash
cd vapi
export VAPI_PRIVATE_KEY=sk_...                       # Vapi private key
export VAPI_SERVER_URL=https://<id>.ngrok.app/vapi/webhook
pip install requests
python setup_assistant.py                            # prints the assistant id
```

Put the **public** key and the printed **assistant id** in `.env`:

```
VITE_VAPI_PUBLIC_KEY=pk_...
VITE_VAPI_ASSISTANT_ID=...
```

Restart `docker compose up`, click **Talk to CRM**, allow the mic, and try:

- "What's the status of the Northwind fleet deal?"
- "Give me the pipeline summary."
- "Who is Maria Alvarez?"
- "List the deals in negotiation."

---

## Running without Docker

**Backend**
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://crm:crm@localhost:5432/crm
uvicorn app.main:app --reload --port 8000      # creates + seeds tables on boot
```

**Frontend**
```bash
cd frontend
cp .env.example .env        # fill in keys
npm install
npm run dev                 # http://localhost:5173
```

---

## Project layout

```
backend/app/
  config.py     env (DATABASE_URL, CORS, optional webhook secret)
  database.py   SQLAlchemy engine + session
  models.py     Account / Contact / Deal ORM models
  crud.py       read-only query functions (shared by REST + voice)
  seed.py       create tables + idempotent seed
  main.py       FastAPI: /vapi/webhook + /api/* endpoints
frontend/src/
  App.jsx        dashboard (pipeline, deals, contacts)
  VoiceAgent.jsx Vapi web SDK: call control + live transcript
  api.js         REST client
vapi/
  assistant.json system prompt + tool schemas
  setup_assistant.py  push the assistant to Vapi
docker-compose.yml  db + backend + frontend
```

## Notes

- The webhook handles both the current Vapi `tool-calls` payload and the
  legacy `function-call` shape. Vapi's API evolves — if a field is rejected,
  check https://docs.vapi.ai and adjust `assistant.json` / the handler.
- Set `VAPI_SERVER_SECRET` on the backend and the matching secret on the Vapi
  assistant to authenticate webhook calls in production.
- **Adding write actions** (create a deal, log a call) = add a tool to
  `assistant.json`, a function to `crud.py`, and an entry to the `TOOLS` map
  in `main.py` — plus real auth, since voice could then mutate data.
- Tighten `CORS_ORIGINS` to your real frontend origin before deploying.
```
