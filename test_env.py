import os
from dotenv import load_dotenv

print("🔍 Testing .env file loading...")

# List files in current directory
print("\n📁 Files in current directory:")
for file in os.listdir('.'):
    if 'env' in file.lower() or file.endswith('.py'):
        print(f"  - {file}")

# Try to load .env file
try:
    load_dotenv()
    print("✅ dotenv loaded successfully!")
except Exception as e:
    print(f"❌ Error loading dotenv: {e}")

# Check each environment variable
print("\n🔧 Checking environment variables:")
env_vars = [
    'ENCRYPTION_KEY',
    'B2_KEY_ID', 
    'B2_APPLICATION_KEY',
    'B2_BUCKET_NAME',
    'APP_SECRET_KEY'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Found (length: {len(value)})")
    else:
        print(f"❌ {var}: NOT FOUND")

print("\n🎯 Test completed!")