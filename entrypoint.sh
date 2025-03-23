#!/bin/bash

# Função para esperar o banco de dados PostgreSQL
wait_for_postgres() {
  echo "Aguardando o banco de dados PostgreSQL iniciar..."
  while ! nc -z db 5432; do
    sleep 0.1
  done
  echo "Banco de dados PostgreSQL está pronto!"
}

# Função para esperar o Redis
wait_for_redis() {
  echo "Aguardando o Redis iniciar..."
  while ! nc -z redis 6379; do
    sleep 0.1
  done
  echo "Redis está pronto!"
}

redis-server &

# Espera os serviços db e redis estarem prontos
wait_for_postgres
wait_for_redis

# Verifica se o banco de dados existe, cria se necessário
echo "Verificando se o banco de dados existe..."
psql postgresql://admin:admin@db:5432/postgres -c "SELECT 1 FROM pg_database WHERE datname = 'teste-ford';" | grep -q 1 || \
  psql postgresql://admin:admin@db:5432/postgres -c "CREATE DATABASE teste-ford;"

# Rodar as migrações
echo "Rodando migrações..."
alembic upgrade head

# Popular o banco de dados
echo "Popular banco de dados..."
python populate_db.py

# Iniciar a aplicação diretamente
echo "Iniciando a aplicação..."
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload