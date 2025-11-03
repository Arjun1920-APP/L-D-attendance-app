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

# Local JSON files
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SPREADSHEET_ID = "1_vVNXOyuCYoAGt6bPHdbP1gJlXEInUcE-EnON0S9K_U"  # Replace with your actual sheet ID

# Authorize gspread client
creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
else:
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(creds.to_json())

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

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
