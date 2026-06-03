"""Read-only query functions. Both the REST API and the Vapi voice tools
call these, so the dashboard and the voice agent always agree.

Each returns plain JSON-serializable dicts.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import OPEN_STAGES, Account, Contact, Deal


def _ilike(col, value):
    return col.ilike(f"%{value.strip()}%")


def find_contact(db: Session, name: str) -> dict:
    rows = db.scalars(select(Contact).where(_ilike(Contact.name, name))).all()
    if not rows:
        return {"found": False, "message": f"No contact matching '{name}'."}
    c = rows[0]
    open_deals = db.scalars(
        select(Deal).where(Deal.account_id == c.account_id, Deal.stage.in_(OPEN_STAGES))
    ).all()
    return {
        "found": True,
        "name": c.name, "title": c.title, "email": c.email, "phone": c.phone,
        "account": c.account.name,
        "open_deals": [{"name": d.name, "stage": d.stage, "amount": d.amount} for d in open_deals],
        "ambiguous": len(rows) > 1,
    }


def get_deal(db: Session, name: str) -> dict:
    rows = db.scalars(select(Deal).where(_ilike(Deal.name, name))).all()
    if not rows:
        return {"found": False, "message": f"No deal matching '{name}'."}
    d = rows[0]
    return {
        "found": True,
        "name": d.name, "account": d.account.name, "stage": d.stage,
        "amount": d.amount, "probability": d.probability,
        "close_date": d.close_date.isoformat(), "owner": d.owner,
    }


def list_deals(db: Session, stage: str = None, owner: str = None, open_only: bool = False) -> dict:
    stmt = select(Deal)
    if stage:
        stmt = stmt.where(_ilike(Deal.stage, stage))
    if owner:
        stmt = stmt.where(_ilike(Deal.owner, owner))
    if open_only:
        stmt = stmt.where(Deal.stage.in_(OPEN_STAGES))
    rows = db.scalars(stmt).all()
    return {
        "count": len(rows),
        "deals": [
            {"name": d.name, "account": d.account.name, "stage": d.stage,
             "amount": d.amount, "owner": d.owner}
            for d in rows
        ],
    }


def pipeline_summary(db: Session) -> dict:
    rows = db.execute(
        select(Deal.stage, func.count(), func.sum(Deal.amount))
        .where(Deal.stage.in_(OPEN_STAGES))
        .group_by(Deal.stage)
    ).all()
    by_stage = {stage: {"count": cnt, "amount": int(amt or 0)} for stage, cnt, amt in rows}

    weighted = db.scalar(
        select(func.coalesce(func.sum(Deal.amount * Deal.probability), 0.0))
        .where(Deal.stage.in_(OPEN_STAGES))
    )
    return {
        "open_total": sum(s["amount"] for s in by_stage.values()),
        "weighted_forecast": round(weighted or 0),
        "by_stage": by_stage,
    }


def account_overview(db: Session, name: str) -> dict:
    rows = db.scalars(select(Account).where(_ilike(Account.name, name))).all()
    if not rows:
        return {"found": False, "message": f"No account matching '{name}'."}
    a = rows[0]
    return {
        "found": True,
        "name": a.name, "industry": a.industry, "tier": a.tier,
        "contacts": [{"name": c.name, "title": c.title} for c in a.contacts],
        "open_value": sum(d.amount for d in a.deals if d.stage in OPEN_STAGES),
        "deals": [{"name": d.name, "stage": d.stage, "amount": d.amount} for d in a.deals],
    }
