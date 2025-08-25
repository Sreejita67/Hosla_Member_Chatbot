from app.utils.messaging import view_messages_for_user

current_user = input("Enter your name (logged-in user): ").strip()
view_messages_for_user(current_user)
