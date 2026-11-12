"""Pipeline completo da A2 (modelagem do UCMF).

Uso:  python main_a2.py
Gera a limpeza (se faltar o CSV limpo), roda os experimentos, interpreta os
resultados e produz figuras, tabelas e números do artigo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
# no Windows, saída redirecionada usa cp1252 e quebra nos "→" das mensagens de progresso
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from config import ARQ_LIMPO  # noqa: E402

if __name__ == "__main__":
    if not ARQ_LIMPO.exists():
        import p02_limpeza
        p02_limpeza.executar()
    import m04_experimentos
    m04_experimentos.executar()
    for etapa in ("m05_interpretacao", "m06_figuras_tabelas"):
        try:
            modulo = __import__(etapa)
        except ModuleNotFoundError:
            continue
        modulo.executar()
