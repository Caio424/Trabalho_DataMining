import json

import pandas as pd
import pytest

from m06_figuras_tabelas import executar

ARTEFATOS = ["figuras/fig1_leakage.pdf", "figuras/fig2_curvas.pdf",
             "figuras/fig3_erros_importancia.pdf", "tabelas/tab_dados.tex",
             "tabelas/tab_modelos.tex", "tabelas/tab_ablacao.tex", "numeros.tex"]


@pytest.fixture(scope="module")
def artigo(saida_reduzida, tmp_path_factory):
    destino = tmp_path_factory.mktemp("artigo")
    executar(origem=saida_reduzida, destino=destino)
    return destino


def test_gera_todos_os_artefatos(artigo):
    for rel in ARTEFATOS:
        assert (artigo / rel).stat().st_size > 0


def test_numeros_batem_com_o_resumo(saida_reduzida, artigo):
    resumo = pd.read_csv(saida_reduzida / "resumo_metricas.csv")
    melhor = json.loads((saida_reduzida / "resumo.json").read_text())["melhor_complexo"]
    auc = resumo.query("experimento == 'principal' and modelo == @melhor")["auc_roc_media"].iloc[0]
    esperado = f"\\newcommand{{\\aucMelhor}}{{{auc:.3f}".replace(".", ",")
    assert esperado in (artigo / "numeros.tex").read_text(encoding="utf-8")


def test_tabela_de_modelos_usa_virgula_e_tem_cinco_linhas(artigo):
    tex = (artigo / "tabelas/tab_modelos.tex").read_text(encoding="utf-8")
    assert tex.count("\\\\") >= 6 and "0." not in tex


def test_macros_das_correcoes_da_revisao(artigo):
    tex = (artigo / "numeros.tex").read_text(encoding="utf-8")
    for nome in ["fCincoDois", "pFCincoDois", "aucSemBDoisLogreg", "aucSemBDoisMelhor",
                 "recallNenhumMelhor", "especNenhumMelhor", "nBruto", "segundoNome",
                 "ordemDemais", "pctSinalSemMotivos"]:
        assert "\\newcommand{\\" + nome + "}" in tex, nome
    assert "Sem Sopro e B2" in (artigo / "tabelas/tab_ablacao.tex").read_text(encoding="utf-8")


def test_macros_sem_digitos_no_nome(artigo):
    import re
    nomes = re.findall(r"\\newcommand\{\\([^}]*)\}",(artigo / "numeros.tex").read_text(encoding="utf-8"))
    assert nomes and all(re.fullmatch(r"[A-Za-z]+", n) for n in nomes)
    assert len(nomes) == len(set(nomes))
