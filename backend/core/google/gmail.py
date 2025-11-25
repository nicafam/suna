import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

API_KEY = os.getenv("MCP_API_KEY")  # None = kein Auth
CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")

app = FastAPI()

def gmail_service():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

class InvokeRequest(BaseModel):
    tool: str
    args: dict = {}

def auth(api_key: str | None):
    if API_KEY and api_key != f"Bearer {API_KEY}":
        raise HTTPException(401, "unauthorized")


@app.api_route("/metadata", methods=["GET", "POST"])
def metadata():
    return {"name": "gmail-mcp", "version": "1.0.0", "capabilities": ["tools"]}


@app.api_route("/tools", methods=["GET", "POST"])
def tools():
    return {
        "tools": [
            {
                "name": "gmail_list_messages",
                "description": "List recent messages",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "default": ""},
                        "maxResults": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 10,
                        },
                    },
                },
            }
        ]
    }


@app.api_route("/", methods=["GET", "POST"])
def root():
    # Return metadata for convenience; avoids 404s when clients probe root
    return metadata()

@app.post("/invoke")
def invoke(req: InvokeRequest, authorization: str | None = Header(None)):
    auth(authorization)
    svc = gmail_service()
    if req.tool == "gmail_list_messages":
        data = svc.users().messages().list(userId="me", q=req.args.get("q", ""), maxResults=req.args.get("maxResults", 10)).execute()
        return {"result": data.get("messages", [])}
    raise HTTPException(400, "unknown tool")
