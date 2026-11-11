"""A2 - Execução dos experimentos. Grava os resultados brutos em saida/a2/.

Uso:  python src/m04_experimentos.py
"""
import json
import platform
import time
from collections import Counter
from importlib import metadata
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from config import CENARIOS, RANDOM_STATE, SAIDA_A2
from m01_atributos import carregar_xy
from m02_modelos import ESTRATEGIAS, MODELOS
from m03_validacao import METRICAS, teste_5x2cv, validacao_aninhada

COMPLEXOS = ["arvore", "rf", "gb"]
ROTULO = ["experimento", "cenario", "modelo", "estrategia"]


def moda_params(por_fold: list[dict]) -> dict:
    chaves = [json.dumps(p, sort_keys=True) for p in por_fold]
    return json.loads(Counter(chaves).most_common(1)[0][0])


def _dados(n_amostra):
    dados = {c: carregar_xy(c) for c in CENARIOS}
    if n_amostra:
        _, y, _ = dados["principal"]
        sel, _ = train_test_split(y.index, train_size=n_amostra, stratify=y, random_state=RANDOM_STATE)
        sel = sorted(sel)
        dados = {c: (X.loc[sel], y.loc[sel], g.loc[sel]) for c, (X, y, g) in dados.items()}
    return dados


def executar(n_amostra: int | None = None, n_externo: int = 10, n_interno: int = 5,
             destino: Path = SAIDA_A2) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    dados = _dados(n_amostra)
    metricas, oof, imps = [], [], []
    params = {c: {} for c in CENARIOS}

    def rodar(experimento, cenario, nome, estrategia="nenhum", **kw):
        X, y, _ = dados[cenario]
        r = validacao_aninhada(nome, X, y, estrategia=estrategia, n_externo=n_externo,
                               n_interno=n_interno, **kw)
        rotulo = dict(zip(ROTULO, (experimento, cenario, nome, estrategia)))
        metricas.append(r.metricas.assign(**rotulo))
        oof.append(r.oof.assign(**rotulo))
        print(f"  {experimento:16s} {cenario:9s} {nome:6s} {estrategia:13s} "
              f"AUC={r.metricas['auc_roc'].mean():.3f} ({time.time() - inicio:.0f}s)", flush=True)
        return r

    # 1) comparação principal (sem SOPRO), com ajuste de hiperparâmetros no laço interno
    for nome in MODELOS:
        r = rodar("principal", "principal", nome, importancia=nome != "dummy")
        params["principal"][nome] = r.params
        if r.importancia is not None:
            imps.append(r.importancia.assign(modelo=nome))
    auc = pd.concat(metricas).query("modelo in @COMPLEXOS").groupby("modelo")["auc_roc"].mean()
    melhor = auc.idxmax()
    pares = ["logreg", melhor]

    # 2) cenários de atributos: tamanho do vazamento (com SOPRO) e dependência dos MOTIVOs
    for cenario in ("com_sopro", "restrito"):
        for nome in pares:
            params[cenario][nome] = rodar("cenarios", cenario, nome).params

    moda = {nome: moda_params(params["principal"][nome]) for nome in pares}
    X, y, grupos = dados["principal"]

    # 3) desbalanceamento, com os hiperparâmetros mais escolhidos no experimento 1
    for nome in pares:
        for estrategia in ESTRATEGIAS:
            rodar("desbalanceamento", "principal", nome, estrategia, params_fixos=moda[nome])

    # 4) partição agrupada por possível paciente (DN + SEXO)
    for nome in pares:
        rodar("agrupado", "principal", nome, grupos=grupos, params_fixos=moda[nome])

    # 5) teste t 5x2cv: baseline x melhor modelo complexo
    t5x2 = teste_5x2cv("logreg", melhor, X, y, n_interno=min(3, n_interno))
    print(f"  5x2cv logreg x {melhor}: t={t5x2['t']:.3f} p={t5x2['p']:.4f}", flush=True)

    pd.concat(metricas, ignore_index=True)[ROTULO + ["fold"] + METRICAS].to_csv(
        destino / "metricas_cv.csv", index=False)
    pd.concat(oof, ignore_index=True)[ROTULO + ["indice", "fold", "y", "proba"]].to_csv(
        destino / "oof.csv", index=False)
    pd.concat(imps, ignore_index=True)[["modelo", "fold", "atributo", "queda_auc"]].to_csv(
        destino / "importancia.csv", index=False)
    saida_params = {c: {n: {"por_fold": pf, "moda": moda_params(pf)} for n, pf in ms.items()}
                    for c, ms in params.items()}
    (destino / "melhores_params.json").write_text(json.dumps(saida_params, indent=2), encoding="utf-8")
    (destino / "teste_5x2cv.json").write_text(
        json.dumps({"modelo_a": "logreg", "modelo_b": melhor, **t5x2}, indent=2), encoding="utf-8")
    versoes = {p: metadata.version(p) for p in ["pandas", "numpy", "scikit-learn", "imbalanced-learn", "scipy"]}
    (destino / "resumo.json").write_text(json.dumps({
        "melhor_complexo": melhor, "random_state": RANDOM_STATE, "n_instancias": len(y),
        "n_externo": n_externo, "n_interno": n_interno, "tempo_s": round(time.time() - inicio),
        "python": platform.python_version(), "versoes": versoes,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    executar()
