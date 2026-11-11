import json

import pandas as pd

from m04_experimentos import executar


def test_execucao_reduzida_gera_todos_os_arquivos(saida_reduzida):
    for nome in ["metricas_cv.csv", "oof.csv", "melhores_params.json",
                 "importancia.csv", "teste_5x2cv.json", "resumo.json"]:
        assert (saida_reduzida / nome).exists()
    m = pd.read_csv(saida_reduzida / "metricas_cv.csv")
    assert set(m["experimento"]) == {"principal", "cenarios", "desbalanceamento", "agrupado"}
    principal = m[m["experimento"] == "principal"]
    assert set(principal["modelo"]) == {"dummy", "logreg", "arvore", "rf", "gb"}
    assert set(m.loc[m["experimento"] == "desbalanceamento", "estrategia"]) == {
        "nenhum", "class_weight", "smote", "subamostragem"}
    assert json.loads((saida_reduzida / "resumo.json").read_text())["melhor_complexo"] in {"arvore", "rf", "gb"}


def test_execucao_reduzida_e_reprodutivel(saida_reduzida, tmp_path):
    executar(n_amostra=900, n_externo=3, n_interno=2, destino=tmp_path)
    pd.testing.assert_frame_equal(pd.read_csv(saida_reduzida / "metricas_cv.csv"),
                                  pd.read_csv(tmp_path / "metricas_cv.csv"))
