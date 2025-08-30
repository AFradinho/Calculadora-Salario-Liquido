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
    subs_ali_suj = max(0, subs_ali_dia - cap_subs_ali)                      # Subsídio de alimentação sujeito a tributação

    # Outros subsídios
    ferias = salario_bruto if not duodecimos and mes.lower() == "ferias" else 0
    natal = salario_bruto if not duodecimos and mes.lower() == "natal" else 0
    if duodecimos:
        subsidio = salario_bruto*2/12
    else:
        subsidio = ferias + natal

    R = salario_bruto + subs_ali_suj + subsidio

    esc = escalao(R)
    taxa, est_abat, const, lin_k, lin_c, add_dep = esc["marginal"], esc["est_abat"], esc["const"], esc["lin_k"], esc["lin_c"], esc["add_dep"]
    

    if est_abat == "linear":
        abat = lin_k * (lin_c - R)
    else:
        abat = const
    
    abat_dep = add_dep * dependentes

    tributacao_inicial = max(0, R*taxa - abat - abat_dep)
    taxa_efetiva = tributacao_inicial / R


    # IRS Jovem
    if ano_independente in mapa_IRS_jovem:
        pass

calculadora(1000, subs_ali_dia = 7)