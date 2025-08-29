import os
from app.utils import config, member_info, reminder, messaging, emergency, health_checkup
import sys

def print_emergencies_table(items):
    if not items:
        print("📭 No emergencies logged yet.")
        return
    print("\n🚨 Emergency Logs:")
    for i, e in enumerate(items):
        print(
            f"\n[{i}] {e.get('Member Name', 'N/A')} | "
            f"{e.get('City', 'N/A')} {e.get('Pin Code', '')} | "
            f"{e.get('Time', 'N/A')}\n"
            f"Cause: {e.get('Cause', 'N/A')} | Status: {e.get('Status', 'N/A')}"
        )

def manage_health_checkups(input_name):
    exact_name, age = health_checkup.load_user_info(input_name)
    if not exact_name:
        print(f"❌ Could not find '{input_name}' in the Google Sheet. Using 'Unknown' as age.")
        exact_name = input_name
        age = None
    print(f"\nWelcome to Health Checkup Module, {exact_name} (Age: {age if age else 'Unknown'})")

    try:
        temp = float(input("Enter Temperature (°F): ").strip())
        systolic = int(input("Enter Systolic BP (mmHg): ").strip())
        diastolic = int(input("Enter Diastolic BP (mmHg): ").strip())
        hr = int(input("Enter Heart Rate (bpm): ").strip())
        chol = int(input("Enter Cholesterol (mg/dL): ").strip())
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")
        return

    record = health_checkup.record_health_checkup(
        exact_name, temp, systolic, diastolic, hr, chol, age
    )

    print("\n✅ Health Checkup Recorded!")
    print(f"Flags: {record['Flags']}")
    print(f"Advice: {record['Advice']}")

# -----------------------------
# Main chatbot loop
# -----------------------------
def main():
    print("=== Hosla Member Chatbot ===")
    username = input("Enter your name: ").strip()

    greeting, pic_path, active_members = member_info.greet_user_and_show_active_members(
        config.IMAGE_DIR, username
    )

    if active_members == [] and "No user found" in greeting:
        print("\n" + greeting)
        print("🚫 Sorry! We didn't find your name in our Member List. Check and Try Again if you are a registered HOSLA Member.")
        sys.exit(0)

    print("\n" + greeting)
    if pic_path:
        print(f"📷 Profile picture found at: {pic_path}")
    else:
        print("📷 No profile picture found.")
    print("\n✅ Active Members:")
    for m in active_members:
        print(" - " + m)

    while True:
        print("\n=== Choose Your Service/s ===")
        print("1. Add Reminder")
        print("2. Check Reminders")
        print("3. Mark Reminder as Taken")
        print("4. Send Message")
        print("5. View My Messages")
        print("6. Raise Emergency")
        print("7. View Emergencies")
        print("8. Mark Emergency as Resolved")
        print("9. Health Checkup Updates")
        print("10. View Health Trends")
        print("11. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            reminder.add_reminder(username)
        elif choice == "2":
            reminder.check_reminders(username=username, show_all=True)
        elif choice == "3":
            reminder.mark_as_taken(username)
        elif choice == "4":
            messaging.send_message(username)
        elif choice == "5":
            messaging.view_messages_for_user(username)
        elif choice == "6":
            details = emergency.fetch_member_details(username)
            if not details:
                print("❌ Your member details were not found in the Google Sheet.")
            else:
                cause = input("Enter reason for emergency: ").strip()
                emergency.log_emergency(details, cause)
                print("✅ Emergency logged.")
        elif choice == "7":
            items = emergency.view_emergencies()
            print_emergencies_table(items)
        elif choice == "8":
            items = emergency.view_emergencies()
            if not items:
                print("📭 No emergencies to resolve.")
            else:
                print_emergencies_table(items)
                try:
                    idx = int(input("\nEnter the index to mark Resolved: ").strip())
                    if emergency.mark_resolved(idx):
                        print("✅ Marked as Resolved.")
                    else:
                        print("❌ Invalid index.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        elif choice == "9":
            print("\n🩺 Entering Health Checkup Module...")
            manage_health_checkups(username)
        elif choice == "10":
            print(f"\n📊 Viewing Health Trends for {username}...")
            health_checkup.generate_trends(username)
        elif choice == "11":
            print("👋 Goodbye! Stay healthy, Stay safe. Hosla is always with you. For any enquiry call 7811009309")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
