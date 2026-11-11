import numpy as np
import pytest

from m01_atributos import carregar_xy
from m02_modelos import MODELOS, montar_pipeline


def test_padronizador_usa_so_o_treino(xy):
    X, y, _ = xy
    tr = X.iloc[:8000]
    pipe = montar_pipeline("logreg", X).fit(tr, y.iloc[:8000])
    media = pipe.named_steps["prep"].named_transformers_["num_linear"].named_steps["padroniza"].mean_[0]
    assert media == pytest.approx(tr["IDADE"].fillna(tr["IDADE"].median()).mean())
    assert media != pytest.approx(X["IDADE"].fillna(X["IDADE"].median()).mean())


def test_categoria_inedita_no_teste_nao_quebra(xy):
    X, y, _ = xy
    pipe = montar_pipeline("logreg", X).fit(X.iloc[:2000], y.iloc[:2000])
    novo = X.iloc[2000:2005].copy()
    novo["Convenio"] = "CONVENIO NUNCA VISTO"
    assert pipe.predict_proba(novo).shape == (5, 2)


def test_coluna_toda_ausente_no_treino_mantem_largura(xy):
    X, y, _ = xy
    tr = X.iloc[:2000].copy()
    tr["PA SISTOLICA"] = np.nan
    larg_a = montar_pipeline("logreg", X).fit(tr, y.iloc[:2000])[:-1].transform(X.iloc[2000:2010]).shape[1]
    larg_b = montar_pipeline("logreg", X).fit(X.iloc[:2000], y.iloc[:2000])[:-1].transform(X.iloc[2000:2010]).shape[1]
    assert larg_a == larg_b


def test_reamostragem_so_no_ajuste(xy):
    X, y, _ = xy
    pipe = montar_pipeline("logreg", X, estrategia="smote").fit(X.iloc[:2000], y.iloc[:2000])
    assert len(pipe.predict(X.iloc[2000:2500])) == 500


@pytest.mark.parametrize("nome", ["dummy", "logreg", "arvore", "rf", "gb"])
def test_todos_os_modelos_ajustam_e_grade_e_valida(xy, nome):
    X, y, _ = xy
    pipe = montar_pipeline(nome, X)
    assert set(MODELOS[nome][1]) <= set(pipe.get_params())
    pipe.fit(X.iloc[:1500], y.iloc[:1500])


def test_cenario_restrito_monta_sem_motivos():
    X, y, _ = carregar_xy("restrito")
    montar_pipeline("logreg", X).fit(X.iloc[:1500], y.iloc[:1500])
