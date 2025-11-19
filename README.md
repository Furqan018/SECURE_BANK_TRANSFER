Secure Banking Transfer 🏦


A secure, enterprise-grade file transfer platform with military-grade encryption and cloud storage for banking institutions.

🚀 Features


🔒 Military-Grade Encryption: AES-256 encryption for all files

☁️ Cloud Storage: Backblaze B2 cloud integration

👤 User Authentication: Secure login and registration system

📤 Secure Uploads: Encrypted file uploads with unique File IDs

📥 Protected Downloads: Secure file retrieval and decryption

🗂️ File Management: User-specific file organization and tracking

🛠️ Technology Stack


Frontend: Streamlit

Backend: Python

Encryption: Cryptography (Fernet - AES-256)

Cloud Storage: Backblaze B2

Authentication: SHA-256 hashing

📋 Prerequisites


Python 3.7+

Backblaze B2 Account

Required Python packages:

bash
pip install streamlit cryptography b2sdk requests
⚙️ Installation
Clone the repository

bash
git clone <repository-url>
cd secure-banking-transfer
Install dependencies

bash
pip install -r requirements.txt
Configure Backblaze B2

Update B2_CONFIG in the script with your:

KEY_ID

APPLICATION_KEY

BUCKET_NAME

Run the application

bash
streamlit run app.py


🔐 Usage

Demo Login
Email: demo@bank.com

Password: Demo@123

File Upload Process
Navigate to Upload section

Select a file to upload

File is automatically encrypted with AES-256

Receive a unique File ID for future retrieval

File is securely stored in Backblaze B2 cloud

File Download Process
Go to Download section

Enter your File ID

File is retrieved from cloud storage

Automatic decryption occurs

Download the decrypted file

🏗️ Architecture

text
User → Streamlit UI → Python Backend → Encryption → Backblaze B2 Cloud
  ↓                                      ↓              ↓
Login/Register ← Fernet AES-256 ← File Processing ← Cloud Storage

🔒 Security Features


End-to-End Encryption: Files encrypted before cloud storage

Secure Authentication: SHA-256 password hashing

User Isolation: Separate file storage per user

Unique File IDs: Randomized identifiers for file access

Cloud Security: Backblaze B2 enterprise-grade storage

🎯 Key Components


Cloud Storage Class
Handles Backblaze B2 connection

Manages file upload/download operations

Error handling and reconnection logic

Banking App Class
User authentication and management

File encryption/decryption

Session management

UI rendering and navigation

Encryption System
Fernet (AES-256) encryption

Secure key management

Automatic encryption/decryption

🌐 Deployment


The application can be deployed on:

Streamlit Sharing

Heroku

AWS EC2

Google Cloud Platform

Any platform supporting Python web applications

🔧 Configuration
Update the B2_CONFIG dictionary with your Backblaze B2 credentials:

python
B2_CONFIG = {
    'KEY_ID': 'your-key-id',
    'APPLICATION_KEY': 'your-application-key', 
    'BUCKET_NAME': 'your-bucket-name'
}

📞 Support


For technical support or questions, please contact the development team.

📄 License


This project is licensed for banking and financial institution use.
