"""Configurações compartilhadas pelo pipeline: caminhos, faixas clínicas,
mapeamentos de categorias e estilo dos gráficos."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- caminhos
RAIZ = Path(__file__).resolve().parent.parent
ARQ_BRUTO = RAIZ / "UCMF_raw.csv"
SAIDA = RAIZ / "saida"
FIGURAS = SAIDA / "figuras"
TABELAS = SAIDA / "tabelas"
ARQ_LIMPO = SAIDA / "UCMF_clean.csv"
ARQ_TRANSF = SAIDA / "UCMF_transformed.csv"
ARQ_RESULTADOS = SAIDA / "resultados.json"
ARQ_RELATORIO = SAIDA / "Relatorio_A1_Parte1.docx"

for _p in (SAIDA, FIGURAS, TABELAS):
    _p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- variáveis
ALVO = "NORMAL X ANORMAL"
NUMERICAS = ["IDADE", "Peso", "Altura", "IMC", "PA SISTOLICA", "PA DIASTOLICA", "FC"]
CATEGORICAS = ["SEXO", "Convenio", "PULSOS", "PPA", "B2", "SOPRO",
               "HDA 1", "HDA2", "MOTIVO1", "MOTIVO2"]
DATAS = ["Atendimento", "DN"]

# Faixas de plausibilidade para 0-19 anos (limites fisiológicos amplos, não de
# normalidade). Referências: OMS Child Growth Standards / Growth Reference 5-19
# (peso, estatura, IMC); Fleming et al., Lancet 2011 (FC em crianças);
# Flynn et al., AAP Clinical Practice Guideline 2017 (PA pediátrica).
FAIXAS = {
    "IDADE": (0, 19),
    "Peso": (1, 150),
    "Altura": (40, 200),
    "IMC": (10, 40),
    "PA SISTOLICA": (60, 200),
    "PA DIASTOLICA": (30, 130),
    "FC": (40, 220),
}
UNIDADES = {"IDADE": "anos", "Peso": "kg", "Altura": "cm", "IMC": "kg/m²",
            "PA SISTOLICA": "mmHg", "PA DIASTOLICA": "mmHg", "FC": "bpm"}

# ---------------------------------------------------------------- mapeamentos
# chaves já normalizadas (minúsculas, sem acento, sem espaços nas pontas)
MAP_ALVO = {"normal": "Normal", "normais": "Normal", "anormal": "Anormal"}
MAP_SEXO = {"m": "M", "masculino": "M", "f": "F", "feminino": "F"}  # Indeterminado -> NaN
MAP_SOPRO = {"ausente": "Ausente", "sistolico": "Sistólico", "continuo": "Contínuo",
             "diastolico": "Diastólico", "sistolico e diastolico": "Sistólico e diastólico"}
MAP_PULSOS = {"normais": "Normais", "amplos": "Amplos", "diminuidos": "Diminuídos",
              "femorais diminuidos": "Femorais diminuídos", "outro": "Outro"}
MAP_PPA = {"normal": "Normal",
           "pre-hipertensao pas": "Pré-HAS", "pre-hipertensao pad": "Pré-HAS",
           "has-1 pas": "HAS-1", "has-1 pad": "HAS-1",
           "has-2 pas": "HAS-2", "has-2 pad": "HAS-2"}  # #VALUE! / Não Calculado -> NaN
ORDEM_PPA = ["Normal", "Pré-HAS", "HAS-1", "HAS-2"]
LIMIAR_RARO_CONVENIO = 0.01

# ---------------------------------------------------------------- estilo
# Paleta categórica de referência (skill dataviz), slots em ordem fixa.
COR_NORMAL = "#2a78d6"    # slot 1 - azul
COR_ANORMAL = "#eb6834"   # slot 2 - laranja
COR_ANTES = "#9a9892"     # neutro para "dado bruto"
COR_DEPOIS = "#2a78d6"
COR_FAIXA = "#1baf7a"     # faixa de referência
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
GRADE = "#e4e3df"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 7.5,
    "axes.titlesize": 8,
    "axes.labelsize": 7.5,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "axes.edgecolor": TINTA_2,
    "axes.labelcolor": TINTA,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "text.color": TINTA,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRADE,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "figure.dpi": 100,
    "savefig.dpi": 220,
    "savefig.bbox": "tight",
})


def salvar_figura(fig, nome):
    caminho = FIGURAS / f"{nome}.png"
    fig.savefig(caminho, facecolor="white")
    plt.close(fig)
    return caminho


def salvar_tabela(df, nome):
    caminho = TABELAS / f"{nome}.csv"
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return caminho


def registrar_resultados(chave, valor):
    """Acumula números usados no texto do relatório em resultados.json."""
    dados = json.loads(ARQ_RESULTADOS.read_text(encoding="utf-8")) if ARQ_RESULTADOS.exists() else {}
    dados[chave] = valor
    ARQ_RESULTADOS.write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str),
                              encoding="utf-8")


def ler_resultados():
    return json.loads(ARQ_RESULTADOS.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- A2 (modelagem)
RANDOM_STATE = 42
SAIDA_A2 = SAIDA / "a2"
FIGURAS_A2 = SAIDA_A2 / "figuras"
ARTIGO = RAIZ / "artigo"
for _p in (SAIDA_A2, FIGURAS_A2, ARTIGO / "figuras", ARTIGO / "tabelas"):
    _p.mkdir(parents=True, exist_ok=True)

NUM_LOG = ["IMC", "PA SISTOLICA", "FC"]
NUM_LINEAR = ["IDADE", "PA DIASTOLICA"]
NOMINAIS = ["SEXO", "Convenio", "PULSOS", "B2", "SOPRO", "MOTIVO1", "MOTIVO2"]
SINTOMAS = ["Cianose", "Desmaio/tontura", "Dispneia", "Dor precordial", "Ganho de peso",
            "Outro", "Palpitação"]
# valor = colunas excluídas em cada cenário de atributos
CENARIOS = {"principal": ["SOPRO"], "com_sopro": [], "restrito": ["SOPRO", "MOTIVO1", "MOTIVO2"]}
