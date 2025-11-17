env_content = """ENCRYPTION_KEY=05ZIDP5VlbhbhLI1ZHRGwOZKB1UeJR8VaZwLsfpnvPM
B2_KEY_ID=00585cf99ffd52a0000000002
B2_APPLICATION_KEY=K005yiBMqwBcjYlS2lroSIXo72SOa3I
B2_BUCKET_NAME=bank
APP_SECRET_KEY=my_secure_banking_app_secret_123"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ .env file fixed!")