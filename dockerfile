# Usa a imagem oficial do Python
FROM python:3.13.2

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Atualiza e instala pacotes necessários
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    netcat-openbsd \
    redis-server \
    postgresql-client && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH"

# Adiciona o Rust ao PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copia os arquivos do projeto para dentro do container
COPY . . 

# Copia o entrypoint.sh para o container e dá permissão de execução
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do FastAPI
EXPOSE 8001

# Define o entrypoint para o script
ENTRYPOINT ["/app/entrypoint.sh"]
