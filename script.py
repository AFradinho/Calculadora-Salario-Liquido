import json


# Configuração IRS Jovem
mapa_IRS_jovem = {
    1: 1.0,
    2: 0.75,
    3: 0.75,
    4: 0.75,
    5: 0.5,
    6: 0.5,
    7: 0.5,
    8: 0.25,
    9: 0.25,
    10: 0.25
}

IAS = 522.5
IAS_mult = 55
IRS_jovem_cap = IAS * IAS_mult
IRS_jovem_cap_month = IRS_jovem_cap / 14



def load_tables(path=r"tabela_I_IRS.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


tabela = load_tables()

def escalao(R):

    for esc in tabela:
        if esc["upper"] >= R:
            return esc
    return tabela[-1]

def calculadora(
    salario_bruto,                  # Salário Bruto mensal
    meses = 14,                     # Meses de salário
    duodecimos = False,             # Duodécimos
    mes = "base",                   # Base, Ferias, Natal
    dependentes = 0,                # Número de dependentes
    ano_independente = 0,        # Número de anos como independente
    subs_ali_dia = 0,               # Subsídio diário de alimentação
    forma_subs_ali = "numerario",   # Numerário, Cartão
    dias_trabalho = 22              # Número de dias de trabalho por mês
):

    # Subsídios de alimentação
    cap_subs_ali = 6.0 if forma_subs_ali.lower() == "numerario" else 10.2   # Teto de subsídio não sujeito a tributação
    subs_ali_total = dias_trabalho * subs_ali_dia                           # Total de subsídio de alimentação
    subs_ali_suj = max(0, subs_ali_dia - cap_subs_ali)*dias_trabalho        # Subsídio de alimentação sujeito a tributação

    # Outros subsídios
    ferias = salario_bruto if not duodecimos and mes.lower() == "ferias" else 0
    natal = salario_bruto if not duodecimos and mes.lower() == "natal" else 0
    if duodecimos:
        subsidio = salario_bruto*2/meses
    else:
        subsidio = ferias + natal


    # Base coletável
    R = salario_bruto + subs_ali_suj + subsidio

    # Escalão de IRS
    esc = escalao(R)
    taxa, est_abat, const, lin_k, lin_c, add_dep = esc["marginal"], esc["est_abat"], esc["const"], esc["lin_k"], esc["lin_c"], esc["add_dep"]

    if est_abat == "linear":
        abat = lin_k * (lin_c - R)
    else:
        abat = const
    
    abat_dep = add_dep * dependentes

    # Taxa efetiva
    tributacao_inicial = max(0, R*taxa - abat - abat_dep)
    taxa_efetiva = tributacao_inicial / R

    # IRS Jovem
    if ano_independente in mapa_IRS_jovem:
        pct_isento = mapa_IRS_jovem[ano_independente]
        reducao = taxa_efetiva * R * pct_isento if R * pct_isento < IRS_jovem_cap_month else taxa_efetiva * IRS_jovem_cap_month
    else:
        reducao = 0

    irs_total = tributacao_inicial - reducao



    # Segurança Social
    ss_base = salario_bruto + subsidio + subs_ali_suj
    ss = ss_base * 0.11

    salario_liquido = salario_bruto + subsidio + subs_ali_total - irs_total - ss

    #return salario_liquido, ss, subs_ali_total, irs_total, R-subsidio, reducao, taxa_efetiva, subsidio
    return f" Salário Líquido: {salario_liquido:.2f}€\n Salário Bruto: {salario_bruto:.2f}€\n Base Coletável: {R:.2f}€\n Taxa Marginal: {taxa*100:.2f}€\n Tributação Inicial: {tributacao_inicial:.2f}€\n Taxa Efetiva: {taxa_efetiva*100:.2f}%\n\n Pct de Isenção: {pct_isento*100:.2f}%\n Redução de Tributação: {reducao:.2f}€\n Tributação Efetiva: {irs_total:.2f}€"




print(calculadora(3200, subs_ali_dia = 7.63, duodecimos=True, ano_independente=2))