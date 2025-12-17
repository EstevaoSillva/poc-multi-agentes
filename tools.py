from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

def consultar_saldo_cliente(cliente_id: int) -> str:
  
    # Simulação de uma query ao banco
    dados_mock = {1: "R$ 1.500,00", 2: "R$ 12.000,00", 3: "R$ -50,00"}
    return dados_mock.get(cliente_id, "Cliente não encontrado")

def calcular_parcelamento(valor_total: float, qtd_parcelas: int) -> float:
   
    taxa = 1.02
    valor_final = valor_total * (taxa ** qtd_parcelas)
    return round(valor_final / qtd_parcelas, 2)

def enviar_email_gerente(assunto: str, corpo: str) -> str:
   
    print(f"\n[EMAIL ENVIADO] Assunto: {assunto} | Msg: {corpo}")
    return "E-mail enviado com sucesso."

# --- 2. Adicionando ao Agente ---
agente_bancario = Agent(
    name="Assistente Financeiro",
    model=Groq(id="openai/gpt-oss-120b"),
    # AQUI ESTÁ A MÁGICA: Basta passar a lista das funções
    tools=[consultar_saldo_cliente, calcular_parcelamento, enviar_email_gerente],
    instructions=[
        "Você é um assistente bancário útil.",
        "Antes de calcular parcelas, verifique o saldo do cliente.",
        "Se o saldo for negativo, notifique o gerente imediatamente."
    ],
    markdown=True
)
# --- 3. Executando o Teste (Cenário Complexo) ---
# O usuário pede algo que exige usar as tools em cadeia
print("--- Iniciando Atendimento ---")
agente_bancario.print_response(
    "O cliente ID 3 quer comprar uma TV de 2000 reais parcelada em 10 vezes. Posso prosseguir?"
)