from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from jose import jwt    
from app.core.config import JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def _normalize_password_for_bcrypt(password: str) -> str:
    """bcrypt only accepts passwords up to 72 bytes. Truncate safely to avoid runtime errors."""
    encoded = password.encode("utf-8")[:72]
    return encoded.decode("utf-8", errors="ignore")


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=60
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""Convert a plain-text password into a secure hash."""
def hash_password(password: str):
    normalized_password = _normalize_password_for_bcrypt(password)
    return pwd_context.hash(normalized_password)


"""Compare the user's password with the stored hash."""
def verify_password(plain_password: str, hashed_password: str):
    normalized_password = _normalize_password_for_bcrypt(plain_password)
    return pwd_context.verify(normalized_password, hashed_password)

