"""Etapa 4 - Transformações para modelagem (Parte 2).

Obs.: medianas/médias aqui são ajustadas no conjunto inteiro para gerar um
arquivo pronto para exploração. Na modelagem, o imputador e o padronizador
devem ser reajustados SOMENTE no conjunto de treino (evita vazamento).

Gera:
  UCMF_transformed.csv
  tabelas/tab_transformacoes.csv
"""
import numpy as np
import pandas as pd

from config import ALVO, ARQ_TRANSF, ORDEM_PPA, registrar_resultados, salvar_tabela
from p03_bivariada import carregar_limpo

CONTINUAS = ["IDADE", "IMC", "PA SISTOLICA", "PA DIASTOLICA", "FC"]
NOMINAIS = ["SEXO", "Convenio", "PULSOS", "B2", "SOPRO", "MOTIVO1", "MOTIVO2"]
LIMIAR_AUSENTE = 0.20
LIMIAR_ASSIMETRIA = 1.0
N_MIN_DUMMY = 30


def slug(txt):
    import unicodedata, re
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    return re.sub(r"[^0-9a-zA-Z]+", "_", txt).strip("_").lower()


def executar():
    df = carregar_limpo()
    passos = []
    n_colunas_limpo = df.shape[1]

    # 1) remoção de identificadores e redundâncias
    rho = df[["IDADE", "Peso", "Altura"]].corr(method="spearman")
    removidas = ["ID", "Atendimento", "DN", "Peso", "Altura"]
    df = df.drop(columns=removidas)
    passos.append(("Remoção de colunas", "ID, Atendimento, DN, Peso, Altura",
                   f"ID não é preditivo; as datas já estão resumidas em IDADE; Peso e Altura são "
                   f"quase colineares com IDADE (ρ de Spearman = {rho.loc['IDADE','Peso']:.2f} e "
                   f"{rho.loc['IDADE','Altura']:.2f}) e sua informação de composição corporal está no IMC"
                   .replace("0.", "0,")))

    # 2) sintomas (HDA 1 ∪ HDA2) -> indicadores binários
    sintomas = sorted((set(df["HDA 1"].dropna()) | set(df["HDA2"].dropna())) - {"Assintomático"})
    for s in sintomas:
        df[f"sint_{slug(s)}"] = ((df["HDA 1"] == s) | (df["HDA2"] == s)).astype(int)
    df["hda_ausente"] = df["HDA 1"].isna().astype(int)
    df = df.drop(columns=["HDA 1", "HDA2"])
    passos.append(("Engenharia de atributos", f"HDA 1 + HDA2 → {len(sintomas)} indicadores de sintoma + hda_ausente",
                   "HDA2 tem 96% de ausentes; como as duas colunas usam o mesmo vocabulário, "
                   "a união em indicadores (multi-hot) preserva o 2º histórico sem descartar a coluna"))

    # 3) indicadores de ausência
    df["pa_ausente"] = df["PA SISTOLICA"].isna().astype(int)
    df["imc_ausente"] = df["IMC"].isna().astype(int)
    df["ppa_ausente"] = df["PPA"].isna().astype(int)
    passos.append(("Indicadores de ausência", "pa_ausente, imc_ausente, ppa_ausente",
                   f"Variáveis com >{LIMIAR_AUSENTE:.0%} de ausentes; a ausência é informativa "
                   "(% Anormal difere entre quem teve ou não a PA medida)"))

    # 4) PPA ordinal
    df["PPA"] = df["PPA"].map({k: i for i, k in enumerate(ORDEM_PPA)})
    df["PPA"] = df["PPA"].fillna(0)
    passos.append(("Codificação ordinal", "PPA: Normal=0, Pré-HAS=1, HAS-1=2, HAS-2=3",
                   "As classes têm ordem clínica de gravidade; ausentes = 0 (a maioria das medidas é Normal) "
                   "acompanhados de ppa_ausente"))

    # 5) log1p nas assimétricas (assimetria medida só nos valores observados)
    assim_antes = df[CONTINUAS].skew()
    logs = assim_antes[assim_antes.abs() > LIMIAR_ASSIMETRIA].index.tolist()
    df[logs] = np.log1p(df[logs])
    assim_depois = df[CONTINUAS].skew()
    passos.append(("Transformação log(1 + x)", ", ".join(logs),
                   f"Assimetria > {LIMIAR_ASSIMETRIA:g} (cauda à direita): "
                   + "; ".join(f"{c} {assim_antes[c]:.2f}→{assim_depois[c]:.2f}".replace(".", ",") for c in logs)
                   + "; reduz a influência de valores altos em modelos lineares/distância"))

    # 6) imputação das contínuas pela mediana
    medianas = df[CONTINUAS].median()
    df[CONTINUAS] = df[CONTINUAS].fillna(medianas)
    passos.append(("Imputação", "IDADE, IMC, PAS, PAD, FC → mediana",
                   "Mediana é robusta à assimetria; combinada aos indicadores de ausência não esconde o padrão de falta"))

    # 7) padronização
    medias, dps = df[CONTINUAS].mean(), df[CONTINUAS].std()
    df[CONTINUAS] = (df[CONTINUAS] - medias) / dps
    passos.append(("Padronização (z-score)", ", ".join(CONTINUAS),
                   "Escalas diferentes (anos, kg/m², mmHg, bpm); necessário para KNN, SVM, regressão regularizada e redes"))

    # 8) one-hot das nominais
    n_agrupadas = 0
    for c in NOMINAIS:
        df[c] = df[c].fillna("Nao informado")
        cont = df[c].value_counts()
        raras = cont[cont < N_MIN_DUMMY].index
        n_agrupadas += len(raras)
        df.loc[df[c].isin(raras), c] = "Outro"
    df = pd.get_dummies(df, columns=NOMINAIS, prefix=[slug(c) for c in NOMINAIS], dtype=int)
    passos.append(("One-hot encoding", ", ".join(NOMINAIS),
                   f"Categorias sem ordem; ausentes viram 'Nao informado'; {n_agrupadas} categorias com n<{N_MIN_DUMMY} "
                   "agrupadas em 'Outro' para evitar colunas quase vazias"))

    # 9) alvo
    df[ALVO] = (df[ALVO] == "Anormal").astype(int)
    df = df.rename(columns={ALVO: "ALVO_ANORMAL"})
    df = df[[c for c in df.columns if c != "ALVO_ANORMAL"] + ["ALVO_ANORMAL"]]
    passos.append(("Codificação do alvo", "NORMAL X ANORMAL → ALVO_ANORMAL (1 = Anormal)",
                   "Formato binário exigido pelos classificadores"))

    df.columns = [slug(c) if c != "ALVO_ANORMAL" else c for c in df.columns]
    df.to_csv(ARQ_TRANSF, index=False, encoding="utf-8-sig")
    salvar_tabela(pd.DataFrame(passos, columns=["Transformação", "Variáveis", "Justificativa"]),
                  "tab_transformacoes")
    registrar_resultados("transformado", {
        "shape": list(df.shape), "colunas_limpo": n_colunas_limpo,
        "log1p": logs, "assimetria_antes": assim_antes.round(2).to_dict(),
        "assimetria_depois": assim_depois.round(2).to_dict(),
        "sintomas": sintomas,
        "ausentes_restantes": int(df.isna().sum().sum()),
    })
    print(f"[4] transformação: {df.shape[0]} linhas x {df.shape[1]} colunas; ausentes = {df.isna().sum().sum()}")
    return df


if __name__ == "__main__":
    executar()
