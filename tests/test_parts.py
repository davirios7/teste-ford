import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DimParts
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


# Teste de contagem total de peças
def test_get_total_parts_count(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/parts/count", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem total de peças
    assert "total_parts" in response_json
    assert isinstance(response_json["total_parts"], int)


# Teste de contagem de peças por fornecedor
def test_get_parts_count_by_supplier(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/parts/count-by-supplier", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de peças por fornecedor
    assert len(response_json) > 0
    # Verifique se o formato está correto (fornecedor -> contagem de peças)
    for supplier, count in response_json.items():
        assert isinstance(supplier, str)
        assert isinstance(count, int)


# Teste de contagem de peças compradas pelo menos uma vez
def test_get_count_purchased_parts(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/parts/count-purchased", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de peças compradas
    assert "total_purchased_parts" in response_json
    assert isinstance(response_json["total_purchased_parts"], int)


# Teste de contagem de compras feitas por fornecedor
def test_get_purchases_count_by_supplier(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/parts/count-purchases-by-supplier", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém a contagem de compras por fornecedor
    assert len(response_json) > 0
    # Verifique se o formato está correto (fornecedor -> contagem de compras)
    for supplier, count in response_json.items():
        assert isinstance(supplier, str)
        assert isinstance(count, int)
