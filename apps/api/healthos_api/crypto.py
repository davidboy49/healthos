import base64
import hashlib

from cryptography.fernet import Fernet

from healthos_api.config import get_settings


def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().token_encryption_key.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_token(token: str) -> str:
    return _fernet().encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(token: str) -> str:
    return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")

