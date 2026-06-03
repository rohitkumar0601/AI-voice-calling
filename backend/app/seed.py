"""Create tables and load seed data. Safe to run repeatedly:
it only seeds when the accounts table is empty.

    python -m app.seed
"""

from datetime import date

from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Account, Contact, Deal


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.scalar(select(Account).limit(1)):
            print("Data already present — skipping seed.")
            return

        db.add_all([
            Account(id="ACC-1", name="Northwind Logistics", industry="Transportation", tier="Enterprise"),
            Account(id="ACC-2", name="Bluepeak Health", industry="Healthcare", tier="Mid-market"),
            Account(id="ACC-3", name="Orchard & Vine", industry="Retail", tier="SMB"),
        ])
        db.add_all([
            Contact(id="CON-1", name="Maria Alvarez", title="VP Operations",
                    email="maria@northwind.com", phone="+1-415-555-0101", account_id="ACC-1"),
            Contact(id="CON-2", name="James Okoro", title="CFO",
                    email="james@bluepeak.health", phone="+1-415-555-0102", account_id="ACC-2"),
            Contact(id="CON-3", name="Priya Nair", title="Head of Procurement",
                    email="priya@northwind.com", phone="+1-415-555-0103", account_id="ACC-1"),
            Contact(id="CON-4", name="Tom Becker", title="Owner",
                    email="tom@orchardvine.com", phone="+1-415-555-0104", account_id="ACC-3"),
        ])
        db.add_all([
            Deal(id="DEAL-1", name="Northwind fleet rollout", account_id="ACC-1",
                 stage="Negotiation", amount=240000, probability=0.7,
                 close_date=date(2026, 7, 15), owner="Dana Reed"),
            Deal(id="DEAL-2", name="Bluepeak EHR integration", account_id="ACC-2",
                 stage="Proposal", amount=88000, probability=0.4,
                 close_date=date(2026, 8, 1), owner="Dana Reed"),
            Deal(id="DEAL-3", name="Orchard POS upgrade", account_id="ACC-3",
                 stage="Qualification", amount=19500, probability=0.2,
                 close_date=date(2026, 9, 10), owner="Sam Ito"),
            Deal(id="DEAL-4", name="Northwind support renewal", account_id="ACC-1",
                 stage="Closed Won", amount=60000, probability=1.0,
                 close_date=date(2026, 5, 20), owner="Sam Ito"),
        ])
        db.commit()
        print("Seeded accounts, contacts, and deals.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
