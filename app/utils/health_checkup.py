import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Fallback if config is missing
try:
    from app.utils.config import BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Sheet CSV link
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8IArJoxgQ2EL2fQJn_rUVozWqJbz-n0Qn42rTMDHHZezCbn5MEa-0TcvRfPiEGPyDj3W96LkRFwSH/pub?gid=19136775&single=true&output=csv"

# ---------------------------------------
# Fetch exact member name & age
# ---------------------------------------
def load_user_info(username: str):
    """Fetch exact Member Name and Age from Google Sheet, case-insensitive."""
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        match = df[df['Member Name'].str.strip().str.lower() == username.strip().lower()]
        if not match.empty:
            exact_name = match.iloc[0]['Member Name']
            age = int(match.iloc[0]['Age'])
            return exact_name, age
    except Exception as e:
        print(f"[ERROR] Could not fetch info from sheet: {e}")
    return None, None

# ---------------------------------------
# Health CSV loader
# ---------------------------------------
def load_health_data(filename="health_data.csv"):
    """Load or create the health data CSV."""
    file_path = os.path.join(BASE_DIR, "data", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=[
            "Timestamp", "Patient Name", "Age",
            "Temperature (°F)", "Blood Pressure (mmHg)",
            "Heart Rate (bpm)", "Cholesterol (mg/dL)",
            "Flags", "Advice"
        ])
        df.to_csv(file_path, index=False)
    return file_path

# ---------------------------------------
# Generate advice with age-specific tips
# ---------------------------------------
def generate_advice(temp_f, systolic, diastolic, heart_rate, cholesterol, age=None):
    """Generate health advice and flags. Adds senior-specific advice for age 50-100."""
    flags, advice = [], []

    # Temperature
    if temp_f > 100.4:
        flags.append("Fever")
        advice.append("🌡️ High temperature – consult a doctor.")
    elif temp_f < 95:
        flags.append("Hypothermia")
        advice.append("❄️ Low body temperature – seek medical help.")
    else:
        advice.append("✅ Temperature normal.")

    # Blood Pressure
    if systolic > 130 or diastolic > 80:
        flags.append("High BP")
        advice.append("⚠️ Blood pressure is high – reduce salt & consult doctor.")
    elif systolic < 90 or diastolic < 60:
        flags.append("Low BP")
        advice.append("⚠️ Blood pressure is low – hydrate & rest.")
    else:
        advice.append("✅ Blood pressure normal.")

    # Heart Rate
    if heart_rate > 100:
        flags.append("Tachycardia")
        advice.append("❤️ Heart rate is high – check for stress or illness.")
    elif heart_rate < 60:
        flags.append("Bradycardia")
        advice.append("❤️ Heart rate is low – consult a doctor.")
    else:
        advice.append("✅ Heart rate normal.")

    # Cholesterol
    if cholesterol >= 240:
        flags.append("High Cholesterol")
        advice.append("🥗 High cholesterol – adjust diet and exercise.")
    elif 200 <= cholesterol < 240:
        flags.append("Borderline Cholesterol")
        advice.append("⚠️ Borderline cholesterol – watch your diet.")
    else:
        advice.append("✅ Cholesterol normal.")

    # Age-specific advice for seniors (50-100)
    if age is not None and 50 <= age <= 100:
        advice.append("👴 As a senior (50+), maintain regular checkups, balanced diet, and moderate exercise.")

    return ", ".join(flags) if flags else "Normal", " | ".join(advice)

# ---------------------------------------
# Record a health checkup
# ---------------------------------------
def record_health_checkup(username, temp_f, systolic, diastolic, heart_rate, cholesterol, age=None):
    """Record a health checkup with flags and advice."""
    file_path = load_health_data()
    bp = f"{systolic}/{diastolic}"
    flags, advice = generate_advice(temp_f, systolic, diastolic, heart_rate, cholesterol, age)

    new_record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Patient Name": username,
        "Age": age if age else "Unknown",
        "Temperature (°F)": temp_f,
        "Blood Pressure (mmHg)": bp,
        "Heart Rate (bpm)": heart_rate,
        "Cholesterol (mg/dL)": cholesterol,
        "Flags": flags,
        "Advice": advice
    }

    # Safe append to CSV
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=new_record.keys())

    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_csv(file_path, index=False)

    return new_record

# ---------------------------------------
# Generate health trends and summary
# ---------------------------------------
def generate_trends(username):
    """Plot clear health trends with subplots for easy interpretation."""
    file_path = load_health_data()  # Ensure this is defined elsewhere
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print("📭 No health records found yet.")
        return

    df = pd.read_csv(file_path)
    user_df = df[df["Patient Name"].str.strip().str.lower() == username.strip().lower()]

    if user_df.empty:
        print(f"📭 No health records found for {username}.")
        return

    # Convert timestamp to datetime
    user_df["Timestamp"] = pd.to_datetime(user_df["Timestamp"])
    user_df = user_df.sort_values("Timestamp").tail(5)

    # Split BP into systolic and diastolic
    bp_values = user_df["Blood Pressure (mmHg)"].str.split("/", expand=True).astype(float)
    user_df["Systolic BP"] = bp_values[0]
    user_df["Diastolic BP"] = bp_values[1]

    # Create subplots
    fig, axes = plt.subplots(5, 1, figsize=(12, 15), sharex=True)
    fig.suptitle(f"📈 Health Trends for {username}", fontsize=16, fontweight="bold")

    metrics = [
        ("Temperature (°F)", "Temperature (°F)", "green"),
        ("Systolic BP", "Systolic BP (mmHg)", "blue"),
        ("Diastolic BP", "Diastolic BP (mmHg)", "cyan"),
        ("Heart Rate (bpm)", "Heart Rate (bpm)", "orange"),
        ("Cholesterol (mg/dL)", "Cholesterol (mg/dL)", "purple"),
    ]

    # Plot each metric separately
    for ax, (col, ylabel, color) in zip(axes, metrics):
        ax.plot(user_df["Timestamp"], user_df[col], marker='o', color=color, label=col)

        # ✅ Format x-axis ticks as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.format_xdata = mdates.DateFormatter("%Y-%m-%d")  # ✅ fixes (x,y) readout

        # Highlight abnormal values in red
        for i, row in user_df.iterrows():
            flags = str(row.get("Flags", "Normal"))
            if flags != "Normal":
                ax.scatter(row["Timestamp"], row[col], color="red", s=100, zorder=5)

        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()

    # X-axis formatting
    axes[-1].set_xlabel("Date", fontsize=12)
    plt.xticks(rotation=45)

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # leave space for suptitle
    plt.show()

    # Trend summaries
    print(f"\n📊 Weekly Health Trends for {username} (last {len(user_df)} records):")
    def summarize_trend(metric):
        values = user_df[metric].tolist()
        trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
        return f"{metric}: {values[0]} → {values[-1]} ({trend})"

    for m in ["Temperature (°F)", "Heart Rate (bpm)", "Systolic BP", "Diastolic BP", "Cholesterol (mg/dL)"]:
        print(summarize_trend(m))
