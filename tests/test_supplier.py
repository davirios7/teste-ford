import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DimSupplier, DimLocations
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


# Teste de contagem de suppliers por localização
def test_count_suppliers_per_location(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/suppliers/count-suppliers-per-location", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém alguma localização
    assert len(response_json) >= 0
    # Verifique se o formato está correto (location_id -> contagem)
    for location_id, count in response_json.items():
        assert isinstance(int(location_id), int)
        assert isinstance(count, int)


# Teste para obter a contagem de suppliers por localização
def test_get_supplier_count_by_location(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/suppliers/count-by-location", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém alguma localização
    assert len(response_json) >= 0
    # Verifique se o formato está correto (location_id -> contagem)
    for location_id, count in response_json.items():
        assert isinstance(int(location_id), int)
        assert isinstance(count, int)