import numpy as np
import pandas as pd
import pytest

from m03_validacao import calcular_metricas, particoes, validacao_aninhada


def test_metricas_em_caso_conhecido():
    m = calcular_metricas(np.array([1, 1, 1, 0, 0, 0, 0, 0]),
                          np.array([.9, .8, .2, .7, .1, .1, .1, .1]))
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["especificidade"] == pytest.approx(4 / 5)
    assert m["precisao"] == pytest.approx(2 / 3)
    assert m["acuracia_bal"] == pytest.approx((2 / 3 + 4 / 5) / 2)


def test_particoes_estratificadas_e_disjuntas(xy):
    _, y, _ = xy
    ps = particoes(y)
    assert len(ps) == 10
    assert sorted(np.concatenate([te for _, te in ps])) == list(range(len(y)))
    for _, te in ps:
        assert y.iloc[te].mean() == pytest.approx(y.mean(), abs=0.01)


def test_particao_agrupada_nao_divide_grupo(xy):
    _, y, grupos = xy
    for tr, te in particoes(y, grupos=grupos):
        assert set(grupos.iloc[tr]).isdisjoint(grupos.iloc[te])


def test_cada_instancia_avaliada_uma_vez(amostra):
    X, y = amostra
    r = validacao_aninhada("logreg", X, y, n_externo=3, n_interno=2)
    assert len(r.metricas) == 3 and len(r.params) == 3
    assert sorted(r.oof["indice"]) == list(range(len(y)))


def test_execucao_e_deterministica(amostra):
    X, y = amostra
    a = validacao_aninhada("rf", X, y, n_externo=3, n_interno=2, params_fixos={})
    b = validacao_aninhada("rf", X, y, n_externo=3, n_interno=2, params_fixos={})
    pd.testing.assert_frame_equal(a.metricas, b.metricas)


def test_rotulos_embaralhados_dao_auc_de_acaso(amostra):
    X, y = amostra
    y_emb = pd.Series(np.random.default_rng(42).permutation(y.to_numpy()), index=y.index)
    r = validacao_aninhada("logreg", X, y_emb, n_externo=3, n_interno=2)
    assert 0.42 < r.metricas["auc_roc"].mean() < 0.58


def test_dummy_tem_auc_meio(amostra):
    X, y = amostra
    assert validacao_aninhada("dummy", X, y, n_externo=3).metricas["auc_roc"].mean() == pytest.approx(0.5)


def test_importancia_usa_colunas_originais(amostra):
    X, y = amostra
    r = validacao_aninhada("logreg", X, y, n_externo=3, n_interno=2, importancia=True)
    assert set(r.importancia["atributo"]) == set(X.columns)


def test_estatistica_5x2cv_exemplo_calculado_a_mao():
    from m03_validacao import estatistica_5x2cv
    d = np.array([[.02, .01], [.03, .01], [.01, .02], [.02, .02], [.03, .02]])
    t, p = estatistica_5x2cv(d)
    assert t == pytest.approx(2.3905, abs=1e-3)
    assert 0.05 < p < 0.10


def test_estatistica_5x2cv_sem_variancia_nao_divide_por_zero():
    from m03_validacao import estatistica_5x2cv
    t, p = estatistica_5x2cv(np.zeros((5, 2)))
    assert t == 0.0 and p == 1.0


def test_f_combinado_5x2cv_exemplo_calculado_a_mao():
    from m03_validacao import estatistica_f_5x2cv
    d = np.array([[.02, .01], [.03, .01], [.01, .02], [.02, .02], [.03, .02]])
    f, p = estatistica_f_5x2cv(d)
    assert f == pytest.approx(0.0041 / (2 * 0.00035), rel=1e-6)
    assert 0.01 < p < 0.05


def test_teste_5x2cv_modelo_contra_si_mesmo(amostra):
    from m03_validacao import teste_5x2cv
    X, y = amostra
    r = teste_5x2cv("logreg", "logreg", X, y, n_interno=2)
    assert r["t"] == 0.0 and np.allclose(r["diferencas"], 0)
    assert r["f"] == 0.0 and r["p_f"] == 1.0
