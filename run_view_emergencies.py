from app.utils import emergency

def main():
    emergencies = emergency.view_emergencies()
    if not emergencies:
        print("✅ No emergencies at the moment.")
        return

    print("\n🚨 Pending Emergencies 🚨\n")
    for idx, e in enumerate(emergencies):
        status_color = "\033[91m" if e["Status"] == "Pending" else "\033[92m"
        print(f"{status_color}{idx+1}. {e['Member Name']} - {e['Cause']} ({e['Status']})\033[0m")
        print(f"   Location: {e['Locality']}, {e['City']} - {e['Pin Code']}")
        print(f"   Contact: {e['Contact']}")
        print(f"   Time: {e['Time']}\n")

    choice = input("Mark any emergency as resolved? (y/n): ").strip().lower()
    if choice == "y":
        index = int(input("Enter emergency number: ")) - 1
        if emergency.mark_resolved(index):
            print("✅ Emergency marked as resolved.")
        else:
            print("❌ Invalid selection.")

if __name__ == "__main__":
    main()
