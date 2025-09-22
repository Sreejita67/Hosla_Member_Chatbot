import pandas as pd
import bcrypt
import requests
import io
import re
import gspread
from google.oauth2.service_account import Credentials

# Google Sheet (public CSV link for read)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8IArJoxgQ2EL2fQJn_rUVozWqJbz-n0Qn42rTMDHHZezCbn5MEa-0TcvRfPiEGPyDj3W96LkRFwSH/pub?gid=19136775&single=true&output=csv"

# Spreadsheet info
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1fEdv8-ky0jc2_RshMQclRP_U8kcxSRkIcj8BGXzXXSA/edit"
WORKSHEET_NAME = "Hosla Member Details"

# Service account credentials
SERVICE_ACCOUNT_FILE = "hosla-creds.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    # ✅ Open spreadsheet by URL and select worksheet
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
except FileNotFoundError:
    sheet = None  # Fallback if creds missing
    print("⚠️ hosla-472907-c7d47bfcd616.json not found, running in READ-only mode")

def load_sheet():
    """Fetch Google Sheet as DataFrame using gspread to preserve exact data."""
    if sheet is None:
        # fallback to CSV public link (read-only)
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))

    # ✅ Use raw values to avoid gspread's automatic conversions
    raw_data = sheet.get_all_values()
    headers = raw_data[0]
    rows = raw_data[1:]
    return pd.DataFrame(rows, columns=headers)

def authenticate_user(username, password, debug=False):
    df = load_sheet()

    username = str(username).strip().lower()
    df_username_series = df["Username"].astype(str).str.strip().str.lower()
    matches = df[df_username_series == username]

    if matches.empty:
        if debug:
            print(f"DEBUG: username '{username}' not found.")
        return None

    row = matches.iloc[0]
    stored_val = row.get("Password", "")

    if debug:
        print(f"DEBUG: Raw stored_val repr: {repr(stored_val)}")

    if pd.isna(stored_val):
        if debug:
            print("DEBUG: Stored password is NaN/empty.")
        return None

    # Clean and strip hash
    stored_hash = str(stored_val).strip().strip('"').strip("'")
    stored_hash = "".join(stored_hash.split())  # remove whitespace/newlines
    stored_hash = re.sub(r"[^\x20-\x7E]", "", stored_hash)  # remove hidden chars

    if debug:
        print(f"DEBUG: Cleaned stored_hash repr: {repr(stored_hash)}")
        print(f"DEBUG: Cleaned hash length: {len(stored_hash)}")

    if len(stored_hash) != 60 and stored_hash.startswith("$2b$"):
        print("⚠️ WARNING: Hash length is not 60 — Google Sheets may have corrupted the value.")

    if stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
        try:
            if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                if debug:
                    print("DEBUG: bcrypt.checkpw -> True (login successful)")
                return row.to_dict()
            else:
                if debug:
                    print("DEBUG: bcrypt.checkpw -> False (password mismatch)")
                return None
        except ValueError as e:
            if debug:
                print(f"DEBUG: bcrypt.checkpw ValueError: {e}")
            return None
    else:
        # fallback plaintext
        return row.to_dict() if stored_hash == password else None


def register_user(full_name, age, role, interests, locality, city, pin_code,
                  contact_no, email, dob, username, password,
                  profile_picture="", active="Yes"):
    if sheet is None:
        raise RuntimeError("❌ Cannot register: hosla-472907-c7d47bfcd616.json missing!")

    # ✅ Validate mobile number
    if not is_valid_mobile(contact_no):
        print(f"❌ Invalid mobile number '{contact_no}'. Must be 10 digits starting with 6-9.")
        return False

    # ✅ Validate email
    if not is_valid_email(email):
        print(f"❌ Invalid email address '{email}'.")
        return False

    # ✅ Normalize username
    username = str(username).strip().lower()

    # ✅ Check duplicate username
    df = load_sheet()
    if username in df["Username"].astype(str).str.lower().values:
        print(f"⚠️ Username '{username}' already exists. Choose another.")
        return False

    # ✅ Hash password and self-check
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    if not bcrypt.checkpw(password.encode(), hashed_pw.encode()):
        raise ValueError("❌ Hash verification failed after generation!")

    new_row = [
        full_name, age, role, interests, locality, city, pin_code,
        active, profile_picture, contact_no, email, dob, username, hashed_pw
    ]

    sheet.append_row(new_row, value_input_option="RAW")
    print(f"✅ User {full_name} registered successfully with username '{username}'")
    return True

# Example usage
if __name__ == "__main__":
    # Example Register
    # register_user("Rina Das", 21, "Member", "Dance, Music", "Salt Lake", "Kolkata", "700091",
    #               "9876543210", "rina@example.com", "29-10-2004", "rina_d", "mypassword")

    # Example Login
    user = authenticate_user("rina_d", "mypassword")
    if user:
        print(f"✅ Welcome {user['Member Name']} ({user['Role']})")
    else:
        print("❌ Invalid login")
