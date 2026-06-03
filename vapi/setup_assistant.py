"""Create or update the Vapi assistant from assistant.json.

    export VAPI_PRIVATE_KEY=sk_...
    export VAPI_SERVER_URL=https://<your-tunnel>/vapi/webhook
    python setup_assistant.py             # create
    python setup_assistant.py <id>        # update existing

Prints the assistant id -> put it in frontend/.env as VITE_VAPI_ASSISTANT_ID.
Vapi's API evolves; if a field is rejected, check https://docs.vapi.ai.
"""
import json, os, sys, requests

API = "https://api.vapi.ai/assistant"
KEY = os.environ["VAPI_PRIVATE_KEY"]
SERVER_URL = os.getenv("VAPI_SERVER_URL")

with open(os.path.join(os.path.dirname(__file__), "assistant.json")) as f:
    config = json.load(f)
if SERVER_URL:
    config["server"]["url"] = SERVER_URL

headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
if len(sys.argv) > 1:
    resp = requests.patch(f"{API}/{sys.argv[1]}", headers=headers, json=config)
else:
    resp = requests.post(API, headers=headers, json=config)
resp.raise_for_status()
print("Assistant id:", resp.json().get("id"))
print("Server URL :", config["server"]["url"])
