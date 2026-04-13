# Usa uma imagem oficial com Python e suporte a CUDA
FROM nvidia/cuda:12.4.1-base-ubuntu22.04

# Instala o Python e o Pip (já que a imagem base é limpa)
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia o seu requirements.txt para dentro do container
COPY requirements.txt .

# Instala as dependências (usando o link que resolve o erro do Torch)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu130

# Copia o restante do seu código
COPY . .

# Comando para rodar seu script principal
CMD ["python3", "seu_script_principal.py"]