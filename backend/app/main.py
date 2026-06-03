"""FastAPI backend — serves the React dashboard over REST and handles
Vapi voice-agent tool calls, all backed by Postgres.

    uvicorn app.main:app --reload --port 8000
"""

import json

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud
from .config import CORS_ORIGINS, VAPI_SERVER_SECRET
from .database import get_db
from .models import Account, Contact, Deal
from .seed import seed

app = FastAPI(title="Atlas CRM — voice backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    # Create tables + seed on boot so `docker compose up` just works.
    seed()


# Map Vapi tool names to query functions. Read-only by design.
TOOLS = {
    "find_contact": crud.find_contact,
    "get_deal": crud.get_deal,
    "list_deals": crud.list_deals,
    "pipeline_summary": crud.pipeline_summary,
    "account_overview": crud.account_overview,
}


def _extract_tool_calls(message: dict):
    """Tolerant of Vapi payload-shape drift across API versions."""
    calls = message.get("toolCallList") or message.get("toolCalls")
    if calls:
        out = []
        for c in calls:
            fn = c.get("function", {})
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            out.append({"id": c.get("id"), "name": fn.get("name"), "args": args})
        return out
    fc = message.get("functionCall")  # legacy shape
    if fc:
        return [{"id": None, "name": fc.get("name"), "args": fc.get("parameters", {})}]
    return []


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    if VAPI_SERVER_SECRET and request.headers.get("x-vapi-secret") != VAPI_SERVER_SECRET:
        return {"error": "unauthorized"}

    body = await request.json()
    message = body.get("message", {})
    msg_type = message.get("type")
    if msg_type not in ("tool-calls", "function-call"):
        return {}  # ack status-update / transcript / end-of-call-report / etc.

    results = []
    for call in _extract_tool_calls(message):
        impl = TOOLS.get(call["name"])
        try:
            result = impl(db, **call["args"]) if impl else {"error": f"unknown tool {call['name']}"}
        except TypeError as e:
            result = {"error": f"bad arguments for {call['name']}: {e}"}
        results.append({"toolCallId": call["id"], "name": call["name"], "result": result})

    if msg_type == "function-call" and results:
        return {"result": results[0]["result"]}
    return {"results": results}


# --- REST for the React dashboard ------------------------------------------

@app.get("/api/accounts")
def accounts(db: Session = Depends(get_db)):
    return [
        {"id": a.id, "name": a.name, "industry": a.industry, "tier": a.tier}
        for a in db.query(Account).all()
    ]


@app.get("/api/contacts")
def contacts(db: Session = Depends(get_db)):
    return [
        {"id": c.id, "name": c.name, "title": c.title, "email": c.email,
         "phone": c.phone, "account": c.account.name}
        for c in db.query(Contact).all()
    ]


@app.get("/api/deals")
def deals(db: Session = Depends(get_db)):
    return [
        {"id": d.id, "name": d.name, "account": d.account.name, "stage": d.stage,
         "amount": d.amount, "owner": d.owner, "close_date": d.close_date.isoformat()}
        for d in db.query(Deal).all()
    ]


@app.get("/api/pipeline")
def pipeline(db: Session = Depends(get_db)):
    return crud.pipeline_summary(db)


@app.get("/health")
def health():
    return {"ok": True}
