# test_settings.py
from config import settings

print("🔍 Testing configuration...")
print(f"Discord Token: {'✅ Set' if settings.DISCORD_BOT_TOKEN else '❌ Missing'}")
print(f"Guild ID: {settings.GUILD_ID}")
print(f"Google Credentials: {settings.GOOGLE_CREDENTIALS_FILE}")
print(f"Guild Member Roles: {settings.GUILD_MEMBER_ROLE_IDS}")
print(f"Officer Roles: {settings.OFFICER_ROLE_IDS}")
print("\n✅ Configuration loaded successfully!")
