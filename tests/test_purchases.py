import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DimPurchases
from app.core.database import get_db
from sqlmodel import Session


# A função de configuração do cliente de testes
@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


# Função auxiliar para realizar o login e obter o token de acesso
def login(client: TestClient):
    login_data = {"username": "davirios123", "password": "1234567"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


# Teste de contagem de compras por tipo
def test_get_purchase_count_by_type(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/purchases/count-by-type", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de compras por tipo
    assert len(response_json) > 0
    # Verifique se o formato está correto (tipo de compra -> contagem)
    for purchase_type, count in response_json.items():
        assert isinstance(purchase_type, str)
        assert isinstance(count, int)


# Teste de contagem de compras por ano
def test_get_purchase_count_by_year(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/purchases/count-by-year", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de compras por ano
    assert len(response_json) > 0
    # Verifique se o formato está correto (ano -> contagem)
    for year, count in response_json.items():
        assert isinstance(year, str)
        assert isinstance(count, int)


# Teste de contagem de compras por mês
def test_get_purchase_count_by_month(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/purchases/count-by-month", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de compras por mês
    assert len(response_json) > 0
    # Verifique se o formato está correto (mês -> contagem)
    for month, count in response_json.items():
        assert isinstance(month, str)
        assert isinstance(count, int)