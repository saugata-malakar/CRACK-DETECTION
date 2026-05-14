"""
Quick OAuth Setup Checker
Run this to verify your Google OAuth configuration
"""

import os
import json

print("=" * 60)
print("🔐 Google OAuth Configuration Checker")
print("=" * 60)
print()

# Check for environment variables
client_id = os.environ.get('GOOGLE_CLIENT_ID')
client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

if client_id and client_secret:
    print("✅ Environment variables found!")
    print(f"   Client ID: {client_id[:20]}...")
    print(f"   Client Secret: {client_secret[:15]}...")
    print()
else:
    print("⚠️  Environment variables not found")
    print()
    print("📝 To set up Google OAuth:")
    print()
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project")
    print("3. Enable Google+ API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add redirect URI: http://localhost:5000/auth/google/callback")
    print()
    print("6. Then set environment variables:")
    print("   Windows:")
    print("   set GOOGLE_CLIENT_ID=your-client-id")
    print("   set GOOGLE_CLIENT_SECRET=your-client-secret")
    print()
    print("   Or create .env file:")
    print("   GOOGLE_CLIENT_ID=your-client-id")
    print("   GOOGLE_CLIENT_SECRET=your-client-secret")
    print()

# Check if client_secret.json exists
if os.path.exists('client_secret.json'):
    print("✅ client_secret.json file exists")
    try:
        with open('client_secret.json', 'r') as f:
            data = json.load(f)
            if 'web' in data:
                print("✅ OAuth configuration looks good!")
    except:
        print("⚠️  client_secret.json format issue")
else:
    print("ℹ️  client_secret.json will be created on first run")

print()
print("=" * 60)
print("📚 For detailed setup instructions, see:")
print("   GOOGLE_OAUTH_SETUP.md")
print("=" * 60)
print()

# Check dependencies
print("Checking dependencies...")
try:
    import google.oauth2
    import google_auth_oauthlib
    print("✅ Google OAuth libraries installed")
except ImportError:
    print("⚠️  Missing dependencies. Install with:")
    print("   pip install google-auth google-auth-oauthlib google-auth-httplib2")

print()
print("🚀 Ready to start? Run:")
print("   python app_commercial.py")
print()
