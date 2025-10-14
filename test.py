from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle
from datetime import datetime

app = Flask(__name__)

# ---------------- Google Sheets setup ----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# OAuth2 token handling
creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

client = gspread.authorize(creds)

# Your spreadsheet ID (replace with yours!)
SPREADSHEET_ID = "1_vVNXOyuCYoAGt6bPHdbP1gJlXEInUcE-EnON0S9K_U"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ---------------- Routes ----------------

@app.route("/")
def index():
    return render_template("index.html", session="Arjun Feedback Session")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    try:
        # Match your GSheet structure
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
            data.get("name"),
            data.get("email"),
            data.get("phone"),
            "L&D Feedback Session",  # Default session name
            data.get("q1"),
            data.get("q2"),
            data.get("q3"),
            data.get("q4")
        ]
        sheet.append_row(row)
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(debug=True)
