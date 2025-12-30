"""Quick test that reports GPU and PyTorch availability.

Run: python3 scripts/test_gpu.py
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.backend import device


def main():
    print("nvidia-smi output:\n", device.list_gpus())

    td = device.get_torch_device()
    if td is None:
        print("PyTorch não instalado ou não disponível. Instale PyTorch para testar a GPU.")
        return

    import torch
    print("torch.cuda.is_available():", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Device:", torch.cuda.get_device_name(0))


if __name__ == '__main__':
    main()
