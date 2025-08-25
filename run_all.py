# run_all.py
import os
from app.utils import config, member_info, medication, messaging, emergency, health_checkup
import sys

def print_emergencies_table(items):
    """Display emergency logs in a simple table."""
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

def main():
    print("=== Hosla Member Chatbot ===")
    username = input("Enter your name: ").strip()

    # 1️⃣ Greet user & show active members
    greeting, pic_path, active_members = member_info.greet_user_and_show_active_members(
        config.IMAGE_DIR, username
    )

    if active_members == [] and "No user found" in greeting:
        print("\n" + greeting)
        print("🚫Sorry ! We didn't find your name in our Member List. Check and Try Again if you are a registered HOSLA Member")
        sys.exit(0)

    print("\n" + greeting)
    if pic_path:
        print(f"📷 Profile picture found at: {pic_path}")
    else:
        print("📷 No profile picture found.")
    print("\n✅ Active Members:")
    for m in active_members:
        print(" - " + m)

    # Menu loop
    while True:
        print("\n=== Choose Your Service/s===")
        print("1. Add Medication Reminder")
        print("2. Check Reminders")
        print("3. Send Message")
        print("4. View My Messages")
        print("5. Raise Emergency")
        print("6. View Emergencies")
        print("7. Mark Emergency as Resolved")
        print("8. Health Checkup Updates")
        print("9. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            medication.add_reminder(username)
        elif choice == "2":
            medication.check_reminders()
        elif choice == "3":
            messaging.send_message(username)
        elif choice == "4":
            messaging.view_messages_for_user(username)
        elif choice == "5":
            details = emergency.fetch_member_details(username)
            if not details:
                print("❌ Your member details were not found in the Google Sheet.")
            else:
                cause = input("Enter reason for emergency: ").strip()
                emergency.log_emergency(details, cause)
                print("✅ Emergency logged.")
        elif choice == "6":
            items = emergency.view_emergencies()
            print_emergencies_table(items)
        elif choice == "7":
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
        elif choice == "8":
            health_checkup.manage_checkups(username)
        elif choice == "9":
            print("👋 Goodbye! Stay healthy, Stay safe. Hosla is always with you. For any enquiry call 7811009309")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
