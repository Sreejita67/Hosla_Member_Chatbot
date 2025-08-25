from app.utils.member_info import greet_user_and_show_active_members

# Only pass image directory now
img_dir = "data/Hosla_Members_Pic"

username = input("Enter your UserName: ")
greeting, pic_path, active_members = greet_user_and_show_active_members(img_dir, username)

print("\n" + greeting)
if pic_path:
    print(f"🖼️ Profile picture found at: {pic_path}")
else:
    print("⚠️ No profile picture available.")

print("\n🔆 Active Members:")
for member in active_members:
    print("•", member)
