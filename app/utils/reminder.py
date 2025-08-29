import os
import pandas as pd
from datetime import datetime, timedelta

REMINDER_FILE = os.path.join(os.path.dirname(__file__), "reminders.csv")

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return pd.DataFrame(columns=[
            "Username", "Title", "Notes", "Date", "Time(s)", "Frequency", "Taken"
        ])
    df = pd.read_csv(REMINDER_FILE, dtype=str).fillna("")
    if "Taken" not in df.columns:
        df["Taken"] = ""
    return df

def save_reminders(df):
    df.to_csv(REMINDER_FILE, index=False)

# -----------------------------
# Add reminder
# -----------------------------
def add_reminder(username):
    df = load_reminders()
    title = input("Reminder Title: ").strip()
    notes = input("Notes (optional): ").strip()
    date_str = input("Date (DD/MM/YYYY or DD-MM-YYYY or DD/MM/YY): ").strip()
    times_str = input("Time(s) (HH:MM, comma-separated for multiple alerts): ").strip()
    frequency = input("Frequency (Once/Daily/Weekly/Monthly): ").strip().lower()
    alert_times_str = input("Alert times (comma-separated, e.g., 09:00,30min-before): ").strip()

    # Standardize 2-digit year
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%y")
    except:
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except:
            try:
                date_obj = datetime.strptime(date_str, "%d-%m-%y")
            except:
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                except ValueError:
                    print("❌ Invalid date format.")
                    return
    date_final = date_obj.strftime("%Y-%m-%d")

    df = pd.concat([df, pd.DataFrame([{
        "Username": username,
        "Title": title,
        "Notes": notes,
        "Date": date_final,
        "Time(s)": times_str,
        "Frequency": frequency,
        "Taken": ""
    }])], ignore_index=True)

    save_reminders(df)
    print("✅ Reminder added successfully!")
    # Google Calendar integration (optional)
    try:
        from googleapiclient.discovery import build
        # Your Google Calendar code here
    except Exception:
        print("⚠️ Google Calendar credentials not found, skipping calendar integration.")

# -----------------------------
# Check reminders
# -----------------------------
def check_reminders(username=None, show_all=False):
    df = load_reminders()
    if username:
        df = df[df["Username"] == username]

    if df.empty:
        print("📭 No upcoming reminders.")
        return

    print("\n🔔 Upcoming Reminders:")
    now = datetime.now()
    for i, row in df.iterrows():
        # Get all alert times
        times_list = [t.strip() for t in row["Time(s)"].split(",") if t.strip()]
        for t_str in times_list:
            try:
                # Handle relative times like 30min-before, 1hr-before
                if "min-before" in t_str:
                    mins = int(t_str.replace("min-before", "").strip())
                    alert_time = datetime.strptime(row["Date"] + " " + times_list[0], "%Y-%m-%d %H:%M") - timedelta(minutes=mins)
                elif "hr-before" in t_str:
                    hrs = int(t_str.replace("hr-before", "").strip())
                    alert_time = datetime.strptime(row["Date"] + " " + times_list[0], "%Y-%m-%d %H:%M") - timedelta(hours=hrs)
                else:
                    alert_time = datetime.strptime(row["Date"] + " " + t_str, "%Y-%m-%d %H:%M")
            except:
                continue

            if show_all or alert_time >= now:
                print(f"🔹 {row['Username']}: {row['Title']} ({row['Notes']}) at {alert_time.strftime('%Y-%m-%d %H:%M')} | Taken: {row['Taken']}")

# -----------------------------
# Mark as Taken
# -----------------------------
def mark_as_taken(username):
    df = load_reminders()
    df_user = df[df["Username"] == username]
    if df_user.empty:
        print("📭 No reminders to mark as taken.")
        return

    print("\n📝 Reminders for marking as taken:")
    for idx, row in df_user.iterrows():
        print(f"[{idx}] {row['Title']} on {row['Date']} at {row['Time(s)']} | Taken: {row['Taken']}")

    try:
        sel = int(input("Enter the index to mark as taken: ").strip())
        if sel in df.index:
            df.at[sel, "Taken"] = "Yes"
            save_reminders(df)
            print("✅ Marked as Taken!")
        else:
            print("❌ Invalid index.")
    except ValueError:
        print("❌ Enter a valid number.")
