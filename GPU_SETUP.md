# GPU Setup Guide - PoC Multi-Agentes

## ✅ Status Atual
- **GPU Detectada**: NVIDIA GeForce RTX 3050 Laptop GPU
- **CUDA Version**: 13.0
- **PyTorch Status**: ✅ Instalado com suporte CUDA
- **torch.cuda.is_available()**: ✅ True

---

## 🚀 Quick Start

### 1. Ativar Virtual Environment

```bash
source mult-agent/bin/activate
```

### 2. Verificar GPU
```bash
python3 scripts/test_gpu.py
```

Saída esperada:
```
nvidia-smi output:
 GPU 0: NVIDIA GeForce RTX 3050 Laptop GPU (...)
torch.cuda.is_available(): True
Device: NVIDIA GeForce RTX 3050 Laptop GPU
```

---

## 💡 Como Usar GPU no Seu Código

### Importar o helper module

```python
from agents.backend.device import get_torch_device, to_torch_device
```

### Exemplo 1: Enviar modelo para GPU

```python
import torch
from agents.backend.device import get_torch_device

# Obter device (cuda se disponível, caso contrário cpu)
device = get_torch_device()

# Carregar modelo (exemplo com um modelo simples)
model = torch.nn.Linear(10, 5)
model.to(device)  # ou: model = model.to(device)

# Dados
input_data = torch.randn(32, 10)
input_data = input_data.to(device)

# Forward pass na GPU
output = model(input_data)
print(f"Output device: {output.device}")  # cuda:0
```

### Exemplo 2: Usar com modelos pré-treinados (Hugging Face)

```python
from transformers import AutoModel, AutoTokenizer
from agents.backend.device import get_torch_device

device = get_torch_device()

# Carregar modelo e tokenizer
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.to(device)

# Tokenizar e enviar para GPU
inputs = tokenizer("Hello world!", return_tensors="pt")
inputs = {k: v.to(device) for k, v in inputs.items()}

# Forward pass
outputs = model(**inputs)
```

### Exemplo 3: Processar dados em batches na GPU

```python
import torch
from agents.backend.device import get_torch_device, to_torch_device

device = get_torch_device()
model = torch.nn.Sequential(
    torch.nn.Linear(784, 128),
    torch.nn.ReLU(),
    torch.nn.Linear(128, 10)
).to(device)

# Simular dados
batch_size = 64
num_batches = 100

for batch_idx in range(num_batches):
    X = torch.randn(batch_size, 784)
    
    # Enviar para GPU
    X = X.to(device)
    
    # Forward pass
    output = model(X)
    print(f"Batch {batch_idx}, Output shape: {output.shape}, Device: {output.device}")
```

---

## 🔧 Controlar Qual GPU Usar

### Usar apenas GPU 0 (padrão)
```bash
CUDA_VISIBLE_DEVICES=0 python3 seu_script.py
```

### Usar apenas GPU 1 (se houver múltiplas)
```bash
CUDA_VISIBLE_DEVICES=1 python3 seu_script.py
```

### Desabilitar GPU (forçar CPU)
```bash
CUDA_VISIBLE_DEVICES="" python3 seu_script.py
```

Ou no código:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

---

## 📊 Monitorar Uso de GPU Durante Execução

Em outro terminal:
```bash
# Monitoramento contínuo (tipo `top` para GPU)
watch -n 0.5 nvidia-smi
```

Ou uma vez:
```bash
nvidia-smi
```

---

## 🐍 Usando GPU com FastAPI / Backend

Se você tiver rotas FastAPI que carregam modelos:

```python
# main.py ou seu arquivo de rotas
from fastapi import FastAPI, HTTPException
from agents.backend.device import get_torch_device
import torch

app = FastAPI()

# Carregar modelo uma vez ao iniciar
device = get_torch_device()
model = torch.nn.Linear(10, 5).to(device)

@app.post("/predict")
async def predict(data: list):
    try:
        x = torch.tensor(data, dtype=torch.float32).to(device)
        with torch.no_grad():
            output = model(x)
        return {"prediction": output.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🐛 Troubleshooting

### PyTorch não detecta GPU
```bash
python3 -c "import torch; print(torch.cuda.is_available())"
```
Se retornar `False`:
- Verifique drivers: `nvidia-smi`
- Reinstale PyTorch com CUDA correto

### CUDA Out of Memory
```python
import torch
torch.cuda.empty_cache()  # Liberar memória não usada
```

Ou reduza batch size:
```python
batch_size = 32  # reduzir de 64 para 32
```

### Ver versão CUDA instalada
```bash
nvidia-smi
# ou
python3 -c "import torch; print(torch.version.cuda)"
```

---

## 📚 Módulo Helper: `agents/backend/device.py`

Funções disponíveis:

| Função | Descrição |
|--------|-----------|
| `list_gpus()` | Retorna saída de `nvidia-smi -L` |
| `get_torch_device()` | Retorna `torch.device('cuda')` ou `torch.device('cpu')` |
| `to_torch_device(obj, device)` | Move modelo/tensor/lista para device |
| `setup_tf_gpu_memory_growth()` | Ativa memory growth para TensorFlow (se instalado) |

---

## ✨ Próximos Passos

1. **Adapte suas rotas/agentes** para usar `device.get_torch_device()`
2. **Teste performance** comparando CPU vs GPU
3. **Monitore uso** com `nvidia-smi` durante execução
4. **Otimize batch size** conforme disponibilidade de VRAM

---

Sucesso! 🚀
