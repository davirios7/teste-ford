import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.models.user import User
from app.core.database import get_db
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# Gera um token JWT
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


# Decodifica o token JWT
def decode_access_token(token: str):
    try:
        # Decodifica o token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        # Verifica se o token está expirado
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise JWTError("Token has expired")
        return payload
    except JWTError as e:
        return None  # Se ocorrer erro de JWT (token inválido ou expirado), retorna None


# Função para obter o usuário a partir do token JWT
def get_user_from_token(token: str, db: Session) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    username = payload.get("sub")  # Geralmente, 'sub' contém o nome de usuário ou ID
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token doesn't contain username",
        )

    # Aqui você deve fazer uma consulta no banco de dados para buscar o usuário
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


# Função para obter o usuário atual da requisição
def get_current_user(db: Session, token: str) -> User:
    return get_user_from_token(token, db)
