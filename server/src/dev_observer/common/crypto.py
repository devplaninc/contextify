import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class Encryptor:
    _secret: str

    def __init__(self, secret: str):
        self._secret = secret

    def _derive_key(self, salt: str) -> bytes:
        """Derive a key from the secret and salt using PBKDF2"""
        salt_bytes = salt.encode('utf-8')
        secret_bytes = self._secret.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_bytes))
        return key

    def encrypt(self, data: str, salt: str) -> str:
        key = self._derive_key(salt)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, data: str, salt: str) -> str:
        key = self._derive_key(salt)
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(data.encode('utf-8'))
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')