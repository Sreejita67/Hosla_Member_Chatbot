import os
import sys
import re
from app.utils import config, member_info, reminder, messaging, emergency, health_checkup
from auth import authenticate_user, register_user, reset_password  # ✅ Import password reset

# -----------------------------
# Validation Helpers
# -----------------------------
def is_valid_mobile(mobile):
    """Validate Indian mobile numbers (10 digits, starts with 6-9)."""
    return bool(re.fullmatch(r"[6-9]\d{9}", str(mobile).strip()))

def is_valid_email(email):
    """Basic email validation using regex."""
    return bool(re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email.strip()))

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

    print("\n1. Login")
    print("2. Register (New User)")
    print("3. Reset Password")
    choice = input("Choose an option: ").strip()

    if choice == "2":
        print("\n=== Register New Member ===")
        full_name = input("Enter Full Name: ").strip()
        age = input("Enter Age: ").strip()
        role = input("Enter Role: ").strip()
        interests = input("Enter Interests (comma-separated): ").strip()
        locality = input("Enter Locality: ").strip()
        city = input("Enter City: ").strip()
        pin_code = input("Enter Pin Code: ").strip()

        # ✅ Validate mobile number until correct
        while True:
            contact_no = input("Enter Contact No.: ").strip()
            if is_valid_mobile(contact_no):
                break
            print("❌ Invalid mobile number. Must be 10 digits starting with 6-9.")

        # ✅ Validate email until correct
        while True:
            email = input("Enter Email ID: ").strip()
            if is_valid_email(email):
                break
            print("❌ Invalid email format. Please try again.")

        dob = input("Enter Date of Birth (DD-MM-YYYY): ").strip()
        username = input("Choose a username: ").strip()
        password = input("Choose a password: ").strip()

        success = register_user(
            full_name, age, role, interests, locality, city, pin_code,
            contact_no, email, dob, username, password
        )

        if success:
            print("🎉 Registration successful! You are now logged in.")
            user_record = {
                "Member Name": full_name,
                "Username": username,
                "Role": role,
                "City": city,
                "Pin Code": pin_code
            }
            member_name = full_name
        else:
            print("⚠️ Registration failed. Try again.")
            sys.exit(0)

    elif choice == "3":
        print("\n=== Password Reset ===")
        uname = input("Enter your username: ").strip()
        old_pw = input("Enter your old password: ").strip()
        reset_password(uname, old_pw)
        sys.exit(0)

    # -------------------------
    # Login flow
    # -------------------------
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    user_record = authenticate_user(username, password)
    if not user_record:
        print("🚫 Invalid credentials. Please check your username/password.")
        sys.exit(0)

    member_name = user_record.get("Member Name", username)

    greeting, pic_path, active_members = member_info.greet_user_and_show_active_members(
        config.IMAGE_DIR, member_name
    )

    if active_members == [] and "No user found" in greeting:
        print("\n" + greeting)
        print("🚫 Sorry! We didn't find your name in our Member List.")
        sys.exit(0)

    print("\n" + greeting)
    if pic_path:
        print(f"📷 Profile picture found at: {pic_path}")
    else:
        print("📷 No profile picture found.")
    print("\n✅ Active Members:")
    for m in active_members:
        print(" - " + m)

    # -------------------------
    # Main Menu Loop
    # -------------------------
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
            reminder.add_reminder(member_name)
        elif choice == "2":
            reminder.check_reminders(username=member_name, show_all=True)
        elif choice == "3":
            reminder.mark_as_taken(member_name)
        elif choice == "4":
            messaging.send_message(member_name)
        elif choice == "5":
            messaging.view_messages_for_user(member_name)
        elif choice == "6":
            details = emergency.fetch_member_details(member_name)
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
            manage_health_checkups(member_name)
        elif choice == "10":
            print(f"\n📊 Viewing Health Trends for {member_name}...")
            health_checkup.generate_trends(member_name)
        elif choice == "11":
            print("👋 Goodbye! Stay healthy, Stay safe. Hosla is always with you. For any enquiry call 7811009309")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
