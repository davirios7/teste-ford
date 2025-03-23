import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import FactWarranties
from app.core.database import get_db
from sqlmodel import Session
from datetime import date


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


# Teste de contagem de warranties por vehicle_id
def test_count_warranties_by_vehicle(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/warranties/count-by-vehicle", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum vehicle_id
    assert len(response_json) >= 0
    # Verifique se o formato está correto (vehicle_id -> contagem)
    for vehicle_id, count in response_json.items():
        assert isinstance(int(vehicle_id), int)
        assert isinstance(count, int)


# Teste de contagem de warranties por part_id
def test_count_warranties_by_part(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/warranties/count-by-part", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum part_id
    assert len(response_json) >= 0
    # Verifique se o formato está correto (part_id -> contagem)
    for part_id, count in response_json.items():
        assert isinstance(int(part_id), int)
        assert isinstance(count, int)


# Teste de contagem de warranties por localização
def test_count_warranties_by_location(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/warranties/count-by-location", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém alguma localização
    assert len(response_json) >= 0
    # Verifique se o formato está correto (localização -> contagem)
    for location_id, count in response_json.items():
        assert isinstance(int(location_id), int)
        assert isinstance(count, int)


# Teste de contagem de warranties por ano
def test_count_warranties_by_year(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/warranties/count-by-year", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum ano
    assert len(response_json) >= 0
    # Verifique se o formato está correto (ano -> contagem)
    for year, count in response_json.items():
        assert "Year" in year
        year_number = int(year.split(" ")[1])
        assert isinstance(year_number, int)
        assert isinstance(count, int)
