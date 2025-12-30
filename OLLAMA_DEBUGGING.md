# 🔧 Guia: Ollama Não Gera Arquivos - Causas e Soluções

## ❌ O Problema

Você configurou agentes com Ollama + FileTools, mas os arquivos não estão sendo gerados. Isto é comum e tem **múltiplas causas**.

---

## 🔍 Diagnóstico

### 1️⃣ **FileTools Espera `Path`, Não String**

**Erro:** `AttributeError: 'str' object has no attribute 'resolve'`

**Causa:** Você estava passando `backend_dir` (string) em vez de `Path(backend_dir)`

**Solução:** ✅ **JÁ CORRIGIDA** em todos os agentes

```python
# ❌ ANTES (errado)
FileTools(base_dir=backend_dir)  # se backend_dir é string

# ✅ DEPOIS (correto)
backend_dir = Path(backend_dir) if isinstance(backend_dir, str) else backend_dir
FileTools(base_dir=backend_dir)  # agora é Path
```

---

### 2️⃣ **Modelo Ollama Não Sabe Usar FileTools**

**Causa:** Mistral-small (modelo padrão) foi treinado sem suporte nativo para tool-calling no formato que `agno` espera.

**Por que acontece:**
- OpenAI, Claude e outros LLMs têm suporte explícito para function/tool calling
- Ollama/Mistral usam outro formato (se suportarem)
- A biblioteca `agno` tenta se adaptar, mas nem sempre funciona perfeitamente

**Sintomas:**
- Ollama responde em texto normal, ignorando as tools
- Agente não chama `FileTools.write_file()`
- Arquivos nunca são criados

---

## 🛠️ Soluções Práticas

### Solução 1: Usar Modelos Ollama Maiores (Recomendado)

Tente trocar para um modelo maior com melhor suporte a tool-calling:

```bash
# Parar ollama atual
ollama stop

# Baixar modelo melhor (⚠️ ~7GB)
ollama pull neural-chat  # melhor com tools
# ou
ollama pull openhermes  # ótimo com tools
```

Depois atualizar `.env`:
```bash
OLLAMA_MODEL=neural-chat
# ou
OLLAMA_MODEL=openhermes
```

---

### Solução 2: Usar LLM Externo (Mais Confiável)

Se quer garantir que funcione, use OpenAI ou Groq (que têm suporte garantido para tool-calling):

```bash
# Instalar dependência extra
pip install openai

# Criar arquivo config.py
cat > config.py << 'EOF'
from agno.models.openai import OpenAIChat
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Opção 1: OpenAI (GPT-4 ou GPT-3.5)
LLM_MODEL = OpenAIChat(
    model="gpt-3.5-turbo",  # mais barato
    api_key=os.getenv("OPENAI_API_KEY")
)

# Opção 2: Groq (grátis, rápido!)
from agno.models.groq import Groq
LLM_MODEL = Groq(
    model="mixtral-8x7b-32768",
    api_key=os.getenv("GROQ_API_KEY")
)
EOF
```

Depois adaptar agents para usar esse config.

---

### Solução 3: Adicionar Prompting Mais Explícito

Se não quer trocar modelo, adicione instruções MUITO explícitas:

```python
from pathlib import Path
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.file import FileTools

def my_agent(base_dir):
    base_dir = Path(base_dir)
    
    # Instruções ultra-explícitas
    instructions = [
        "Você é um programador senior.",
        "Sempre que solicitado a criar arquivos, OBRIGATORIAMENTE use a ferramenta 'FileTools'.",
        "A ferramenta FileTools tem método: write_file(file_name, content_as_string)",
        "Exemplos:",
        "  - write_file('hello.py', 'print(\"Hi\")')",
        "  - write_file('main.py', 'from fastapi import FastAPI\\napp = FastAPI()')",
        "Você DEVE usar write_file para CADA arquivo que precisar criar.",
        "Forneça código completo e funcional.",
        "NUNCA tente criar arquivos de outra forma que não FileTools.",
    ]
    
    return Agent(
        name="File Creator",
        model=Ollama(
            id="mistral-small",
            temperature=0.1,  # Reduzir randomicidade
        ),
        tools=[FileTools(base_dir=base_dir)],
        instructions=instructions,
    )
```

---

### Solução 4: Usar Função Python Direta (Mais Simples)

Em vez de contar com agentes para gerar código, generate arquivos você mesmo e valide com o LLM:

```python
from agno.models.ollama import Ollama
from pathlib import Path

model = Ollama(id="mistral-small")

# 1. Gerar código com LLM
code = model.generate("Crie um endpoint FastAPI GET /users que retorna uma lista")

# 2. Salvar arquivo
base_dir = Path("./my_app/backend")
(base_dir / "main.py").write_text(code)

# 3. Validar com LLM
validation = model.generate(f"Este código Python está correto? {code[:500]}")
print(validation)
```

---

## 📋 Recomendação para Seu Projeto

### Curto Prazo (Agora)
1. ✅ **Já feito:** Corrigir FileTools para usar Path
2. 🔄 **Fazer:** Testar com instruções melhoradas
   ```bash
   python3 scripts/debug_ollama_improved.py
   ```
3. Se falhar → ir para Médio Prazo

### Médio Prazo (Hoje/Amanhã)
1. Trocar para modelo Ollama melhor (`neural-chat` ou `openhermes`)
2. Ou adicionar suporte para OpenAI/Groq como alternativa

### Longo Prazo (Opcional)
1. Implementar retry logic
2. Adicionar validação de código gerado
3. Fallback para templates se LLM falhar

---

## 🧪 Testar Mudanças

Após fazer mudanças, use estes scripts:

```bash
# Teste básico
python3 scripts/test_gpu.py

# Debug com instruções melhoradas
python3 scripts/debug_ollama_improved.py

# Rodar projeto completo
python3 main.py
```

---

## 📚 Referências

- [Agno Documentation](https://github.com/agno-agi/agno)
- [Ollama Models](https://ollama.ai/library)
- [Neural-Chat Model](https://ollama.ai/library/neural-chat)
- [Function Calling with LLMs](https://platform.openai.com/docs/guides/function-calling)

---

**Próximo passo:** Rode o teste `debug_ollama_improved.py` e veja se funciona!
