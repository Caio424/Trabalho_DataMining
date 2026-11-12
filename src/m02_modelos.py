"""A2 - Pré-processador, catálogo de modelos e montagem do pipeline.

Tudo que é ajustado aos dados (log, imputação, padronização, codificação,
reamostragem) fica dentro do pipeline e é reajustado em cada treino.
"""
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from config import NOMINAIS, NUM_LINEAR, NUM_LOG, RANDOM_STATE

ESTRATEGIAS = ["nenhum", "class_weight", "smote", "subamostragem"]

MODELOS = {
    "dummy": (DummyClassifier(strategy="most_frequent"), {}),
    "logreg": (LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
               {"modelo__C": [0.01, 0.1, 1, 10]}),
    "arvore": (DecisionTreeClassifier(random_state=RANDOM_STATE),
               {"modelo__max_depth": [3, 5, 7, 10, None], "modelo__min_samples_leaf": [1, 10, 50]}),
    "rf": (RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=RANDOM_STATE),
           {"modelo__max_depth": [None, 10, 20], "modelo__min_samples_leaf": [1, 5],
            "modelo__max_features": ["sqrt", 0.3]}),
    "gb": (HistGradientBoostingClassifier(max_iter=200, early_stopping=False,
                                          random_state=RANDOM_STATE),
           {"modelo__learning_rate": [0.05, 0.1], "modelo__max_depth": [3, 6, None],
            "modelo__l2_regularization": [0, 1]}),
}

ROTULOS = {"dummy": "Classe majoritária", "logreg": "Regressão Logística",
           "arvore": "Árvore de Decisão", "rf": "Random Forest", "gb": "Gradient Boosting"}


def _numerico(com_log: bool) -> SkPipeline:
    passos = [("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one"))] if com_log else []
    passos += [("imputa", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
               ("padroniza", StandardScaler())]
    return SkPipeline(passos)


def montar_preprocessador(X: pd.DataFrame) -> ColumnTransformer:
    nominais = [c for c in NOMINAIS if c in X.columns]
    nominal = SkPipeline([
        ("imputa", SimpleImputer(strategy="constant", fill_value="Nao informado")),
        ("codifica", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=30,
                                   sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num_log", _numerico(True), [c for c in NUM_LOG if c in X.columns]),
        ("num_linear", _numerico(False), [c for c in NUM_LINEAR if c in X.columns]),
        ("nominais", nominal, nominais),
    ], remainder="passthrough", verbose_feature_names_out=False)


def montar_pipeline(nome: str, X: pd.DataFrame, estrategia: str = "nenhum") -> Pipeline:
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"estratégia desconhecida: {estrategia}")
    modelo = clone(MODELOS[nome][0])
    if estrategia == "class_weight" and "class_weight" in modelo.get_params():
        modelo.set_params(class_weight="balanced")
    passos = [("prep", montar_preprocessador(X))]
    if estrategia == "smote":
        passos.append(("amostra", SMOTE(random_state=RANDOM_STATE)))
    elif estrategia == "subamostragem":
        passos.append(("amostra", RandomUnderSampler(random_state=RANDOM_STATE)))
    passos.append(("modelo", modelo))
    return Pipeline(passos)
