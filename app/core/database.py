from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

# Criando a engine do banco de dados
engine = create_engine(settings.DATABASE_URL, echo=True)


# Função para criar as tabelas automaticamente
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependência para obter a sessão do banco de dados
def get_db():
    with Session(engine) as session:
        yield session
