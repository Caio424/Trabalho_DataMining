import pandas as pd


def test_confusao_soma_o_total(saida_reduzida):
    c = pd.read_csv(saida_reduzida / "confusao.csv")
    assert (c[["vn", "fp", "fn", "vp"]].sum(axis=1) == 900).all()
    assert len(c) == 2


def test_limiar_monotono(saida_reduzida):
    lim = pd.read_csv(saida_reduzida / "limiar.csv").sort_values("limiar")
    assert lim["recall"].is_monotonic_decreasing and lim["fn"].is_monotonic_increasing
    assert len(lim) == 13


def test_resumo_tem_uma_linha_por_combinacao(saida_reduzida):
    r = pd.read_csv(saida_reduzida / "resumo_metricas.csv")
    assert not r.duplicated(["experimento", "cenario", "modelo", "estrategia"]).any()
    assert {"auc_roc_media", "auc_roc_dp", "recall_media", "f1_media"} <= set(r.columns)


def test_perfil_de_erros_tem_os_quatro_grupos(saida_reduzida):
    assert set(pd.read_csv(saida_reduzida / "perfil_erros.csv")["grupo"]) == {"VP", "FN", "FP", "VN"}


def test_importancia_e_razao_de_chances(saida_reduzida):
    imp = pd.read_csv(saida_reduzida / "importancia_resumo.csv")
    assert imp.groupby("modelo")["queda_auc_media"].apply(lambda s: s.is_monotonic_decreasing).all()
    rc = pd.read_csv(saida_reduzida / "razao_chances.csv")
    assert len(rc) == 10 and (rc["razao_chances"] > 0).all()
