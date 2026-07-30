from dataclasses import dataclass
from typing import List, Dict

# ==========================================
# 1. TABELAS DE IMPOSTOS (Vigentes / Base)
# ==========================================
TABELA_INSS = [
    {"piso": 0.00, "teto": 1412.00, "aliquota": 0.075},
    {"piso": 1412.00, "teto": 2666.68, "aliquota": 0.090},
    {"piso": 2666.68, "teto": 4000.03, "aliquota": 0.120},
    {"piso": 4000.03, "teto": 7786.02, "aliquota": 0.140},
]

TABELA_IRRF = [
    {"piso": 0.00, "teto": 2259.20, "aliquota": 0.000, "deducao": 0.00},
    {"piso": 2259.20, "teto": 2826.65, "aliquota": 0.075, "deducao": 169.44},
    {"piso": 2826.65, "teto": 3751.05, "aliquota": 0.150, "deducao": 381.44},
    {"piso": 3751.05, "teto": 4664.68, "aliquota": 0.225, "deducao": 662.77},
    {"piso": 4664.68, "teto": float("inf"), "aliquota": 0.275, "deducao": 896.00},
]

DEDUCAO_POR_DEPENDENTE = 189.59


# ==========================================
# 2. ALGORITMOS DE CÁLCULO
# ==========================================
def calcular_inss_progressivo(salario_bruto: float) -> float:
    inss_total = 0.0
    for faixa in TABELA_INSS:
        if salario_bruto > faixa["piso"]:
            base_calculo = min(salario_bruto, faixa["teto"]) - faixa["piso"]
            inss_total += base_calculo * faixa["aliquota"]
        if salario_bruto <= faixa["teto"]:
            break
    return round(inss_total, 2)


def calcular_irrf(salario_bruto: float, inss: float, dependentes: int) -> float:
    base_irrf = salario_bruto - inss - (dependentes * DEDUCAO_POR_DEPENDENTE)
    if base_irrf <= 0:
        return 0.0
        
    for faixa in TABELA_IRRF:
        if faixa["piso"] < base_irrf <= faixa["teto"]:
            irrf = (base_irrf * faixa["aliquota"]) - faixa["deducao"]
            return round(max(0.0, irrf), 2)
    return 0.0


def calcular_folha_usuario(salario_bruto: float, jornada_mensal: int = 220, dependentes: int = 0) -> dict:
    inss = calcular_inss_progressivo(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss, dependentes)
    salario_liquido = round(salario_bruto - inss - irrf, 2)
    
    hora_bruta = round(salario_bruto / jornada_mensal, 2)
    hora_liquida = round(salario_liquido / jornada_mensal, 2)
    minuto_liquido = round(hora_liquida / 60, 4)
    
    return {
        "salario_bruto": salario_bruto,
        "salario_liquido": salario_liquido,
        "descontos": {
            "inss": inss,
            "irrf": irrf,
            "total_impostos": round(inss + irrf, 2)
        },
        "jornada_mensal": jornada_mensal,
        "valor_hora_bruta": hora_bruta,
        "valor_hora_liquida": hora_liquida,
        "valor_minuto_liquido": minuto_liquido
    }


def converter_gasto_em_tempo(valor_gasto: float, hora_liquida: float) -> str:
    total_minutos = round((valor_gasto / hora_liquida) * 60)
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas}h {minutos}min"


if __name__ == "__main__":
    resultado = calcular_folha_usuario(salario_bruto=4500.00, jornada_mensal=220, dependentes=0)
    
    print("--- RAIO-X DO SALÁRIO CLT ---")
    print(f"Salário Bruto:   R$ {resultado['salario_bruto']:,.2f}")
    print(f"Desconto INSS: - R$ {resultado['descontos']['inss']:,.2f}")
    print(f"Desconto IRRF: - R$ {resultado['descontos']['irrf']:,.2f}")
    print(f"Salário Líquido: R$ {resultado['salario_liquido']:,.2f}")
    print("---------------------------------")
    print(f"Valor da Hora Líquida: R$ {resultado['valor_hora_liquida']:,.2f}/h")
    
    jantar = 150.00
    tempo_gasto = converter_gasto_em_tempo(jantar, resultado['valor_hora_liquida'])
    print(f"Um jantar de R$ {jantar:.2f} custa: {tempo_gasto} de trabalho líquido!")
