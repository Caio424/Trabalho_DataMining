import pytest

from m01_atributos import carregar_xy


def test_dimensoes_e_alvo():
    X, y, grupos = carregar_xy("principal")
    assert len(X) == len(y) == len(grupos) == 11470
    assert set(y.unique()) == {0, 1}
    assert int(y.sum()) == 4894


def test_cenario_principal_exclui_sopro_e_identificadores():
    X, _, _ = carregar_xy("principal")
    proibidas = {"SOPRO", "ID", "Atendimento", "DN", "Peso", "Altura",
                 "HDA 1", "HDA2", "PPA", "NORMAL X ANORMAL"}
    assert proibidas.isdisjoint(X.columns)


def test_cenarios_diferem_so_nas_colunas_excluidas():
    p, c, r = (set(carregar_xy(k)[0].columns) for k in ("principal", "com_sopro", "restrito"))
    assert c - p == {"SOPRO"}
    assert p - r == {"MOTIVO1", "MOTIVO2"}
    assert p - set(carregar_xy("sem_b2")[0].columns) == {"B2"}


def test_atributos_derivados():
    X, _, _ = carregar_xy("principal")
    assert sum(col.startswith("sint_") for col in X.columns) == 7
    assert set(X["ppa_ord"].unique()) <= {0, 1, 2, 3}
    assert X["ppa_ausente"].mean() == pytest.approx(0.819, abs=0.002)


def test_nada_e_imputado_aqui():
    X, _, _ = carregar_xy("principal")
    assert X["IMC"].isna().sum() > 0


def test_grupos_sem_dn_sao_unicos():
    _, _, grupos = carregar_xy("principal")
    sem_dn = grupos[grupos.str.startswith("linha_")]
    assert sem_dn.is_unique and len(sem_dn) == 587
