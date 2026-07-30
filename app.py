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

def calcular_clt(salario_base, jornada, dependentes, aplicar_irrf=True, horas_50=0.0, horas_100=0.0):
    # 1. Cálculo da hora normal e horas extras
    hora_normal = salario_base / jornada if jornada > 0 else 0.0
    valor_he_50 = round(horas_50 * (hora_normal * 1.5), 2)
    valor_he_100 = round(horas_100 * (hora_normal * 2.0), 2)
    total_horas_extras = round(valor_he_50 + valor_he_100, 2)
    
    # Salário bruto total para base de impostos
    salario_bruto_total = round(salario_base + total_horas_extras, 2)

    # 2. Cálculo do INSS
    inss = 0.0
    for f in TABELA_INSS:
        if salario_bruto_total > f["piso"]:
            base = min(salario_bruto_total, f["teto"]) - f["piso"]
            inss += base * f["aliquota"]
        if salario_bruto_total <= f["teto"]:
            break
    inss = round(inss, 2)

    # 3. Cálculo do IRRF
    irrf = 0.0
    if aplicar_irrf:
        base_irrf = salario_bruto_total - inss - (dependentes * DEDUCAO_POR_DEPENDENTE)
        if base_irrf > 0:
            for f in TABELA_IRRF:
                if f["piso"] < base_irrf <= f["teto"]:
                    irrf = max(0.0, (base_irrf * f["aliquota"]) - f["deducao"])
                    break
        irrf = round(irrf, 2)

    # 4. Salário líquido final e valor da hora trabalhada real
    salario_liquido = round(salario_bruto_total - inss - irrf, 2)
    jornada_total_real = jornada + horas_50 + horas_100
    hora_liquida = round(salario_liquido / jornada_total_real, 2) if jornada_total_real > 0 else 0.0
    
    return {
        "salario_bruto_total": salario_bruto_total,
        "total_horas_extras": total_horas_extras,
        "inss": inss,
        "irrf": irrf,
        "salario_liquido": salario_liquido,
        "hora_liquida": hora_liquida
    }

# ==========================================
# INTERFACE VISUAL (TELAS DO APP)
# ==========================================
st.title("💰 Meu Controle Financeiro & CLT")
st.write("Entenda seu ganho real e descubra quanto custam seus gastos em **tempo de vida trabalhado**.")

st.divider()

# --- SEÇÃO 1: PERFIL TRABALHISTA ---
st.subheader("1. Configure sua Renda")

col1, col2 = st.columns(2)
with col1:
    salario_base = st.number_input("Salário Bruto Base (R$)", min_value=1000.0, value=4500.0, step=100.0)
with col2:
    jornada = st.selectbox("Jornada Mensal (Horas)", options=[220, 180, 160], index=0)

col3, col4 = st.columns(2)
with col3:
    dependentes = st.number_input("Dependentes", min_value=0, value=0, step=1)
with col4:
    st.write("") # Espaçamento visual
    aplicar_irrf = st.toggle("Descontar IRRF na fonte?", value=True)

# Painel expansível para Horas Extras (não polui a tela principal)
horas_50, horas_100 = 0.0, 0.0
with st.expander("➕ Adicionar Horas Extras no Mês (Opcional)"):
    st.write("Informe a quantidade de horas extras realizadas:")
    col_he1, col_he2 = st.columns(2)
    with col_he1:
        horas_50 = st.number_input("Horas Extras 50% (Qtd)", min_value=0.0, value=0.0, step=1.0, help="Horas extras em dias normais de trabalho.")
    with col_he2:
        horas_100 = st.number_input("Horas Extras 100% (Qtd)", min_value=0.0, value=0.0, step=1.0, help="Horas extras em domingos ou feriados.")

# Executando o cálculo instantâneo
folha = calcular_clt(salario_base, jornada, dependentes, aplicar_irrf, horas_50, horas_100)

st.divider()

# --- SEÇÃO 2: RAIO-X DO SALÁRIO ---
st.subheader("2. Seu Salário Real (Líquido)")

# Se houver horas extras, exibe um aviso em destaque com o valor extra ganho
if folha["total_horas_extras"] > 0:
    st.success(f"📈 **Salário Bruto com Horas Extras:** R$ {folha['salario_bruto_total']:,.2f} *(+ R$ {folha['total_horas_extras']:,.2f} em extras)*")

card1, card2, card3 = st.columns(3)

with card1:
    st.metric(
        label="Salário Líquido",
        value=f"R$ {folha['salario_liquido']:,.2f}",
        delta=f"Hora real: R$ {folha['hora_liquida']:,.2f}"
    )
with card2:
    st.metric("Desconto INSS", f"R$ {folha['inss']:,.2f}")
with card3:
    if aplicar_irrf:
        st.metric("Desconto IRRF", f"R$ {folha['irrf']:,.2f}")
    else:
        st.metric("Desconto IRRF", "R$ 0,00", delta="Isento", delta_color="off")

st.divider()

# --- SEÇÃO 3: O DIFERENCIAL (CUSTO EM HORAS DE VIDA) ---
st.subheader("⏱️ Termômetro de Gastos: Custo em Horas de Vida")
st.write("Antes de fazer uma compra, descubra quanto tempo de trabalho líquido ela vai custar:")

col_gasto1, col_gasto2 = st.columns([1, 2])

with col_gasto1:
    valor_compra = st.number_input("Valor da despesa (R$)", min_value=1.0, value=150.0, step=10.0)

with col_gasto2:
    if folha["hora_liquida"] > 0:
        total_minutos = round((valor_compra / folha["hora_liquida"]) * 60)
        horas = total_minutos // 60
        minutos = total_minutos % 60
        
        st.info(f"💡 Para comprar algo de **R$ {valor_compra:,.2f}**, você precisará trabalhar exatamente:")
        st.header(f"⏳ **{horas} horas e {minutos} minutos**")
