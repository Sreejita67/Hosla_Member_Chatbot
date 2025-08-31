import os
import csv
import pandas as pd
from datetime import datetime
from pytz import timezone
from transformers import MarianTokenizer, MarianMTModel
from app.utils.config import GOOGLE_SHEET_CSV_URL, MESSAGE_LOG_PATH

# 🌐 Translation models map
model_map = {
    "bn": "Helsinki-NLP/opus-mt-bn-en",
    "hi": "Helsinki-NLP/opus-mt-hi-en",
    "ta": "Helsinki-NLP/opus-mt-ta-en",
    "te": "Helsinki-NLP/opus-mt-te-en",
    "pa": "Helsinki-NLP/opus-mt-pa-en",
    "mr": "Helsinki-NLP/opus-mt-mr-en"
}
loaded_models = {}

def translate_to_english(msg, lang_code):
    if lang_code == "en":
        return msg
    if lang_code not in loaded_models:
        model_name = model_map[lang_code]
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        loaded_models[lang_code] = (tokenizer, model)
    tokenizer, model = loaded_models[lang_code]
    inputs = tokenizer([msg], return_tensors="pt", padding=True)
    tokens = model.generate(**inputs)
    return tokenizer.decode(tokens[0], skip_special_tokens=True)

def find_member_by_partial_name(input_name, df):
    input_name = input_name.lower().strip()
    matches = df[df["Member Name"].str.lower().str.contains(input_name)]
    if matches.empty:
        return None, []
    elif len(matches) == 1:
        return matches.iloc[0]["Member Name"], []
    else:
        return None, matches["Member Name"].tolist()

def choose_member_from_matches(matches, input_name):
    print(f"\n⚠️ Multiple members found matching '{input_name}':")
    for i, name in enumerate(matches, start=1):
        print(f"{i}. {name}")
    while True:
        try:
            choice = int(input("👉 Please enter the number of the correct member: "))
            if 1 <= choice <= len(matches):
                return matches[choice - 1]
            else:
                print("❌ Invalid choice. Try again.")
        except ValueError:
            print("❌ Please enter a valid number.")

def send_message(current_user, preselected_recipient=None):
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL, dtype=str).fillna("")
    member_names = df["Member Name"]

    if preselected_recipient:
        receiver_name, suggestions = find_member_by_partial_name(preselected_recipient, df)
        if not receiver_name:
            if suggestions:
                receiver_name = choose_member_from_matches(suggestions, preselected_recipient)
            else:
                print("❌ No matching member found.")
                return
    else:
        receiver_input = input("\nEnter the name of the member you want to message or reply to: ").strip()
        receiver_name, suggestions = find_member_by_partial_name(receiver_input, df)

        if not receiver_name:
            if suggestions:
                receiver_name = choose_member_from_matches(suggestions, receiver_input)
            else:
                print("❌ No matching member found.")
                return

    # 🌐 Language
    lang_map = {
        "1": ("en", "English"),
        "2": ("hi", "Hindi"),
        "3": ("bn", "Bengali"),
        "4": ("ta", "Tamil"),
        "5": ("te", "Telugu"),
        "6": ("pa", "Punjabi"),
        "7": ("mr", "Marathi")
    }
    print("\n🌐 Choose message language:")
    for k, v in lang_map.items():
        print(f"{k}. {v[1]}")
    lang_code = lang_map.get(input("Enter choice: ").strip(), ("en",))[0]

    # ✍️ Message
    message = input("Enter your message: ")
    try:
        translated_msg = translate_to_english(message, lang_code)
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        translated_msg = "[Translation Failed]"

    # 📤 Delivery Scope
    print("\nShare Options:")
    print("1. Public\n2. Only this member\n3. Multiple Members")
    choice = input("Choose (1/2/3): ").strip()
    if choice == "1":
        audience = [n for n in member_names if n.lower() != current_user.lower()]
    elif choice == "2":
        audience = [receiver_name]
    elif choice == "3":
        audience_input = input("Enter names separated by commas: ")
        audience = []
        for name_part in audience_input.split(","):
            name_part = name_part.strip()
            name_found, suggestions = find_member_by_partial_name(name_part, df)
            if name_found:
                audience.append(name_found)
            elif suggestions:
                selected = choose_member_from_matches(suggestions, name_part)
                if selected:
                    audience.append(selected)
            else:
                print(f"❌ No match found for '{name_part}'")
    else:
        print("❌ Invalid option. Aborting.")
        return

    # 📎 Save Message(s)
    timestamp = datetime.now(timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
    entries = [{
        "From": current_user,
        "To": name,
        "Original Message": message,
        "Language": lang_code,
        "Translated Message (EN)": translated_msg,
        "Timestamp": timestamp
    } for name in audience]

    file_exists = os.path.exists(MESSAGE_LOG_PATH)
    with open(MESSAGE_LOG_PATH, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=entries[0].keys(), quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writeheader()
        writer.writerows(entries)

    print("\n✅ Message(s) sent successfully!")

    # 🕓 Chat History
    try:
        hist_df = pd.read_csv(MESSAGE_LOG_PATH, quoting=csv.QUOTE_ALL)
        chat_df = hist_df[((hist_df['From'] == current_user) & (hist_df['To'] == receiver_name)) |
                          ((hist_df['From'] == receiver_name) & (hist_df['To'] == current_user))]

        chat_df = chat_df.sort_values(by="Timestamp")

        if chat_df.empty:
            print(f"\n📬 No messages exchanged with {receiver_name} yet.")
        else:
            print(f"\n🔔 Chat with {receiver_name}:")
            for _, row in chat_df.iterrows():
                sender = "👤 You" if row['From'] == current_user else f"👴 {row['From']}"
                print(f"\n🕓 [{row['Timestamp']}]\n{sender}: {row['Original Message']}")
    except Exception as e:
        print(f"⚠️ Unable to show chat: {e}")

def view_messages_for_user(current_user):
    try:
        df = pd.read_csv(MESSAGE_LOG_PATH)
    except FileNotFoundError:
        print("📂 No message log found.")
        return

    # Filter messages addressed to the current user
    messages = df[df['To'].str.lower() == current_user.lower()]

    if messages.empty:
        print("📭 No messages found for you.")
        return

    print(f"\n📨 You have {len(messages)} message(s):")

    for _, row in messages.iterrows():
        print(f"\nFrom: {row['From']}")
        print(f"Message: {row['Message']}")
        print(f"Translated: {row['Translation']}")

        timestamp_str = row.get("Timestamp", None)
        if timestamp_str:
            try:
                msg_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                diff = now - msg_time

                seconds = diff.total_seconds()
                if seconds < 60:
                    readable = f"{int(seconds)} seconds ago"
                elif seconds < 3600:
                    readable = f"{int(seconds // 60)} minutes ago"
                elif seconds < 86400:
                    readable = f"{int(seconds // 3600)} hours ago"
                else:
                    readable = f"{int(seconds // 86400)} days ago"

                print(f"Sent: {readable} ({timestamp_str})")
            except Exception:
                print(f"Timestamp: {timestamp_str}")
        else:
            print("Timestamp: N/A")

    # Ask if the user wants to reply
    reply = input("\n💬 Do you want to reply to any message? (y/n): ").strip().lower()
    if reply == 'y':
        recipient = input("Enter the name of the person you want to reply to: ").strip()
        send_message(current_user, preselected_recipient=recipient)



