import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def test_main_a2_importa_todas_as_etapas_sem_pular_em_silencio():
    codigo = ("import sys, main_a2; "
              "assert {'m04_experimentos', 'm05_interpretacao', 'm06_figuras_tabelas'} <= set(sys.modules)")
    r = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-500:]


def test_saida_redirecionada_aceita_caracteres_fora_do_cp1252():
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    codigo = "import main_a2; print('12.873 → 11.470')"
    r = subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, env=env,
                       capture_output=True)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-500:]
    assert "→" in r.stdout.decode("utf-8")
