import hashlib
import streamlit as st

class AuthManager:
    def __init__(self):
        self.users = self._load_demo_users()
    
    def _load_demo_users(self):
        """Load demo users with hashed passwords"""
        return {
            "demo@bank.com": {
                "password": self._hash_password("Demo@123"),
                "name": "Demo User"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, email: str, password: str) -> bool:
        """Verify user credentials"""
        if email in self.users:
            hashed_password = self._hash_password(password)
            return self.users[email]["password"] == hashed_password
        return False
    
    def register_user(self, email: str, password: str, name: str):
        """Register new user (for future enhancement)"""
        if email not in self.users:
            self.users[email] = {
                "password": self._hash_password(password),
                "name": name
            }
            return True
        return False