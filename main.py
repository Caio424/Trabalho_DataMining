"""Pipeline completo da A1 - Parte 1 (pré-processamento do UCMF).

Uso:  python main.py
Saídas em ./saida (CSVs limpo/transformado, figuras, tabelas e o relatório .docx).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from config import ARQ_RESULTADOS  # noqa: E402
import p01_perfil, p02_limpeza, p03_bivariada, p04_transformacao, p05_relatorio  # noqa: E402

if __name__ == "__main__":
    ARQ_RESULTADOS.unlink(missing_ok=True)   # recomeça do zero a cada execução
    p01_perfil.executar()
    p02_limpeza.executar()
    p03_bivariada.executar()
    p04_transformacao.executar()
    p05_relatorio.executar()
