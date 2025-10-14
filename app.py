from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.credentials import Credentials
import os
import json
from datetime import datetime

app = Flask(__name__)

# ---------------- Google Sheets setup ----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ---------------- Load Credentials from Environment Variables ----------------
credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
token_json = os.environ.get("GOOGLE_TOKEN_JSON")
SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID")

if not credentials_json or not token_json or not SPREADSHEET_ID:
    raise Exception(
        "Missing environment variables: GOOGLE_CREDENTIALS_JSON, GOOGLE_TOKEN_JSON, or GOOGLE_SHEET_ID."
    )

# Convert JSON strings to Python dicts
# credentials_json is kept for completeness if needed by other flows, but we use token_json for authorized creds
credentials_dict = json.loads(credentials_json)
token_dict = json.loads(token_json)

# Authorize gspread client using the token info
creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ---------------- Routes ----------------
@app.route("/")
def index():
    session_name = request.args.get("session", "L&D Session")
    return render_template("index.html", session=session_name)

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
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(debug=True)
