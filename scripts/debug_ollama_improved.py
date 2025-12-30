"""Solução: Agente com suporte melhorado para geração de arquivos via Ollama.

O problema: Ollama/Mistral não sabe naturalmente como usar FileTools do agno.
A solução: Instanciar agentes com instruções explícitas sobre como criar arquivos.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools

load_dotenv()

# Definir diretório de teste
test_dir = Path("./test_output_improved")
test_dir.mkdir(exist_ok=True)

print("🔧 Criando agente com instruções EXPLÍCITAS sobre FileTools")
print(f"📁 Diretório: {test_dir.absolute()}")
print("=" * 70)

# Instruções MUITO explícitas sobre como usar FileTools
improved_instructions = [
    "Você é um desenvolvedor Python senior.",
    "Quando solicitado a criar um arquivo, SEMPRE use a ferramenta 'FileTools' disponível.",
    "A ferramenta FileTools permite: write_file(file_path, content), read_file(file_path), list_files()",
    "IMPORTANTE: Você DEVE usar essas ferramentas para criar/modificar arquivos.",
    "Exemplo: Para criar hello.py com conteúdo, use: write_file('hello.py', 'print(\"Hello\")')",
    "Forneça código completo e funcional.",
    "Se solicitado a criar múltiplos arquivos, crie todos eles usando FileTools.",
]

# Criar agente com instruções melhoradas
agent = Agent(
    name="File Generator Agent",
    model=Ollama(
        id=os.getenv("OLLAMA_MODEL", "mistral-small"),
    ),
    tools=[FileTools(base_dir=test_dir)],
    instructions=improved_instructions,
    markdown=True,
)

# Teste 1: Criar arquivo simples
print("\n✍️  TESTE 1: Criar hello.py")
print("-" * 70)
response1 = agent.run(
    "Crie um arquivo Python chamado 'hello.py' que imprime 'Hello, World My Friend!'"
)
print(f"Resposta:\n{response1}")

hello_file = test_dir / "hello.py"
if hello_file.exists():
    print(f"\n✅ Arquivo criado!")
    print(f"Conteúdo:\n{hello_file.read_text()}")
else:
    print(f"\n❌ Arquivo NÃO foi criado")

# Teste 2: Criar arquivo FastAPI
print("\n✍️  TESTE 2: Criar main.py com FastAPI")
print("-" * 70)
response2 = agent.run(
    "Crie um arquivo 'main.py' com uma API FastAPI simples com um endpoint GET /items que retorna uma lista de items"
)
print(f"Resposta:\n{response2}")

main_file = test_dir / "main.py"
if main_file.exists():
    print(f"\n✅ Arquivo criado!")
    content = main_file.read_text()
    print(f"Conteúdo (primeiras 40 linhas):\n" + "\n".join(content.split("\n")[:40]))
else:
    print(f"\n❌ Arquivo NÃO foi criado")

# Teste 3: Criar múltiplos arquivos
print("\n✍️  TESTE 3: Criar múltiplos arquivos")
print("-" * 70)
response3 = agent.run(
    "Crie 2 arquivos: 'models.py' com uma classe Task, e 'schemas.py' com um Pydantic schema para Task"
)
print(f"Resposta:\n{response3}")

# Verificar
print("\n📂 Arquivos gerados:")
for f in sorted(test_dir.glob("*")):
    print(f"  ✓ {f.name} ({f.stat().st_size} bytes)")

print("\n" + "=" * 70)
print("🔍 ANÁLISE:")
print("  Se os arquivos foram criados: FileTools está funcionando!")
print("  Se NÃO foram criados: O modelo pode não estar seguindo instruções de tool-use")
print("\nSolução alternativa: Usar LLMs mais poderosos (GPT-4, Claude) ou")
print("ajustar formato de tool-calling do ollama/mistral")
