"""A2 - Métricas, validação cruzada aninhada, partição agrupada e teste 5x2cv."""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, StratifiedKFold

from config import RANDOM_STATE
from m02_modelos import MODELOS, montar_pipeline

METRICAS = ["acuracia", "acuracia_bal", "precisao", "recall", "especificidade", "f1",
            "auc_roc", "auc_pr"]


@dataclass
class ResultadoCV:
    metricas: pd.DataFrame
    oof: pd.DataFrame
    params: list
    importancia: pd.DataFrame | None


def calcular_metricas(y_true, proba, limiar: float = 0.5) -> dict[str, float]:
    y_true = np.asarray(y_true)
    pred = (np.asarray(proba) >= limiar).astype(int)
    vn, fp, fn, vp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    recall = recall_score(y_true, pred, zero_division=0)
    espec = vn / (vn + fp) if (vn + fp) else 0.0
    return {
        "acuracia": (vp + vn) / len(y_true),
        "acuracia_bal": (recall + espec) / 2,
        "precisao": precision_score(y_true, pred, zero_division=0),
        "recall": recall,
        "especificidade": espec,
        "f1": f1_score(y_true, pred, zero_division=0),
        "auc_roc": roc_auc_score(y_true, proba),
        "auc_pr": average_precision_score(y_true, proba),
    }


def particoes(y, grupos=None, n_splits: int = 10) -> list[tuple[np.ndarray, np.ndarray]]:
    if grupos is None:
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
        return list(cv.split(np.zeros(len(y)), y))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    return list(cv.split(np.zeros(len(y)), y, groups=grupos))


def ajustar(nome, X_tr, y_tr, *, X_ref, estrategia="nenhum", n_interno=5, params_fixos=None):
    """Ajusta o pipeline no treino; com grade e sem params_fixos, busca no laço interno."""
    pipe = montar_pipeline(nome, X_ref, estrategia)
    grade = MODELOS[nome][1]
    if params_fixos is not None or not grade:
        if params_fixos:
            pipe.set_params(**params_fixos)
        return pipe.fit(X_tr, y_tr), dict(params_fixos or {})
    busca = GridSearchCV(pipe, grade, scoring="roc_auc", n_jobs=-1, refit=True,
                         cv=StratifiedKFold(n_splits=n_interno, shuffle=True, random_state=RANDOM_STATE))
    busca.fit(X_tr, y_tr)
    return busca.best_estimator_, busca.best_params_


def validacao_aninhada(nome, X, y, *, estrategia="nenhum", grupos=None, n_externo=10, n_interno=5,
                       params_fixos: dict | None = None, importancia=False) -> ResultadoCV:
    linhas, oof, params, imps = [], [], [], []
    for k, (tr, te) in enumerate(particoes(y, grupos, n_externo)):
        modelo, p = ajustar(nome, X.iloc[tr], y.iloc[tr], X_ref=X, estrategia=estrategia,
                            n_interno=n_interno, params_fixos=params_fixos)
        X_te, y_te = X.iloc[te], y.iloc[te]
        proba = modelo.predict_proba(X_te)[:, 1]
        linhas.append({"fold": k, **calcular_metricas(y_te, proba)})
        oof.append(pd.DataFrame({"indice": X.index[te], "fold": k, "y": y_te.to_numpy(), "proba": proba}))
        params.append(p)
        if importancia:
            r = permutation_importance(modelo, X_te, y_te, scoring="roc_auc", n_repeats=5,
                                       random_state=RANDOM_STATE)
            imps.append(pd.DataFrame({"fold": k, "atributo": X.columns, "queda_auc": r.importances_mean}))
    return ResultadoCV(pd.DataFrame(linhas), pd.concat(oof, ignore_index=True), params,
                       pd.concat(imps, ignore_index=True) if importancia else None)
