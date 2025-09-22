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
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
except FileNotFoundError:
    sheet = None  # Fallback if creds missing
    print("⚠️ hosla-472907-c7d47bfcd616.json not found, running in READ-only mode")

# -----------------------------
# Helpers
# -----------------------------
def is_valid_mobile(mobile):
    """Validate Indian mobile numbers (10 digits, starts with 6-9)."""
    return bool(re.fullmatch(r"[6-9]\d{9}", str(mobile).strip()))

def is_valid_email(email):
    """Basic email validation using regex."""
    return bool(re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email.strip()))

def load_sheet():
    """Fetch Google Sheet as DataFrame using gspread to preserve exact data."""
    if sheet is None:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))

    raw_data = sheet.get_all_values()
    headers = raw_data[0]
    rows = raw_data[1:]
    return pd.DataFrame(rows, columns=headers)

# -----------------------------
# Authentication
# -----------------------------
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

    stored_hash = str(stored_val).strip().strip('"').strip("'")
    stored_hash = "".join(stored_hash.split())  # remove whitespace/newlines
    stored_hash = re.sub(r"[^\x20-\x7E]", "", stored_hash)  # remove hidden chars

    if debug:
        print(f"DEBUG: Cleaned stored_hash repr: {repr(stored_hash)}")
        print(f"DEBUG: Cleaned hash length: {len(stored_hash)}")

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

# -----------------------------
# Registration
# -----------------------------
def register_user(full_name, age, role, interests, locality, city, pin_code,
                  contact_no, email, dob, username, password,
                  profile_picture="", active="Yes"):
    if sheet is None:
        raise RuntimeError("❌ Cannot register: hosla-472907-c7d47bfcd616.json missing!")

    if not is_valid_mobile(contact_no):
        print(f"❌ Invalid mobile number '{contact_no}'. Must be 10 digits starting with 6-9.")
        return False

    if not is_valid_email(email):
        print(f"❌ Invalid email address '{email}'.")
        return False

    username = str(username).strip().lower()

    df = load_sheet()
    if username in df["Username"].astype(str).str.lower().values:
        print(f"⚠️ Username '{username}' already exists. Choose another.")
        return False

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

# -----------------------------
# Password Reset
# -----------------------------
def reset_password(username, old_password):
    """
    Reset password for an existing user after verifying old password.
    Asks user to confirm new password before saving.
    """
    df = load_sheet()
    username = str(username).strip().lower()
    df_username_series = df["Username"].astype(str).str.strip().str.lower()
    matches = df[df_username_series == username]

    if matches.empty:
        print(f"❌ Username '{username}' not found.")
        return False

    row_idx = matches.index[0]
    row = matches.iloc[0]
    stored_val = row.get("Password", "")

    if pd.isna(stored_val) or not str(stored_val).strip():
        print("❌ Stored password missing or invalid.")
        return False

    stored_hash = str(stored_val).strip().strip('"').strip("'")
    stored_hash = "".join(stored_hash.split())
    stored_hash = re.sub(r"[^\x20-\x7E]", "", stored_hash)

    if stored_hash.startswith(("$2b$", "$2a$", "$2y$")):
        if not bcrypt.checkpw(old_password.encode(), stored_hash.encode()):
            print("❌ Old password is incorrect.")
            return False
    else:
        if stored_hash != old_password:
            print("❌ Old password is incorrect.")
            return False

    new_password = input("Enter your new password: ")
    confirm_password = input("Confirm your new password: ")

    if new_password != confirm_password:
        print("❌ Passwords do not match. Try again.")
        return False

    if len(new_password) < 6:
        print("⚠️ Password too short. Use at least 6 characters.")
        return False

    new_hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()

    sheet.update_cell(row_idx + 2, df.columns.get_loc("Password") + 1, new_hashed_pw)
    print(f"✅ Password updated successfully for '{username}'.")
    return True

# Example usage
if __name__ == "__main__":
    user = authenticate_user("rina_d", "mypassword")
    if user:
        print(f"✅ Welcome {user['Member Name']} ({user['Role']})")
    else:
        print("❌ Invalid login")
