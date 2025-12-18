from pathlib import Path
from dotenv import load_dotenv
from teams.product_team import product_team

load_dotenv()

# Raiz fixa do projeto
APP_ROOT = Path("./my_app")
APP_ROOT.mkdir(exist_ok=True)

(APP_ROOT / "backend").mkdir(exist_ok=True)
(APP_ROOT / "frontend").mkdir(exist_ok=True)

print("🚀 Iniciando desenvolvimento...")
product_team.run(
    """
    Criar um aplicativo To-Do List com:
    - Backend FastAPI com CRUD
    - Frontend HTML/CSS/JS
    - Testes básicos
    """,
    stream=False,
    debug=True,
    debug_level=2

)
print("✅ Finalizado.")
