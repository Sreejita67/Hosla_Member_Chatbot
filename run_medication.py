from app.utils import medication

def main():
    current_user = input("Enter your name (logged-in user): ").strip()

    action = input("\n📌 1. Add Reminder\n📌 2. Run Reminder Check\nChoose (1/2): ").strip()
    if action == "1":
        medication.add_reminder(current_user)
    elif action == "2":
        medication.check_reminders()
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
