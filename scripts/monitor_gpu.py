"""Monitor GPU usage in real-time while agents are running.

Run this in a separate terminal while your agents are executing:
    python3 scripts/monitor_gpu.py
"""
import subprocess
import time
import sys

def monitor_gpu():
    """Display GPU stats continuously."""
    try:
        while True:
            # Clear screen
            subprocess.run('clear' if sys.platform != 'win32' else 'cls', shell=True)
            
            # Show nvidia-smi output
            result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu,utilization.memory,compute_cap',
                                    '--format=csv,noheader,nounits'], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print("=" * 100)
                print(f"{'GPU':<5} {'Name':<40} {'Memory Used':<15} {'GPU %':<10} {'Mem %':<10}")
                print("=" * 100)
                
                for line in lines:
                    parts = line.split(', ')
                    gpu_idx = parts[0].strip()
                    gpu_name = parts[1].strip()[:35]
                    mem_used = f"{float(parts[2].strip()):.0f}MB"
                    mem_total = f"{float(parts[3].strip()):.0f}MB"
                    gpu_util = f"{float(parts[4].strip()):.1f}%"
                    mem_util = f"{float(parts[5].strip()):.1f}%"
                    
                    print(f"{gpu_idx:<5} {gpu_name:<40} {mem_used:>7} / {mem_total:<7} {gpu_util:>8} {mem_util:>8}")
                
                print("=" * 100)
                print("Processes usando GPU:")
                print("-" * 100)
                
                # Show processes
                proc_result = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_bus_id,process_name,pid,used_memory',
                                            '--format=csv,noheader,nounits'],
                                           capture_output=True, text=True)
                
                if proc_result.returncode == 0 and proc_result.stdout.strip():
                    for proc_line in proc_result.stdout.strip().split('\n'):
                        parts = proc_line.split(', ')
                        if len(parts) >= 4:
                            gpu_bus = parts[0].strip()
                            proc_name = parts[1].strip()[:40]
                            pid = parts[2].strip()
                            mem = f"{float(parts[3].strip()):.0f}MB"
                            print(f"  GPU {gpu_bus} | PID {pid:<8} | {proc_name:<40} | {mem:>8}")
                else:
                    print("  Nenhum processo usando GPU")
                
                print("=" * 100)
                print(f"Atualizado às {time.strftime('%H:%M:%S')} | Pressione Ctrl+C para sair")
                time.sleep(1)
            else:
                print("nvidia-smi não encontrado ou GPU não disponível")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\nMonitoramento encerrado.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    monitor_gpu()
