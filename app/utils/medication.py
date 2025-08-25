import pandas as pd
import os
from datetime import datetime
from pytz import timezone
from app.utils import config

MEDICATION_PATH = os.path.join(config.BASE_DIR, "medication_schedule.csv")

def load_schedule():
    if not os.path.exists(MEDICATION_PATH):
        df = pd.DataFrame(columns=["Member Name", "Medicine", "Time", "Dosage", "Status"])
        df.to_csv(MEDICATION_PATH, index=False)
    return pd.read_csv(MEDICATION_PATH)

def save_schedule(df):
    df.to_csv(MEDICATION_PATH, index=False)

def add_reminder(current_user):
    med = input("Medicine name: ").strip()
    time_str = input("Time to take (HH:MM, 24-hr format): ").strip()
    dosage = input("Dosage: ").strip()

    df = load_schedule()
    new_entry = pd.DataFrame([{
        "Member Name": current_user,
        "Medicine": med,
        "Time": time_str,
        "Dosage": dosage,
        "Status": "Pending"
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    save_schedule(df)
    print("✅ Reminder added successfully!")

def check_reminders():
    tz = timezone('Asia/Kolkata')
    now = datetime.now(tz)  # timezone-aware datetime
    df = load_schedule()

    any_reminder = False
    for idx, row in df.iterrows():
        # Parse reminder time and make it timezone-aware
        reminder_time = tz.localize(datetime.strptime(row["Time"], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        ))

        # If current time is BEFORE the reminder time and it's still pending
        if now < reminder_time and row["Status"] == "Pending":
            print(f"🔔 Upcoming Reminder for {row['Member Name']}: "
                  f"Take {row['Medicine']} - {row['Dosage']} at {row['Time']}")
            df.at[idx, "Status"] = "Delivered"
            any_reminder = True

    if any_reminder:
        save_schedule(df)
        print("✅ Reminders delivered and updated.")
    else:
        print("📭 No pending reminders right now.")
