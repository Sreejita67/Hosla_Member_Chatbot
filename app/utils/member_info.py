import pandas as pd
from datetime import datetime
from pytz import timezone
import os

# ✅ Public Google Sheet CSV URL (Replace with yours)
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8IArJoxgQ2EL2fQJn_rUVozWqJbz-n0Qn42rTMDHHZezCbn5MEa-0TcvRfPiEGPyDj3W96LkRFwSH/pub?gid=19136775&single=true&output=csv"

def greet_user_and_show_active_members(img_dir: str, username: str):
    print("🔄 Loading member data from Google Sheet...")
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL, dtype=str).fillna("")

    # Data cleaning
    df["Member Name"] = df["Member Name"].str.strip()
    df["Active"] = df["Active"].str.strip()
    df["Profile Picture"] = df["Profile Picture"].str.strip()
    df["Member Name Lower"] = df["Member Name"].str.lower()

    username_clean = username.strip().lower()
    matched_user = df[df["Member Name Lower"] == username_clean]

    if matched_user.empty:
        return f"❌ No user found with the name: {username}", None, []

    user_info = matched_user.iloc[0]
    hour = datetime.now(timezone('Asia/Kolkata')).hour
    greeting = ("Good morning" if hour < 12 else
                "Good afternoon" if hour < 17 else
                "Good evening" if hour < 20 else
                "Good night")

    greeting_msg = (
        f"{greeting}, {user_info['Member Name']} \n"
        f"Age: {user_info['Age']} | City: {user_info['City']} | Role: {user_info['Role']}"
    )

    pic_filename = user_info.get("Profile Picture", "").strip()
    pic_path = None
    if pic_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        potential_path = os.path.join(img_dir, pic_filename)
        if os.path.exists(potential_path):
            pic_path = potential_path

    active_df = df[df["Active"].str.lower() == "yes"]
    active_members = [
        f"{row['Member Name']} – {row['City']} interested in {row['Interests']}"
        for _, row in active_df.iterrows()
    ]

    return greeting_msg, pic_path, active_members
