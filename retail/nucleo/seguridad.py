import hashlib
import bcrypt


def hash_contrasena(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    if _es_hash_bcrypt(hash_almacenado):
        return bcrypt.checkpw(contrasena.encode(), hash_almacenado.encode())
    return _es_hash_sha256_valido(contrasena, hash_almacenado)


def es_hash_sha256(hash_almacenado: str) -> bool:
    return len(hash_almacenado) == 64 and all(
        c in "0123456789abcdef" for c in hash_almacenado
    )


def _es_hash_bcrypt(hash_almacenado: str) -> bool:
    return hash_almacenado.startswith("$2")


def _es_hash_sha256_valido(contrasena: str, hash_almacenado: str) -> bool:
    return hash_almacenado == hashlib.sha256(contrasena.encode()).hexdigest()
