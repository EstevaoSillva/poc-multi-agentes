"""Utilities to detect and use GPU (PyTorch / TensorFlow) in the project.

This module avoids importing heavy ML libs at import-time and provides
helper functions to detect GPUs and move models/tensors to device.
"""
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


def list_gpus() -> Optional[str]:
    """Return `nvidia-smi -L` output if available, otherwise None."""
    try:
        import subprocess
        out = subprocess.check_output(["nvidia-smi", "-L"], stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return None


def get_torch_device() -> Optional[object]:
    """Return a torch.device if PyTorch is installed, else None.

    Use this to decide where to place models/tensors: 'cuda' if available, else 'cpu'.
    """
    try:
        import torch
    except Exception:
        return None
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Log device selection
    if device.type == "cuda":
        logger.info(f"✅ GPU detectada: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("⚠️  GPU não disponível - usando CPU")
    
    return device


def to_torch_device(obj: Any, device: Optional[object] = None, log_name: str = "") -> Any:
    """Move a torch `Module` or tensor or collection to `device`.

    Raises RuntimeError if PyTorch is not installed.
    
    Args:
        obj: PyTorch module, tensor, ou collection (list/tuple)
        device: torch.device alvo. Se None, usa get_torch_device()
        log_name: Nome para logging (ex: "modelo_bert", "batch_input")
    """
    try:
        import torch
    except Exception:
        raise RuntimeError("PyTorch não está instalado")

    if device is None:
        device = get_torch_device()
        if device is None:
            raise RuntimeError("PyTorch não disponível")

    # Modules and tensors have `.to()`
    if hasattr(obj, "to"):
        result = obj.to(device)
        if log_name:
            logger.debug(f"➜ Movido {log_name} para {device}")
        return result

    # For lists/tuples recurse
    if isinstance(obj, (list, tuple)):
        return type(obj)(to_torch_device(o, device) for o in obj)

    # Otherwise return as-is
    return obj


def print_device_info():
    """Print formatted device information."""
    try:
        import torch
        
        print("\n" + "="*60)
        print("🖥️  DEVICE INFORMATION")
        print("="*60)
        
        if torch.cuda.is_available():
            print(f"✅ GPU Disponível: {torch.cuda.get_device_name(0)}")
            print(f"   Memória Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            print(f"   Memória Alocada: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
            print(f"   Memória Reservada: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
            print(f"   Versão CUDA: {torch.version.cuda}")
        else:
            print("⚠️  GPU não disponível - usando CPU")
        
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Erro ao exibir informações de device: {e}")


def setup_tf_gpu_memory_growth() -> bool:
    """Enable memory growth for TensorFlow GPUs when TF is installed.

    Returns True if GPUs were found and growth was (attempted) configured, False otherwise.
    """
    try:
        import tensorflow as tf
    except Exception:
        return False

    try:
        gpus = tf.config.list_physical_devices("GPU")
        if not gpus:
            return False
        for g in gpus:
            try:
                tf.config.experimental.set_memory_growth(g, True)
                logger.info(f"✅ TensorFlow memory growth ativado para {g}")
            except Exception as e:
                logger.warning(f"Erro ao ativar memory growth: {e}")
        return True
    except Exception:
        return False


__all__ = [
    "list_gpus",
    "get_torch_device",
    "to_torch_device",
    "print_device_info",
    "setup_tf_gpu_memory_growth",
]

