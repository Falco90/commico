from cryptography.fernet import Fernet
from app.core.settings import settings

fernet = Fernet(settings.GITHUB_TOKEN_ENCRYPTION_KEY)

def encrypt_github_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_github_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()
