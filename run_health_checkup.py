# run_health_checkup.py
from app.utils.health_checkup import add_health_checkup, show_recent_health_data, plot_health_trends

def run_health_checkup():
    current_user = input("Enter your name (logged-in user): ").strip()

    print("\n📋 Enter today's health checkup data:")
    try:
        systolic = int(input("  Systolic (mmHg): "))
        diastolic = int(input("   Diastolic (mmHg): "))
        heart_rate = int(input("   Heart Rate (bpm): "))
        temperature = float(input("   Temperature (°C): "))
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")
        return

    
    add_health_checkup(current_user, systolic, diastolic, heart_rate, temperature)
    print("💾 Health checkup saved successfully.\n")
    

    # Show last 5 records
    print("📊 Last 5 Health Records:")
    show_recent_health_data(current_user, last_n=5)

    # Plot health trends
    plot_health_trends(current_user)

if __name__ == "__main__":
    run_health_checkup()

