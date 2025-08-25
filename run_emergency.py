from app.utils import emergency

def main():
    user_name = input("Enter your name (logged-in user): ").strip()
    details = emergency.fetch_member_details(user_name)
    
    if not details:
        print("❌ Member not found in database.")
        return
    
    cause = input("Enter the cause of emergency: ").strip()
    emergency.log_emergency(details, cause)
    print("\n🚨 Emergency alert sent successfully! 🚨")

if __name__ == "__main__":
    main()
