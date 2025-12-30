"""Debug script para verificar se ollama consegue gerar arquivos via agentes."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Criar diretório de teste
test_dir = Path("./test_output")
test_dir.mkdir(exist_ok=True)

print(f"🔍 Testando geração de arquivos com Ollama")
print(f"📁 Diretório: {test_dir.absolute()}")
print(f"🤖 Model: {os.getenv('OLLAMA_MODEL')}")
print("=" * 60)

# Criar agente com FileTools
agent = Agent(
    name="Test Agent",
    model=Ollama(id=os.getenv("OLLAMA_MODEL", "mistral-small")),
    tools=[FileTools(base_dir=test_dir)],  # FileTools espera Path, não str
    instructions=[
        "Você é um desenvolvedor Python.",
        "Você deve criar arquivos quando solicitado.",
        "Use as ferramentas disponíveis para escrever arquivos.",
    ],
)

# Teste 1: Criar arquivo simples
print("\n📝 Teste 1: Criando arquivo Python simples...")
response1 = agent.run(
    "Crie um arquivo chamado 'hello.py' com um programa Python que imprime 'Hello, World!'"
)
print(f"Resposta: {response1}")
print(f"Arquivo criado? {(test_dir / 'hello.py').exists()}")
if (test_dir / 'hello.py').exists():
    print(f"Conteúdo:\n{(test_dir / 'hello.py').read_text()}")

# Teste 2: Criar arquivo mais complexo
print("\n📝 Teste 2: Criando arquivo FastAPI...")
response2 = agent.run(
    "Crie um arquivo 'main.py' com uma API FastAPI simples com 2 endpoints: GET /hello e POST /users"
)
print(f"Resposta: {response2}")
print(f"Arquivo criado? {(test_dir / 'main.py').exists()}")
if (test_dir / 'main.py').exists():
    print(f"Conteúdo (primeiras 30 linhas):\n{chr(10).join((test_dir / 'main.py').read_text().split(chr(10))[:30])}")

# Teste 3: Listar arquivos criados
print("\n📂 Arquivos criados em test_output:")
for f in test_dir.glob("*"):
    print(f"  - {f.name} ({f.stat().st_size} bytes)")

print("\n" + "=" * 60)
print("✅ Testes concluídos!")
print("\nSe os arquivos NÃO foram criados, possíveis causas:")
print("1. Ollama offline ou modelo não disponível")
print("2. FileTools não reconhecendo a sintaxe do modelo")
print("3. Prompt não incitando bem o modelo a usar FileTools")
