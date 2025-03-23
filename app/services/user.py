from sqlmodel import Session, select
from app.models.user import User


# Buscar usuário pelo nome de usuário
def get_user_by_username(db: Session, username: str):
    return db.exec(select(User).where(User.username == username)).first()


# Buscar usuário pelo email
def get_user_by_email(db: Session, email: str):
    return db.exec(select(User).where(User.email == email)).first()


# Criar um novo usuário
def create_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    user = User(username=username, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
