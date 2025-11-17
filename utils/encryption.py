import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class EncryptionManager:
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())
    
    def encrypt_file(self, file_data: bytes) -> bytes:
        """Encrypt file data"""
        return self.fernet.encrypt(file_data)
    
    def decrypt_file(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data"""
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_filename(self, filename: str) -> str:
        """Encrypt filename for additional security"""
        encrypted_name = self.fernet.encrypt(filename.encode())
        return base64.urlsafe_b64encode(encrypted_name).decode()
    
    def decrypt_filename(self, encrypted_filename: str) -> str:
        """Decrypt filename"""
        encrypted_name = base64.urlsafe_b64decode(encrypted_filename.encode())
        return self.fernet.decrypt(encrypted_name).decode()