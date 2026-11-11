import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(scope="session")
def xy():
    from m01_atributos import carregar_xy
    X, y, grupos = carregar_xy("principal")
    ordem = X.sample(frac=1, random_state=42).index
    X, y, grupos = X.loc[ordem], y.loc[ordem], grupos.loc[ordem]
    return X.reset_index(drop=True), y.reset_index(drop=True), grupos.reset_index(drop=True)


@pytest.fixture(scope="session")
def amostra(xy):
    X, y, _ = xy
    return X.iloc[:1200].reset_index(drop=True), y.iloc[:1200].reset_index(drop=True)
