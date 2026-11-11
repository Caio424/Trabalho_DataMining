"""Etapa 2 - Limpeza.

Cada regra registra quantos valores/linhas alterou; o log vira a Tabela de
qualidade do relatório. Nenhum valor ausente é imputado aqui.

Gera:
  UCMF_clean.csv
  tabelas/tab_log_limpeza.csv
  tabelas/tab_descritiva_antes_depois.csv
  tabelas/tab_categoricas_limpo.csv
"""
import re
import unicodedata

import numpy as np
import pandas as pd

from config import (ALVO, ARQ_LIMPO, CATEGORICAS, FAIXAS, LIMIAR_RARO_CONVENIO, MAP_ALVO,
                    MAP_PPA, MAP_PULSOS, MAP_SEXO, MAP_SOPRO, NUMERICAS,
                    registrar_resultados, salvar_tabela)
from p01_perfil import carregar_bruto, descritiva, numericas_brutas, resumo_categoricas

DATA_MAX_ESTUDO = pd.Timestamp("2010-12-31")   # último atendimento plausível no conjunto
EXCEL_ORIGEM = pd.Timestamp("1899-12-30")


class Log:
    def __init__(self):
        self.linhas = []

    def add(self, variavel, problema, solucao, n):
        self.linhas.append({"Variável": variavel, "Problema": problema,
                            "Solução": solucao, "Registros afetados": int(n)})

    def df(self):
        return pd.DataFrame(self.linhas)


def normalizar(s):
    """minúsculas, sem acento, sem espaços extras (mantém NaN)."""
    def f(x):
        if pd.isna(x):
            return np.nan
        x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode()
        return re.sub(r"\s+", " ", x).strip().lower()
    return s.map(f)


def mapear(df, col, mapa, log, problema, extra=""):
    antes = df[col].copy()
    df[col] = normalizar(df[col]).map(mapa)
    # conta só grafias minoritárias (a grafia dominante de cada categoria é só renomeada)
    dominante = antes.groupby(df[col]).agg(lambda s: s.value_counts().index[0])
    alterados = (df[col].notna() & (antes != df[col].map(dominante))).sum()
    log.add(col, problema, f"Padronização para {' / '.join(sorted(set(mapa.values())))}{extra}", alterados)


def fora_da_faixa(df, col, log, problema_extra=""):
    lo, hi = FAIXAS[col]
    m = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
    df.loc[m, col] = np.nan
    log.add(col, f"Valores implausíveis (fora de [{lo}; {hi}]){problema_extra}",
            "Convertidos em ausente", m.sum())
    return m.sum()


def parse_data(serie):
    """dd/mm/aa, dd/mm/aaaa ou serial do Excel; demais formatos -> NaT."""
    s = serie.astype("string").str.strip()
    out = pd.to_datetime(s.where(s.str.fullmatch(r"\d{2}/\d{2}/\d{2}")), format="%d/%m/%y", errors="coerce")
    quatro = pd.to_datetime(s.where(s.str.fullmatch(r"\d{2}/\d{2}/\d{4}")), format="%d/%m/%Y", errors="coerce")
    serial = pd.to_numeric(s.where(s.str.fullmatch(r"\d{5}")), errors="coerce")
    serial = EXCEL_ORIGEM + pd.to_timedelta(serial, unit="D")
    return out.fillna(quatro).fillna(serial), s


def limpar_datas_idade(df, log):
    orig_idade = df["IDADE"].copy()
    for c in ("Atendimento", "DN"):
        data, s = parse_data(df[c])
        n_serial = s.str.fullmatch(r"\d{5}").fillna(False).sum()
        n_texto = (s.notna() & data.isna()).sum()
        futuras = data > DATA_MAX_ESTUDO
        log.add(c, "Datas como número serial do Excel", "Convertidas (origem 30/12/1899)", n_serial)
        log.add(c, "Texto livre/formato inválido (ex.: '5 anos', '??')", "Convertido em ausente", n_texto)
        log.add(c, "Ano de 2 dígitos lido no século errado (ex.: 2066)",
                f"Datas após {DATA_MAX_ESTUDO.year} convertidas em ausente", futuras.sum())
        df[c] = data.mask(futuras)

    dias = (df["Atendimento"] - df["DN"]).dt.days
    idade_calc = dias / 365.25
    # fator do erro sistemático da IDADE original (medido onde as duas existem)
    ok = idade_calc.gt(1) & orig_idade.gt(1)
    fator = float((orig_idade[ok] / idade_calc[ok]).median())
    registrar_resultados("idade_fator_erro", round(fator, 4))
    registrar_resultados("idade_dias_por_ano_implicito", round(365.25 / fator, 1))
    divergente = (idade_calc.notna() & orig_idade.notna() & ((orig_idade - idade_calc).abs() > .05)).sum()
    idade = idade_calc.copy()
    sem_data = idade.isna() & orig_idade.notna()
    idade[sem_data] = orig_idade[sem_data] / fator
    df["IDADE"] = idade
    log.add("IDADE", f"Erro sistemático: valor ~{(fator-1)*100:.1f}% acima de (Atendimento − DN)",
            "Recalculada a partir das datas (÷365,25); sem data: IDADE original corrigida pelo fator",
            divergente + sem_data.sum())
    neg = (df["IDADE"] < 0).sum()
    fora_da_faixa(df, "IDADE", log, f"; {neg} negativas (atendimento antes do nascimento)")


def executar():
    bruto = carregar_bruto()
    df = bruto.copy()
    log = Log()

    # 1) duplicatas exatas ignorando ID
    dup = df.drop(columns="ID").duplicated()
    df = df[~dup].copy()
    log.add("(linhas)", "Registros duplicados (idênticos exceto pelo ID)", "Removidos", dup.sum())

    # 2) alvo
    mapear(df, ALVO, MAP_ALVO, log, "Grafias inconsistentes ('anormal', 'Normais')")
    sem_alvo = df[ALVO].isna()
    df = df[~sem_alvo].copy()
    log.add(ALVO, "Rótulo ausente", "Linhas removidas (rótulo não é imputável)", sem_alvo.sum())

    # 3) datas e idade
    limpar_datas_idade(df, log)

    # 4) antropometria
    for c in ("Peso", "Altura"):
        zeros = (df[c] == 0).sum()
        df.loc[df[c] == 0, c] = np.nan
        log.add(c, "Zero usado como 'não medido'", "Convertido em ausente", zeros)
        fora_da_faixa(df, c, log)
    imc_calc = df["Peso"] / (df["Altura"] / 100) ** 2
    difere = (imc_calc.notna() & ((imc_calc - df["IMC"]).abs() > 1)).sum()
    novos = (imc_calc.notna() & df["IMC"].isna()).sum()
    removidos = (imc_calc.isna() & df["IMC"].notna()).sum()
    df["IMC"] = imc_calc
    log.add("IMC", "Inconsistente com Peso/Altura² (ex.: 848) e arredondado",
            "Recalculado = Peso/Altura² (m)", difere + novos + removidos)
    fora_da_faixa(df, "IMC", log)

    # 5) pressão arterial
    for c in ("PA SISTOLICA", "PA DIASTOLICA"):
        fora_da_faixa(df, c, log)
    inv = (df["PA SISTOLICA"] <= df["PA DIASTOLICA"]).sum()
    df.loc[df["PA SISTOLICA"] <= df["PA DIASTOLICA"], ["PA SISTOLICA", "PA DIASTOLICA"]] = np.nan
    log.add("PA SIST./DIAST.", "PAS ≤ PAD (fisiologicamente impossível)", "Par convertido em ausente", inv)

    # 6) PPA
    ppa_norm = normalizar(df["PPA"])
    invalidos = ppa_norm.isin(["#value!", "nao calculado"]).sum()
    df["PPA"] = ppa_norm.map(MAP_PPA)
    log.add("PPA", "Erro de fórmula ('#VALUE!') e 'Não Calculado' mesmo com PA medida",
            "Convertidos em ausente", invalidos)
    log.add("PPA", "Classes separadas por PAS/PAD (9 níveis)",
            "Agrupadas em 4 níveis ordinais: Normal < Pré-HAS < HAS-1 < HAS-2",
            df["PPA"].notna().sum())
    sem_pa = df["PPA"].notna() & df["PA SISTOLICA"].isna()
    df.loc[sem_pa, "PPA"] = np.nan
    log.add("PPA", "Classificação sem PA válida que a sustente", "Convertida em ausente", sem_pa.sum())

    # 7) FC
    fc_txt = df["FC"].astype(str).str.strip()
    faixa = fc_txt.str.extract(r"^(\d+)\s*(?:-|a)\s*(\d+)$").astype(float)
    fc = pd.to_numeric(fc_txt, errors="coerce").astype(float)
    eh_faixa = faixa[0].notna().to_numpy()
    fc[eh_faixa] = faixa[eh_faixa].mean(axis=1).to_numpy()
    df["FC"] = fc
    log.add("FC", "Armazenada como texto; faixas digitadas ('80-90', '156 a 168')",
            "Convertida para número; faixa → ponto médio", eh_faixa.sum())
    fora_da_faixa(df, "FC", log)

    # 8) categóricas
    indet = normalizar(df["SEXO"]).eq("indeterminado").sum()
    mapear(df, "SEXO", MAP_SEXO, log, "5 grafias (M/Masculino/masculino...)")
    log.add("SEXO", "Categoria 'Indeterminado' (não informado)", "Convertida em ausente", indet)
    mapear(df, "SOPRO", MAP_SOPRO, log, "Caixa/acento ('Sistólico' × 'sistólico')")
    mapear(df, "PULSOS", MAP_PULSOS, log, "Caixa ('Normais' × 'NORMAIS')")
    for c in ("HDA 1", "HDA2"):
        df[c] = df[c].str.strip().replace({"Palpitacao": "Palpitação"})
    raw_conv = df["Convenio"]
    conv = normalizar(raw_conv).str.upper().str.replace(r"[.\-_/ ]+$", "", regex=True).str.replace(r"\s*\.\s*", " ", regex=True).str.strip()
    freq = conv.value_counts(normalize=True)
    raros = conv.isin(freq[freq < LIMIAR_RARO_CONVENIO].index)
    registrar_resultados("convenio_grafias", {"bruto": int(raw_conv.nunique()), "padronizado": int(conv.nunique())})
    conv[raros] = "OUTROS"
    log.add("Convenio", f"{raw_conv.nunique()} grafias ('Camed' × 'CAMED'); cauda longa",
            f"Caixa/pontuação padronizadas ({freq.size} valores); <1% → 'OUTROS'", raros.sum())
    aus_conv = conv.isna().sum()
    df["Convenio"] = conv.fillna("NAO INFORMADO")
    log.add("Convenio", "Ausente", "Categoria explícita 'NAO INFORMADO'", aus_conv)
    for c in ("MOTIVO1", "MOTIVO2"):
        n = df[c].str.match(r"^\d+\s*-\s*").sum()
        df[c] = (df[c].str.replace(r"^\d+\s*-\s*", "", regex=True).str.strip()
                 .replace({"Cardiopatia congenica": "Cardiopatia congênita",
                           "Cardiopatia na familia": "Cardiopatia na família"}))
        log.add(c, "Código numérico embutido no texto", "Prefixo removido", n)
    log.add("HDA2", f"{df['HDA2'].isna().mean()*100:.0f}% ausente",
            "Unida a HDA 1 em indicadores de sintoma (transformação)", df["HDA2"].isna().sum())

    df = df.reset_index(drop=True)
    df.to_csv(ARQ_LIMPO, index=False, encoding="utf-8-sig")

    # tabelas
    salvar_tabela(log.df(), "tab_log_limpeza")
    antes = descritiva(numericas_brutas(bruto)).assign(Momento="Bruto")
    depois = descritiva(df[NUMERICAS]).assign(Momento="Limpo")
    salvar_tabela(pd.concat([antes, depois]), "tab_descritiva_antes_depois")
    salvar_tabela(resumo_categoricas(df, [ALVO] + CATEGORICAS), "tab_categoricas_limpo")

    registrar_resultados("limpo_shape", list(df.shape))
    registrar_resultados("limpo_ausentes_pct", (df.isna().mean() * 100).round(1).to_dict())
    registrar_resultados("limpo_alvo", df[ALVO].value_counts().to_dict())
    print(f"[2] limpeza: {bruto.shape[0]} → {df.shape[0]} linhas; {len(log.linhas)} regras registradas")
    return df


if __name__ == "__main__":
    executar()
