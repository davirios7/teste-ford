import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.auth import UserCreate, LoginRequest
from app.core.database import get_db
from sqlmodel import Session
from faker import Faker

fake = Faker()


# A função de configuração do cliente de testes
@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


# Teste para o registro de novo usuário
def test_register(client: TestClient):
    user_data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(length=10),
    }
    response = client.post("/api/auth/register", json=user_data)

    response_json = response.json()
    assert response.status_code == 201
    assert response_json["message"] == "User registered successfully"


# Teste de login
def test_login(client: TestClient):
    # Crie um usuário de teste previamente no banco de dados (pode ser dentro de uma fixture)
    user_data = {"username": "davirios123", "password": "1234567"}
    response = client.post("/api/auth/login", json=user_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Teste de recuperação do usuário autenticado
def test_get_current_user(client: TestClient):
    # Primeiro, faça login para obter um token válido
    login_data = {"username": "davirios123", "password": "1234567"}
    login_response = client.post("/api/auth/login", json=login_data)

    # Verificar se o login foi bem-sucedido
    assert login_response.status_code == 200

    # Acessar o token de acesso
    access_token = login_response.json().get("access_token")
    assert access_token is not None, "Access token not found in response"

    # Agora, use o token para fazer a requisição ao /me
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "username": "davirios123",
        "email": "davirios12345@alu.ufc.br",
    }


# Teste de logout
def test_logout(client: TestClient):
    # Primeiro, faça login para obter um token válido
    login_data = {"username": "davirios123", "password": "1234567"}
    login_response = client.post("/api/auth/login", json=login_data)

    # Verificar se o login foi bem-sucedido
    assert login_response.status_code == 200

    # Acessar o token de acesso
    access_token = login_response.json().get("access_token")
    assert access_token is not None, "Access token not found in response"

    # Agora, faça logout usando o token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
