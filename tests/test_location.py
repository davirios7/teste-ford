import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DimLocations
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


# Teste de contagem por país
def test_get_location_count_by_country(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/locations/count-by-country", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum país
    assert len(response_json) > 0
    # Verifique se o formato está correto (país -> contagem)
    for country, count in response_json.items():
        assert isinstance(country, str)
        assert isinstance(count, int)


# Teste de contagem de cidades únicas por país
def test_get_unique_cities_by_country(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/locations/unique-cities-by-country", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum país
    assert len(response_json) > 0
    # Verifique se o formato está correto (país -> contagem de cidades únicas)
    for country, count in response_json.items():
        assert isinstance(country, str)
        assert isinstance(count, int)


# Teste de contagem de províncias por país
def test_get_province_count_by_country(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/locations/count-provinces-by-country", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum país
    assert len(response_json) > 0
    # Verifique se o formato está correto (país -> contagem de províncias)
    for country, count in response_json.items():
        assert isinstance(country, str)
        assert isinstance(count, int)


# Teste de contagem por tipo de mercado
def test_get_location_count_by_market(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/locations/count-by-market", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum tipo de mercado
    assert len(response_json) > 0
    # Verifique se o formato está correto (mercado -> contagem)
    for market, count in response_json.items():
        assert isinstance(market, str)
        assert isinstance(count, int)
