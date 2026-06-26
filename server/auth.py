"""Password verification using passlib bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode('utf-8'),
            hashed.encode('utf-8')
        )
    except ValueError as e:
        return False