from __future__ import annotations

import base64
import hashlib
import os

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    _HAY_CRYPTOGRAPHY = True
except ModuleNotFoundError:
    _HAY_CRYPTOGRAPHY = False


def _clave_maestra() -> bytes:
    hostname = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "localhost"
    salt = b"InnobertRetail_salt_2026"
    if _HAY_CRYPTOGRAPHY:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000)
        return base64.urlsafe_b64encode(kdf.derive(hostname.encode()))
    else:
        return hashlib.pbkdf2_hmac("sha256", hostname.encode(), salt, 600_000)


def cifrar(texto: str) -> str:
    if not texto:
        return ""
    if _HAY_CRYPTOGRAPHY:
        f = Fernet(_clave_maestra())
        return f.encrypt(texto.encode()).decode()
    else:
        # Fallback: XOR con hash (NO escriptación fuerte, evita texto plano)
        clave = _clave_maestra()
        datos = texto.encode()
        return base64.urlsafe_b64encode(
            bytes(d ^ clave[i % len(clave)] for i, d in enumerate(datos))
        ).decode()


def descifrar(token: str) -> str:
    if not token:
        return ""
    try:
        if _HAY_CRYPTOGRAPHY:
            f = Fernet(_clave_maestra())
            return f.decrypt(token.encode()).decode()
        else:
            clave = _clave_maestra()
            datos = base64.urlsafe_b64decode(token.encode())
            return bytes(
                d ^ clave[i % len(clave)] for i, d in enumerate(datos)
            ).decode()
    except Exception:
        return ""
