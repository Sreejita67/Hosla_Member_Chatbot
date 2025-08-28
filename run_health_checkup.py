from app.utils.health_checkup import record_health_checkup

def run_health_checkup():
    patient_name = input("Enter your name (logged-in user): ").strip()

    print("\n📋 Enter today's health checkup data:")
    try:
        systolic = int(input("  Systolic (mmHg): "))
        diastolic = int(input("  Diastolic (mmHg): "))
        heart_rate = int(input("  Heart Rate (bpm): "))
        cholesterol = float(input("  Cholesterol (mg/dL): "))
        temperature_f = float(input("  Temperature (°F): "))
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")
        return

    # Save data (with advice + permanent record)
    record_health_checkup(
        username=patient_name,
        temp_f=temperature_f,
        systolic=systolic,
        diastolic=diastolic,
        heart_rate=heart_rate,
        cholesterol=cholesterol
    )

    print("\n💾 Health checkup saved successfully with advice!\n")

if __name__ == "__main__":
    run_health_checkup()
