# get_refresh_token.py
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os, json

# CLIENT_ID = "1030575266366-59deg5mbdvcvi8e9mrgv9g2mho0tfu9v.apps.googleusercontent.com"
# CLIENT_SECRET = "<CLIENT_SECRET>"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]  # or gmail.modify if needed

client_file = os.environ["GOOGLE_OAUTH_CLIENT_FILE"]
with open(client_file) as f:
    client_config = json.load(f)

def main():
    flow = InstalledAppFlow.from_client_config(client_config,
        scopes=SCOPES,
    )
    creds = flow.run_local_server(port=0, prompt="consent")
    # force refresh to ensure refresh_token is present
    creds.refresh(Request())
    print("Access Token:", creds.token)
    print("Refresh Token:", creds.refresh_token)

if __name__ == "__main__":
    main()
