import csv
import datetime
import requests
from app.utils import config

EMERGENCY_LOG = "logs/emergency_logs.csv"

def fetch_member_details(user_name):
    """Fetch user details from Google Sheets CSV"""
    response = requests.get(config.GOOGLE_SHEET_CSV_URL)
    response.raise_for_status()
    rows = list(csv.DictReader(response.text.splitlines()))
    
    for row in rows:
        if row["Member Name"].strip().lower() == user_name.strip().lower():
            return {
                "name": row["Member Name"],
                "locality": row.get("Locality", "N/A"),
                "city": row.get("City", "N/A"),
                "pin": row.get("Pin Code", "N/A"),
                "contact": row.get("Contact", "N/A")
            }
    return None

def log_emergency(details, cause):
    """Log emergency to CSV"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Member Name": details["name"],
        "Locality": details["locality"],
        "City": details["city"],
        "Pin Code": details["pin"],
        "Contact": details["contact"],
        "Time": now,
        "Cause": cause,
        "Status": "Pending"
    }
    
    file_exists = False
    try:
        with open(EMERGENCY_LOG, "r", encoding="utf-8") as f:
            file_exists = True
    except FileNotFoundError:
        pass
    
    with open(EMERGENCY_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

def view_emergencies():
    """View all emergencies with Pending first, then Resolved."""
    try:
        with open(EMERGENCY_LOG, "r", encoding="utf-8") as f:
            emergencies = list(csv.DictReader(f))
            # Sort so Pending comes before Resolved
            emergencies.sort(key=lambda e: 0 if e["Status"] == "Pending" else 1)
            return emergencies
    except FileNotFoundError:
        return []

def mark_resolved(index):
    """Mark emergency as resolved"""
    emergencies = view_emergencies()
    if 0 <= index < len(emergencies):
        emergencies[index]["Status"] = "Resolved"
        with open(EMERGENCY_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=emergencies[0].keys())
            writer.writeheader()
            writer.writerows(emergencies)
        return True
    return False
