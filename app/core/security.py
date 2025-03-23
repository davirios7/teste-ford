from passlib.context import CryptContext

# Configuração do Passlib para criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash da senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verifica se a senha informada corresponde ao hash armazenado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
