from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

# ----------------- Config -----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "credentials.json"  # Your OAuth client JSON
TOKEN_FILE = "token.json"              # Will be created after authorization

# ----------------- OAuth Flow -----------------
def main():
    # Check if credentials.json exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found in project folder!")
        return

    # Run the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials as JSON
    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(creds.to_json())

    print(f"OAuth successful! {TOKEN_FILE} created.")

if __name__ == "__main__":
    main()
