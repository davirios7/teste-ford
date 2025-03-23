from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta
from app.cache import delete_cache, set_cache

from app.core.database import get_db
from app.core.auth import (
    create_access_token,
    decode_access_token,
)
from app.core.security import (
    verify_password,
    hash_password,
)
from app.schemas.auth import LoginRequest, UserCreate
from app.services.user import get_user_by_username, create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Registro de novo usuário
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar se o nome de usuário já existe
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Verificar se o e-mail já existe
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already taken")

    # Hash da senha
    hashed_password = hash_password(user_data.password)

    # Criar o novo usuário
    user = create_user(db, user_data.username, user_data.email, hashed_password)

    return {"message": "User registered successfully", "user_id": user.id}


# Login e geração de token
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(hours=1)
    )

    # Armazena a sessão do usuário no cache (Redis)
    session_key = f"session_{access_token}"
    set_cache(session_key, user.username, expiration=3600)  # Expiração de 1 hora

    return {"access_token": access_token, "token_type": "bearer"}


# Recupera usuário autenticado
@router.get("/me")
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # Decodificar o token JWT
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Verificar se o usuário existe no banco
    username = payload.get("sub")
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Retornar os dados do usuário
    return {"username": user.username, "email": user.email}


# Função de Logout
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Obtém o usuário atual a partir do token JWT
    user = get_current_user(token, db)

    # Usando o token JWT como chave no cache (assumindo que a chave seja o token)
    session_key = f"session_{token}"

    # Remove a sessão do usuário do cache
    delete_cache(session_key)

    return {"message": "Logout successful"}
