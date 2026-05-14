"""
Setup Verification Script for CrackDetect AI Commercial Platform
Run this to verify all configurations are correct before starting the app
"""

import os
import sys

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_status(check, status, message=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check}")
    if message:
        print(f"   → {message}")

def check_dependencies():
    print_header("Checking Dependencies")
    
    dependencies = {
        'flask': 'Flask',
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'PIL': 'Pillow',
        'google.auth': 'Google Auth',
        'google_auth_oauthlib': 'Google OAuth',
        'requests': 'Requests'
    }
    
    all_installed = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print_status(f"{name}", True)
        except ImportError:
            print_status(f"{name}", False, f"Install with: pip install {module}")
            all_installed = False
    
    return all_installed

def check_files():
    print_header("Checking Required Files")
    
    required_files = {
        'app_commercial.py': 'Main application file',
        '03_model.py': 'Model definitions',
        'templates/commercial/base.html': 'Base template',
        'templates/commercial/home.html': 'Home page',
        'templates/commercial/login.html': 'Login page',
        'templates/commercial/register.html': 'Register page',
        'templates/commercial/dashboard.html': 'Dashboard',
        'templates/commercial/predict.html': 'Predict page',
        'templates/commercial/history.html': 'History page',
        'templates/commercial/compare.html': 'Compare page',
        'templates/commercial/pricing.html': 'Pricing page',
        'templates/commercial/features.html': 'Features page',
        'templates/commercial/api_docs.html': 'API docs',
        'templates/commercial/about.html': 'About page'
    }
    
    all_exist = True
    for file, description in required_files.items():
        exists = os.path.exists(file)
        print_status(f"{description} ({file})", exists)
        if not exists:
            all_exist = False
    
    return all_exist

def check_oauth_config():
    print_header("Checking OAuth Configuration")
    
    # Check if credentials are in app_commercial.py
    try:
        with open('app_commercial.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        google_client_id = '685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com'
        google_secret = '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'
        github_client_id = 'Ov23lisABjBsaidhXk1q'
        github_secret = '0d7d62e38cc652ebb0fd13901df125f3f7eba30a'
        
        checks = [
            (google_client_id in content, "Google Client ID configured"),
            (google_secret in content, "Google Client Secret configured"),
            (github_client_id in content, "GitHub Client ID configured"),
            (github_secret in content, "GitHub Client Secret configured"),
            ('/auth/google' in content, "Google OAuth route exists"),
            ('/auth/github' in content, "GitHub OAuth route exists"),
            ('/auth/google/callback' in content, "Google callback route exists"),
            ('/auth/github/callback' in content, "GitHub callback route exists")
        ]
        
        all_configured = True
        for status, message in checks:
            print_status(message, status)
            if not status:
                all_configured = False
        
        return all_configured
        
    except Exception as e:
        print_status("OAuth configuration check", False, str(e))
        return False

def check_model_files():
    print_header("Checking Model Files")
    
    checkpoint_exists = os.path.exists('checkpoints/best_model.pth')
    print_status("Model checkpoint (checkpoints/best_model.pth)", checkpoint_exists, 
                 "Will use pretrained models if not found" if not checkpoint_exists else "")
    
    return True  # Not critical

def print_oauth_instructions():
    print_header("OAuth Setup Instructions")
    
    print("\n📌 GOOGLE OAUTH SETUP:")
    print("   1. Go to: https://console.cloud.google.com/")
    print("   2. Navigate to: APIs & Services → Credentials")
    print("   3. Find Client ID: 685487767318-mug18aoiddj00r2bbn6n28c0qfe6lehd.apps.googleusercontent.com")
    print("   4. Add Authorized redirect URI:")
    print("      → http://localhost:5000/auth/google/callback")
    print("   5. Add Authorized JavaScript origin:")
    print("      → http://localhost:5000")
    print("   6. Click SAVE")
    
    print("\n📌 GITHUB OAUTH SETUP:")
    print("   1. Go to: https://github.com/settings/developers")
    print("   2. Find OAuth App: Crack AI")
    print("   3. Update Authorization callback URL:")
    print("      → http://localhost:5000/auth/github/callback")
    print("   4. Update Homepage URL:")
    print("      → http://localhost:5000")
    print("   5. Click Update application")

def main():
    print("\n" + "🚀"*35)
    print("  CrackDetect AI - Setup Verification")
    print("🚀"*35)
    
    # Run all checks
    deps_ok = check_dependencies()
    files_ok = check_files()
    oauth_ok = check_oauth_config()
    model_ok = check_model_files()
    
    # Summary
    print_header("Verification Summary")
    
    all_checks = [
        (deps_ok, "Dependencies"),
        (files_ok, "Required Files"),
        (oauth_ok, "OAuth Configuration"),
        (model_ok, "Model Files")
    ]
    
    all_passed = all(status for status, _ in all_checks)
    
    for status, name in all_checks:
        print_status(name, status)
    
    print("\n" + "="*70)
    
    if all_passed:
        print("\n✅ ALL CHECKS PASSED!")
        print("\n🎉 Your setup is complete and ready to run!")
        print("\n📝 Next steps:")
        print("   1. Configure OAuth redirect URIs (see instructions above)")
        print("   2. Run: python app_commercial.py")
        print("   3. Open: http://localhost:5000")
        print("\n" + "="*70 + "\n")
    else:
        print("\n⚠️  SOME CHECKS FAILED!")
        print("\n📝 Please fix the issues above before running the app.")
        print("\n💡 For detailed setup instructions, see: FINAL_SETUP.md")
        print("\n" + "="*70 + "\n")
        
        # Show OAuth instructions if OAuth check failed
        if not oauth_ok:
            print_oauth_instructions()
            print("\n" + "="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
