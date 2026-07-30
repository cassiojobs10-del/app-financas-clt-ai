from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from calculadora_clt import calcular_folha_usuario, converter_gasto_em_tempo

# Inicializa o aplicativo da API
app = FastAPI(
    title="API - Finanças Pessoais & Folha CLT",
    description="Motor financeiro para cálculo de remuneração líquida e custo em horas de vida.",
    version="1.0.0"
)

# ==========================================
# 1. MODELOS DE ENTRADA (O que a API recebe)
# ==========================================
class DadosFolhaInput(BaseModel):
    salario_bruto: float = Field(..., gt=0, description="Salário bruto mensal em reais")
    jornada_mensal: int = Field(220, gt=0, description="Horas trabalhadas no mês (ex: 220, 180)")
    dependentes: int = Field(0, ge=0, description="Número de dependentes para dedução do IRRF")

class ConversaoGastoInput(BaseModel):
    valor_gasto: float = Field(..., gt=0, description="Preço do produto/serviço em reais")
    hora_liquida: float = Field(..., gt=0, description="Valor da hora líquida do usuário")


# ==========================================
# 2. ROTAS DA API (Os endpoints do App)
# ==========================================
@app.get("/")
def status_api():
    """Verifica se a API está online."""
    return {"status": "online", "mensagem": "API Finanças CLT operacional!"}


@app.post("/api/v1/calcular-folha")
def rota_calcular_folha(dados: DadosFolhaInput):
    """
    Recebe salário bruto, jornada e dependentes e retorna o raio-X completo
    com salário líquido, INSS progressivo, IRRF e valores por hora/minuto.
    """
    try:
        resultado = calcular_folha_usuario(
            salario_bruto=dados.salario_bruto,
            jornada_mensal=dados.jornada_mensal,
            dependentes=dados.dependentes
        )
        return {"sucesso": True, "dados": resultado}
    except Exception as erro:
        raise HTTPException(status_code=400, detail=f"Erro no processamento do cálculo: {str(erro)}")


@app.post("/api/v1/custo-em-horas")
def rota_converter_gasto(dados: ConversaoGastoInput):
    """
    Converte o valor de uma despesa no tempo de vida (horas e minutos)
    necessário para pagá-la com base na hora líquida.
    """
    try:
        tempo_formatado = converter_gasto_em_tempo(
            valor_gasto=dados.valor_gasto,
            hora_liquida=dados.hora_liquida
        )
        return {
            "sucesso": True,
            "valor_gasto": dados.valor_gasto,
            "tempo_trabalho_necessario": tempo_formatado
        }
    except Exception as erro:
        raise HTTPException(status_code=400, detail=f"Erro na conversão: {str(erro)}")
