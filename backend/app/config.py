import os

# Postgres connection. In Docker Compose this points at the "db" service;
# locally it defaults to a Postgres on localhost.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://crm:crm@localhost:5432/crm",
)

# Optional shared secret for authenticating Vapi webhook requests.
VAPI_SERVER_SECRET = os.getenv("VAPI_SERVER_SECRET")

# CORS: comma-separated list of allowed frontend origins ("*" allows all).
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
