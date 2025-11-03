from flask import Flask, render_template, request, jsonify, session , url_for
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from datetime import datetime
import json
import urllib.parse

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Needed for Flask sessions
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1_vVNXOyuCYoAGt6bPHdbP1gJlXEInUcE-EnON0S9K_U"  # Your sheet ID

creds = None

try:
    # 1️⃣ Try to load OAuth token from Render environment
    token_env = os.getenv("GOOGLE_TOKEN")
    if token_env:
        token_json = urllib.parse.unquote(token_env)  # decode if stored encoded
        token_data = json.loads(token_json)

        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes"),
        )
        print("✅ Loaded OAuth credentials from environment variable (Render mode)")

    # 2️⃣ Fallback: use local token.json (for local dev)
    elif os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        print("✅ Loaded local token.json (Local mode)")

    # 3️⃣ If no token found, prompt OAuth login locally
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
        print("✅ Created new token.json from OAuth login (Local mode)")

    # Initialize Google Sheets client
    if creds:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    else:
        sheet = None
        print("⚠️ Google Sheets client not initialized")

except Exception as e:
    print("❌ Error loading Google credentials:", e)
    sheet = None


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
            data.get("q10")
        
        ]
        sheet.append_row(row)
        return jsonify({"status": "success" , "redirect": url_for("thankyou")})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(debug=True)
