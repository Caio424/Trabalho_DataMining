"""A2 - Do UCMF_clean.csv para (X, y, grupos).

Só faz operações linha a linha; nada aqui é ajustado aos dados (imputação,
padronização e codificação ficam no pipeline, reajustado em cada treino).
"""
import re
import unicodedata

import pandas as pd

from config import ALVO, ARQ_LIMPO, CENARIOS, ORDEM_PPA, SINTOMAS

REMOVIDAS = ["ID", "Atendimento", "DN", "Peso", "Altura", "HDA 1", "HDA2", "PPA", ALVO]


def slug(txt):
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    return re.sub(r"[^0-9a-zA-Z]+", "_", txt).strip("_").lower()


def montar_atributos(df: pd.DataFrame, cenario: str = "principal") -> pd.DataFrame:
    X = df.copy()
    for s in SINTOMAS:
        X[f"sint_{slug(s)}"] = ((X["HDA 1"] == s) | (X["HDA2"] == s)).astype(int)
    X["hda_ausente"] = X["HDA 1"].isna().astype(int)
    X["ppa_ord"] = X["PPA"].map({k: i for i, k in enumerate(ORDEM_PPA)}).fillna(0).astype(int)
    X["ppa_ausente"] = X["PPA"].isna().astype(int)
    return X.drop(columns=REMOVIDAS + CENARIOS[cenario])


def carregar_xy(cenario: str = "principal") -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    df = pd.read_csv(ARQ_LIMPO, parse_dates=["Atendimento", "DN"], encoding="utf-8-sig")
    y = (df[ALVO] == "Anormal").astype(int).rename("y")
    grupos = (df["DN"].dt.strftime("%Y-%m-%d") + "|" + df["SEXO"].fillna("?")).rename("grupo")
    sem_dn = df["DN"].isna()
    grupos[sem_dn] = "linha_" + df.index[sem_dn].astype(str)
    return montar_atributos(df, cenario), y, grupos
