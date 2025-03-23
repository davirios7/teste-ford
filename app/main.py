from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.routes import (
    location,
    parts,
    purchases,
    supplier,
    warranties,
    vehicle,
    auth,
)
from app.cache import get_cache, init_cache
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


# Usando o contexto lifespan para inicializar o cache
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando o cache...")
    init_cache()
    yield
    print("Encerrando a API...")


app = FastAPI(title="Teste Ford API - Davi Rios", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir acesso de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos os headers
)

# Definindo OAuth2PasswordBearer para autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Função para verificar o token e garantir que o usuário está autenticado
def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verifica se a sessão existe no Redis
    session_key = f"session_{token}"
    session = get_cache(session_key)

    if not session:
        raise HTTPException(status_code=401, detail="Session not found or expired")

    current_user: User = get_current_user(db=db, token=token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return current_user


app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(
    vehicle.router,
    prefix="/api",
    tags=["vehicles"],
    dependencies=[Depends(verify_token)],
)
app.include_router(
    parts.router, prefix="/api", tags=["parts"], dependencies=[Depends(verify_token)]
)
app.include_router(
    purchases.router,
    prefix="/api",
    tags=["purchases"],
    dependencies=[Depends(verify_token)],
)
app.include_router(
    location.router,
    prefix="/api",
    tags=["locations"],
    dependencies=[Depends(verify_token)],
)
app.include_router(
    supplier.router,
    prefix="/api",
    tags=["suppliers"],
    dependencies=[Depends(verify_token)],
)
app.include_router(
    warranties.router,
    prefix="/api",
    tags=["warranties"],
    dependencies=[Depends(verify_token)],
)


# Rota personalizada para lidar com erro 404
@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"detail": "URL not found. Please check the URL or request."},
        )
    raise exc


# Rota personalizada para lidar com métodos não permitidos
@app.exception_handler(StarletteHTTPException)
async def method_not_allowed_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={
                "detail": f"Método {request.method} não permitido na rota {request.url.path}"
            },
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
