import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone
from app.utils.config import BASE_DIR

DATA_FILE = os.path.join(BASE_DIR, "data", "health_data.csv")

def load_health_data():
    """Load or create the health data CSV."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["User", "Date", "BP_Systolic", "BP_Diastolic", "Heart_Rate", "Temperature"])
        df.to_csv(DATA_FILE, index=False)
        return df

def save_health_data(df):
    """Save the entire DataFrame (append already handled outside)."""
    df.to_csv(DATA_FILE, index=False)

def give_health_advice(systolic, diastolic, heart_rate, temperature):
    """Provide personalized health advice based on vitals."""
    advice = []

    # Blood Pressure
    if systolic > 140 or diastolic > 90:
        advice.append("⚠ High BP. Reduce salt, manage stress, consult a doctor if it persists.")
    elif systolic < 90 or diastolic < 60:
        advice.append("⚠ Low BP. Stay hydrated and eat balanced food. See a doctor if frequent.")
    else:
        advice.append("✅ BP is within normal range.")

    # Heart Rate
    if heart_rate > 100:
        advice.append("⚠ High heart rate. Rest, avoid caffeine, manage stress.")
    elif heart_rate < 60:
        advice.append("⚠ Low heart rate. Light exercise may help. Consult a doctor if persistent.")
    else:
        advice.append("✅ Heart rate is normal.")

    # Temperature
    if temperature > 38:
        advice.append("⚠ Fever detected. Rest, drink fluids, and see a doctor if it stays high.")
    elif temperature < 36:
        advice.append("⚠ Low temperature. Keep warm and monitor your health.")
    else:
        advice.append("✅ Temperature is normal.")

    print("\n💡 Health Advice:")
    for tip in advice:
        print("   -", tip)

    return advice

def add_health_checkup(user, systolic, diastolic, heart_rate, temperature):
    """Add a health checkup record for a user and provide advice."""
    df = load_health_data()
    india_time = datetime.now(timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = {
        "User": user,
        "Date": india_time,
        "BP_Systolic": systolic,
        "BP_Diastolic": diastolic,
        "Heart_Rate": heart_rate,
        "Temperature": temperature
    }
    
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_health_data(df)
    print(f"✅ Health data added for {user} at {india_time}")

    # Provide health advice after saving
    give_health_advice(systolic, diastolic, heart_rate, temperature)

def show_recent_health_data(user, last_n=5):
    """Display recent health data for a user."""
    df = load_health_data()
    user_df = df[df["User"] == user]
    
    if user_df.empty:
        print(f"⚠ No health records found for {user}")
        return
    
    print(f"\n📊 Last {last_n} health records for {user}:")
    print(user_df.tail(last_n))

def plot_health_trends(user):
    """Plot and save trends of BP, Heart Rate, and Temperature."""
    df = load_health_data()
    user_df = df[df["User"] == user].copy()  # avoid SettingWithCopyWarning
    
    if user_df.empty:
        print(f"⚠ No health records found for {user}")
        return
    
    user_df.loc[:, "Date"] = pd.to_datetime(user_df["Date"])
    plt.figure(figsize=(10, 6))
    plt.plot(user_df["Date"], user_df["BP_Systolic"], label="BP Systolic")
    plt.plot(user_df["Date"], user_df["BP_Diastolic"], label="BP Diastolic")
    plt.plot(user_df["Date"], user_df["Heart_Rate"], label="Heart Rate")
    plt.plot(user_df["Date"], user_df["Temperature"], label="Temperature (°C)")
    
    plt.title(f"Health Trends for {user}")
    plt.xlabel("Date")
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save chart
    charts_dir = os.path.join(BASE_DIR, "data", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    chart_path = os.path.join(charts_dir, f"health_trends_{user}.png")
    plt.savefig(chart_path)
    
    plt.show()
    print(f"📁 Trend chart saved at: {chart_path}")

def manage_checkups(user):
    """Interactive menu for managing health checkups."""
    while True:
        print("\n=== Health Checkup Menu ===")
        print("1. Add a new health checkup")
        print("2. View recent health data")
        print("3. Plot health trends")
        print("4. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            try:
                systolic = int(input("Enter BP Systolic: "))
                diastolic = int(input("Enter BP Diastolic: "))
                heart_rate = int(input("Enter Heart Rate: "))
                temperature = float(input("Enter Temperature (°C): "))
                add_health_checkup(user, systolic, diastolic, heart_rate, temperature)
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
        elif choice == "2":
            show_recent_health_data(user)
        elif choice == "3":
            plot_health_trends(user)
        elif choice == "4":
            print("⬅ Returning to main menu...")
            break
        else:
            print("❌ Invalid choice. Try again.")
