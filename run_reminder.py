from app.utils import reminder

def main():
    current_user = input("Enter your name: ").strip()
    
    print("\n1. Add Reminder")
    print("2. Check Reminders")
    print("3. Mark Reminder as Taken")
    choice = input("Choose (1/2/3): ").strip()

    if choice == "1":
        reminder.add_reminder(current_user)
    elif choice == "2":
        # Show all upcoming reminders for the user
        reminder.check_reminders(username=current_user, show_all=True)
    elif choice == "3":
        reminder.mark_as_taken(current_user)
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
