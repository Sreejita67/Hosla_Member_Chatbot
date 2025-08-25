from app.utils.messaging import send_message
from app.utils.config import GOOGLE_SHEET_CSV_URL, MESSAGE_LOG_PATH

current_user = input("Enter your name (logged-in user): ").strip()
send_message(current_user)
