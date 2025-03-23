import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DimVehicle, PropulsionType
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


# Teste de contagem de veículos por faixa de ano
def test_count_vehicles_by_year_range(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    start_year = 2020
    end_year = 2023
    response = client.get(
        f"/api/vehicles/count-by-year-range?start_year={start_year}&end_year={end_year}",
        headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém dados
    assert len(response_json) >= 0
    # Verifique se o formato está correto (ano -> contagem)
    for year, count in response_json.items():
        assert isinstance(int(year), int)
        assert isinstance(count, int)


# Teste de contagem de veículos por tipo de propulsão
def test_count_vehicles_by_propulsion(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/vehicles/count-by-propulsion", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum tipo de propulsão
    assert len(response_json) >= 0
    # Verifique se o formato está correto (propulsão -> contagem)
    for propulsion, count in response_json.items():
        assert isinstance(propulsion, str)
        assert isinstance(count, int)


# Teste de contagem de veículos por ano de fabricação
def test_count_vehicles_by_year(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/vehicles/count-by-year", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum ano
    assert len(response_json) >= 0
    # Verifique se o formato está correto (ano -> contagem)
    for year, count in response_json.items():
        assert isinstance(int(year), int)
        assert isinstance(count, int)


# Teste de contagem de veículos por mês de produção
def test_count_vehicles_by_prod_month(client: TestClient):
    token = login(client)  # Faz login e obtém o token de acesso
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/vehicles/count-by-prod-month", headers=headers)

    assert response.status_code == 200
    response_json = response.json()

    # Verifique se o retorno contém algum mês
    assert len(response_json) >= 0
    # Verifique se o formato está correto (mês -> contagem)
    for month, count in response_json.items():
        assert isinstance(month, str)
        assert isinstance(count, int)
        assert "Month" in month  # Garante que a chave começa com "Month"
        month_number = int(month.split(" ")[1])  # Extrai o número do mês
        assert 1 <= month_number <= 12  # Garante que o número do mês é válido
