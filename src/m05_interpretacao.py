"""A2 - Interpretação dos resultados gravados por m04 (matriz de confusão, limiar,
importância dos atributos, razão de chances e perfil dos erros).

Uso:  python src/m05_interpretacao.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from config import SAIDA_A2
from m01_atributos import carregar_xy, slug
from m03_validacao import METRICAS, ajustar, calcular_metricas

ROTULO = ["experimento", "cenario", "modelo", "estrategia"]
LIMIARES = np.round(np.arange(0.20, 0.80 + 1e-9, 0.05), 2)


def _oof_principal(oof: pd.DataFrame, modelo: str) -> pd.DataFrame:
    return oof.query("experimento == 'principal' and modelo == @modelo")


def resumo_metricas(metricas: pd.DataFrame) -> pd.DataFrame:
    agg = metricas.groupby(ROTULO, sort=False)[METRICAS].agg(["mean", "std"])
    agg.columns = [f"{m}_{'media' if s == 'mean' else 'dp'}" for m, s in agg.columns]
    return agg.reset_index()


def matriz_confusao(oof: pd.DataFrame, modelos: list[str]) -> pd.DataFrame:
    linhas = []
    for nome in modelos:
        o = _oof_principal(oof, nome)
        pred = (o["proba"] >= 0.5).astype(int)
        linhas.append({"modelo": nome,
                       "vn": int(((o["y"] == 0) & (pred == 0)).sum()),
                       "fp": int(((o["y"] == 0) & (pred == 1)).sum()),
                       "fn": int(((o["y"] == 1) & (pred == 0)).sum()),
                       "vp": int(((o["y"] == 1) & (pred == 1)).sum())})
    return pd.DataFrame(linhas)


def tabela_limiar(oof: pd.DataFrame, modelo: str) -> pd.DataFrame:
    o = _oof_principal(oof, modelo)
    linhas = []
    for t in LIMIARES:
        m = calcular_metricas(o["y"], o["proba"], limiar=t)
        pred = o["proba"] >= t
        linhas.append({"limiar": t, "recall": m["recall"], "precisao": m["precisao"],
                       "especificidade": m["especificidade"], "f1": m["f1"],
                       "fn": int(((o["y"] == 1) & ~pred).sum()), "fp": int(((o["y"] == 0) & pred).sum())})
    return pd.DataFrame(linhas)


def importancia_resumo(imp: pd.DataFrame) -> pd.DataFrame:
    r = (imp.groupby(["modelo", "atributo"])["queda_auc"].agg(queda_auc_media="mean", queda_auc_dp="std")
         .reset_index())
    return r.sort_values(["modelo", "queda_auc_media"], ascending=[True, False], ignore_index=True)


def razao_chances(params_moda: dict) -> pd.DataFrame:
    """Regressão Logística ajustada no conjunto inteiro, só para leitura dos coeficientes
    (o desempenho é sempre o da validação cruzada)."""
    X, y, _ = carregar_xy("principal")
    modelo, _ = ajustar("logreg", X, y, X_ref=X, params_fixos=params_moda)
    nomes = modelo.named_steps["prep"].get_feature_names_out()
    coef = modelo.named_steps["modelo"].coef_[0]
    r = pd.DataFrame({"termo": nomes, "coeficiente": coef, "razao_chances": np.exp(coef)})
    return r.reindex(r["coeficiente"].abs().sort_values(ascending=False).index).head(10).reset_index(drop=True)


def perfil_erros(oof: pd.DataFrame, modelo: str) -> pd.DataFrame:
    o = _oof_principal(oof, modelo)
    X, _, _ = carregar_xy("principal")
    pred = (o["proba"] >= 0.5).astype(int).to_numpy()
    y = o["y"].to_numpy()
    grupo = np.select([(y == 1) & (pred == 1), (y == 1) & (pred == 0), (y == 0) & (pred == 1)],
                      ["VP", "FN", "FP"], default="VN")
    d = X.loc[o["indice"].to_numpy()].assign(grupo=grupo, proba=o["proba"].to_numpy())
    motivos = pd.crosstab(d["grupo"], d["MOTIVO1"].fillna("Nao informado"), normalize="index") * 100
    motivos.columns = [f"motivo1_{slug(c)}_pct" for c in motivos.columns]
    base = d.groupby("grupo").agg(n=("proba", "size"), proba_mediana=("proba", "median"),
                                  idade_mediana=("IDADE", "median"), fc_mediana=("FC", "median"),
                                  hda_ausente_pct=("hda_ausente", lambda s: 100 * s.mean()))
    return base.join(motivos).reindex(["VP", "FN", "FP", "VN"]).reset_index()


def executar(origem: Path = SAIDA_A2) -> None:
    metricas = pd.read_csv(origem / "metricas_cv.csv")
    oof = pd.read_csv(origem / "oof.csv")
    melhor = json.loads((origem / "resumo.json").read_text(encoding="utf-8"))["melhor_complexo"]
    params = json.loads((origem / "melhores_params.json").read_text(encoding="utf-8"))

    resumo_metricas(metricas).to_csv(origem / "resumo_metricas.csv", index=False)
    matriz_confusao(oof, ["logreg", melhor]).to_csv(origem / "confusao.csv", index=False)
    tabela_limiar(oof, melhor).to_csv(origem / "limiar.csv", index=False)
    importancia_resumo(pd.read_csv(origem / "importancia.csv")).to_csv(
        origem / "importancia_resumo.csv", index=False)
    razao_chances(params["principal"]["logreg"]["moda"]).to_csv(origem / "razao_chances.csv", index=False)
    perfil_erros(oof, melhor).to_csv(origem / "perfil_erros.csv", index=False)


if __name__ == "__main__":
    executar()
