from flask import Flask, render_template, request, jsonify, session , url_for
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from datetime import datetime

import json

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Needed for Flask sessions

# ---------------- Google Sheets setup ----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1_vVNXOyuCYoAGt6bPHdbP1gJlXEInUcE-EnON0S9K_U"  # Your sheet ID

import urllib.parse

# Try to load credentials from environment variables (for Render)
credentials_env = os.getenv("GOOGLE_CREDENTIALS")
token_env = os.getenv("GOOGLE_TOKEN")

creds = None

try:
    if credentials_env:
        # If stored as URL-encoded JSON in Render, decode it
        credentials_json = urllib.parse.unquote(credentials_env)
        creds_data = json.loads(credentials_json)
        from google.oauth2.service_account import Credentials as ServiceAccountCredentials
        creds = ServiceAccountCredentials.from_service_account_info(creds_data, scopes=SCOPES)
        print("✅ Loaded credentials from environment variables (Render mode)")
    elif os.path.exists("token.json"):
        # Fallback for local mode
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        print("✅ Loaded credentials from local token.json (Local mode)")
    else:
        # Local flow for first-time auth
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
        print("✅ New token.json created (Local mode)")
except Exception as e:
    print("❌ Error loading Google credentials:", e)

# Initialize Google Sheets client
if creds:
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
else:
    sheet = None
    print("⚠️ Google Sheets client not initialized")


# ---------------- Routes ----------------
@app.route("/")
def index():
    session_name = request.args.get("session", "L&D Session")
    return render_template("index.html", session=session_name)

@app.route("/thankyou")
def thankyou():
    name = session.pop("user_name", "Participant")
    return render_template("thankyou.html", name=name)

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Store user name in session
    session["user_name"] = data.get("name")  

    try:

        # Prepare row to append to Google Sheet
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
            data.get("name"),
            data.get("email"),
            data.get("phone"),
            data.get("session"),
            data.get("q1"),
            data.get("q2"),
            data.get("q3"),
            data.get("q4"),
            data.get("q5"),
            data.get("q6"),
            data.get("q7"),
            data.get("q8"),
            data.get("q9"),
            data.get("q10"),
            data.get("q11"),
            data.get("q12")
        ]
        sheet.append_row(row)
        return jsonify({"status": "success" , "redirect": url_for("thankyou")})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(debug=True)
