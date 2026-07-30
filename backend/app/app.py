import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="App Finanças CLT & IA",
    page_icon="💰",
    layout="centered"
)

# ==========================================
# LÓGICA DE CÁLCULO (TABELAS DE IMPOSTOS)
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

def calcular_clt(salario_bruto, jornada, dependentes):
    # Cálculo do INSS
    inss = 0.0
    for f in TABELA_INSS:
        if salario_bruto > f["piso"]:
            base = min(salario_bruto, f["teto"]) - f["piso"]
            inss += base * f["aliquota"]
        if salario_bruto <= f["teto"]:
            break
    inss = round(inss, 2)

    # Cálculo do IRRF
    base_irrf = salario_bruto - inss - (dependentes * DEDUCAO_POR_DEPENDENTE)
    irrf = 0.0
    if base_irrf > 0:
        for f in TABELA_IRRF:
            if f["piso"] < base_irrf <= f["teto"]:
                irrf = max(0.0, (base_irrf * f["aliquota"]) - f["deducao"])
                break
    irrf = round(irrf, 2)

    salario_liquido = round(salario_bruto - inss - irrf, 2)
    hora_liquida = round(salario_liquido / jornada, 2) if jornada > 0 else 0.0
    
    return salario_liquido, inss, irrf, hora_liquida

# ==========================================
# INTERFACE VISUAL (TELAS DO APP)
# ==========================================
st.title("💰 Meu Controle Financeiro & CLT")
st.write("Entenda seu ganho real e descubra quanto custam seus gastos em **tempo de vida trabalhado**.")

st.divider()

# --- SEÇÃO 1: PERFIL TRABALHISTA ---
st.subheader("1. Configure sua Renda")
col1, col2, col3 = st.columns(3)

with col1:
    salario_bruto = st.number_input("Salário Bruto (R$)", min_value=1000.0, value=4500.0, step=100.0)
with col2:
    jornada = st.selectbox("Jornada Mensal (Horas)", options=[220, 180, 160], index=0)
with col3:
    dependentes = st.number_input("Dependentes", min_value=0, value=0, step=1)

# Executando o cálculo instantâneo
sal_liquido, inss, irrf, hora_liq = calcular_clt(salario_bruto, jornada, dependentes)

st.divider()

# --- SEÇÃO 2: RAIO-X DO SALÁRIO ---
st.subheader("2. Seu Salário Real (Líquido)")
card1, card2, card3 = st.columns(3)

with card1:
    st.metric("Salário Líquido", f"R$ {sal_liquido:,.2f}", delta=f"Hora real: R$ {hora_liq:,.2f}")
with card2:
    st.metric("Desconto INSS", f"R$ {inss:,.2f}")
with card3:
    st.metric("Desconto IRRF", f"R$ {irrf:,.2f}")

st.divider()

# --- SEÇÃO 3: O DIFERENCIAL (CUSTO EM HORAS DE VIDA) ---
st.subheader("⏱️ Termômetro de Gastos: Custo em Horas de Vida")
st.write("Antes de fazer uma compra, descubra quanto tempo de trabalho líquido ela vai custar:")

col_gasto1, col_gasto2 = st.columns([1, 2])

with col_gasto1:
    valor_compra = st.number_input("Valor da despesa (R$)", min_value=1.0, value=150.0, step=10.0)

with col_gasto2:
    if hora_liq > 0:
        total_minutos = round((valor_compra / hora_liq) * 60)
        horas = total_minutos // 60
        minutos = total_minutos % 60
        
        st.info(f"💡 Para comprar algo de **R$ {valor_compra:,.2f}**, você precisará trabalhar exatamente:")
        st.header(f"⏳ **{horas} horas e {minutos} minutos**")
