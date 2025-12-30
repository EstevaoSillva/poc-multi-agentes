"""Exemplo: Como verificar que os agentes estão usando GPU.

Demonstra diferentes formas de rastrear uso de GPU.
"""
import logging
from agents.backend.device import get_torch_device, to_torch_device, print_device_info
import torch

# Ativar logging para ver mensagens de rastreamento
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

def example_1_basico():
    """Forma mais simples de verificar device."""
    print("\n" + "="*60)
    print("EXEMPLO 1: Verificação Básica")
    print("="*60)
    
    device = get_torch_device()
    print(f"Device atual: {device}")
    print(f"Type: {type(device)}")
    
    if torch.cuda.is_available():
        print(f"✅ GPU está sendo usada!")
    else:
        print("⚠️  CPU sendo usada")


def example_2_com_modelo():
    """Exemplo com modelo PyTorch."""
    print("\n" + "="*60)
    print("EXEMPLO 2: Modelo na GPU")
    print("="*60)
    
    device = get_torch_device()
    
    # Criar modelo
    model = torch.nn.Sequential(
        torch.nn.Linear(768, 256),
        torch.nn.ReLU(),
        torch.nn.Linear(256, 10)
    )
    
    # Mover para device (com logging)
    model = to_torch_device(model, device, log_name="modelo_bert")
    
    # Verificar onde o modelo está
    first_param = next(model.parameters())
    print(f"Parâmetros do modelo estão em: {first_param.device}")
    
    # Testar forward pass
    batch = torch.randn(4, 768).to(device)
    output = model(batch)
    print(f"Output device: {output.device}")


def example_3_monitoramento():
    """Exemplo com monitoramento de memória."""
    print("\n" + "="*60)
    print("EXEMPLO 3: Monitoramento de GPU")
    print("="*60)
    
    print_device_info()
    
    # Alocar memória na GPU
    device = get_torch_device()
    if device.type == 'cuda':
        tensor = torch.randn(1000, 1000).to(device)
        print(f"Tensor de 1000x1000 alocado na GPU")
        print_device_info()
        del tensor
        torch.cuda.empty_cache()
        print("Tensor deletado e cache limpo")
        print_device_info()


def example_4_batch_processing():
    """Exemplo processando batches na GPU."""
    print("\n" + "="*60)
    print("EXEMPLO 4: Processamento de Batch")
    print("="*60)
    
    device = get_torch_device()
    model = torch.nn.Linear(10, 1).to(device)
    
    # Simular processamento de 3 batches
    for i in range(3):
        batch = torch.randn(32, 10).to(device)
        output = model(batch)
        print(f"Batch {i}: Input {batch.device}, Output {output.device}")


def example_5_comparar_tempo():
    """Comparar tempo de execução CPU vs GPU."""
    print("\n" + "="*60)
    print("EXEMPLO 5: Benchmark CPU vs GPU")
    print("="*60)
    
    import time
    
    # Teste na CPU
    device_cpu = torch.device('cpu')
    model_cpu = torch.nn.Sequential(
        torch.nn.Linear(1024, 512),
        torch.nn.ReLU(),
        torch.nn.Linear(512, 256)
    ).to(device_cpu)
    
    # Teste na GPU
    device_gpu = get_torch_device()
    model_gpu = torch.nn.Sequential(
        torch.nn.Linear(1024, 512),
        torch.nn.ReLU(),
        torch.nn.Linear(512, 256)
    ).to(device_gpu)
    
    # Benchmark
    iterations = 100
    batch_size = 64
    
    # CPU
    start = time.time()
    for _ in range(iterations):
        x = torch.randn(batch_size, 1024).to(device_cpu)
        _ = model_cpu(x)
    cpu_time = time.time() - start
    
    # GPU
    torch.cuda.synchronize() if device_gpu.type == 'cuda' else None
    start = time.time()
    for _ in range(iterations):
        x = torch.randn(batch_size, 1024).to(device_gpu)
        _ = model_gpu(x)
    torch.cuda.synchronize() if device_gpu.type == 'cuda' else None
    gpu_time = time.time() - start
    
    print(f"CPU: {cpu_time:.4f}s")
    print(f"GPU: {gpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")


def main():
    """Executar todos os exemplos."""
    print("\n\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "RASTREAMENTO DE GPU - EXEMPLOS" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    example_1_basico()
    example_2_com_modelo()
    example_3_monitoramento()
    example_4_batch_processing()
    
    if torch.cuda.is_available():
        example_5_comparar_tempo()
    else:
        print("\n⚠️  GPU não disponível - benchmark não executado")
    
    print("\n" + "="*60)
    print("✅ Exemplos concluídos!")
    print("="*60)
    print("\nPara monitorar GPU em tempo real durante execução:")
    print("  python3 scripts/monitor_gpu.py")
    print("\n")


if __name__ == '__main__':
    main()
