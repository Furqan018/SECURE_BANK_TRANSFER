import os

print("📁 Current Directory:", os.getcwd())
print("\n📋 Files in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")

print("\n🔍 Checking for .env file:")
if os.path.exists('.env'):
    print("✅ .env file exists!")
    print("\n📄 Content of .env file:")
    with open('.env', 'r') as f:
        content = f.read()
        print(content)
else:
    print("❌ .env file NOT found!")
    
print("\n🔍 Checking for env files with different names:")
env_files = [f for f in os.listdir('.') if 'env' in f.lower()]
for file in env_files:
    print(f"  - {file}")