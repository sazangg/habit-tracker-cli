import base64
import json
import os
from pathlib import Path
from secrets import token_bytes
from typing import Any, Dict, List
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
from filelock import FileLock
from dotenv import load_dotenv

load_dotenv()


def derive_key(passphrase: str, salt: bytes, iterations: int = 390_000) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def new_fernet(passphrase: str, salt: bytes) -> Fernet:
    return Fernet(derive_key(passphrase, salt))


def get_passphrase() -> str:
    pw = os.getenv("PASSPHRASE")
    if pw:
        return pw

    raise ValueError("PASSPHRASE not defined in the environment variables")


class EncryptedJSONRepo:
    @classmethod
    def load_data(cls, path: Path) -> List[Dict[str, Any]]:
        if not path.exists() or path.stat().st_size == 0:
            return []

        passphrase = get_passphrase()
        file_bytes = path.read_bytes()
        salt, cipher_text = file_bytes[:16], file_bytes[16:]
        f = new_fernet(passphrase, salt)
        try:
            plain_text = f.decrypt(cipher_text)
        except InvalidToken as e:
            raise ValueError("Wrong pass-phrase or corrupted file.") from e

        return json.loads(plain_text.decode())

    @classmethod
    def save_data(cls, data, path: Path) -> None:
        passphrase = get_passphrase()
        salt = token_bytes(16)
        f = new_fernet(passphrase, salt)
        json_data = json.dumps(data, indent=2).encode()
        cipher_text = f.encrypt(json_data)
        path.parent.mkdir(parents=True, exist_ok=True)

        lock = FileLock(path.with_suffix(".lock"))
        with lock:
            path.write_bytes(salt + cipher_text)
