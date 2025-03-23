import redis
from fastapi import HTTPException

# Variável global para o cliente Redis
redis_client = None


# Função para inicializar a conexão com o Redis
def init_cache():
    global redis_client
    if redis_client is None:  # Verifica se o cliente já foi inicializado
        redis_client = redis.StrictRedis(
            host="localhost", port=6379, db=0, decode_responses=True
        )
        # Teste de conexão para garantir que o Redis está disponível
        try:
            redis_client.ping()
            print("Redis conectado com sucesso!")
        except redis.exceptions.ConnectionError as e:
            raise HTTPException(status_code=500, detail="Erro ao conectar com o Redis")


# Função para armazenar um valor no cache com uma chave
def set_cache(key: str, value: str, expiration: int = 3600):
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Cache não inicializado.")
    try:
        redis_client.setex(key, expiration, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache Error: {str(e)}")


# Função para obter o valor do cache
def get_cache(key: str):
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Cache não inicializado.")
    try:
        return redis_client.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache Error: {str(e)}")


# Função para remover o valor do cache
def delete_cache(key: str):
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Cache não inicializado.")
    try:
        redis_client.delete(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache Error: {str(e)}")
