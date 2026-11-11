"""Etapa 1 - Carga e análise univariada do dado BRUTO.

Gera:
  figuras/fig1_numericas_bruto.png   boxplots das numéricas + datas com faixa de referência
  figuras/fig2_categoricas_bruto.png barras das categóricas (grafias duplicadas e ausentes)
  tabelas/tab_categoricas_bruto.csv  resumo das categóricas
"""
import numpy as np
import pandas as pd

from config import (ALVO, ARQ_BRUTO, CATEGORICAS, COR_ANTES, COR_FAIXA, FAIXAS, NUMERICAS,
                    TINTA_2, UNIDADES, registrar_resultados, salvar_figura, salvar_tabela)
import matplotlib.pyplot as plt


def carregar_bruto():
    return pd.read_csv(ARQ_BRUTO, dtype={"Atendimento": str, "DN": str})


def numericas_brutas(df):
    """Versão numérica 'ingênua' do bruto (FC é texto; faixas viram NaN)."""
    out = df[NUMERICAS].copy()
    out["FC"] = pd.to_numeric(df["FC"], errors="coerce")
    return out


def descritiva(df_num):
    """Estatísticas descritivas por variável numérica."""
    linhas = []
    for c in df_num.columns:
        s = df_num[c]
        linhas.append({
            "Variável": c, "n": int(s.notna().sum()),
            "% ausente": round(100 * s.isna().mean(), 1),
            "Média": s.mean(), "DP": s.std(), "Mín": s.min(), "Q1": s.quantile(.25),
            "Mediana": s.median(), "Q3": s.quantile(.75), "Máx": s.max(),
            "Assimetria": s.skew(),
        })
    return pd.DataFrame(linhas)


def resumo_categoricas(df, colunas):
    linhas = []
    for c in colunas:
        s = df[c]
        vc = s.value_counts()
        linhas.append({
            "Variável": c, "Categorias": int(s.nunique()),
            "% ausente": round(100 * s.isna().mean(), 1),
            "Moda": vc.index[0] if len(vc) else "-",
            "% moda": round(100 * vc.iloc[0] / s.notna().sum(), 1) if len(vc) else np.nan,
        })
    return pd.DataFrame(linhas)


def _anos(serie):
    """Ano das datas brutas, só para visualização (serial Excel ignorado aqui)."""
    d = pd.to_datetime(serie, format="%d/%m/%y", errors="coerce")
    return d.dt.year


def figura_numericas(df):
    num = numericas_brutas(df)
    fig, eixos = plt.subplots(2, 4, figsize=(7.1, 3.1))
    for ax, c in zip(eixos.flat, NUMERICAS):
        s = num[c].dropna()
        lo, hi = FAIXAS[c]
        ax.axvspan(lo, hi, color=COR_FAIXA, alpha=.15, lw=0)
        ax.boxplot(s, vert=False, widths=.5, patch_artist=True,
                   boxprops=dict(facecolor=COR_ANTES, alpha=.6, lw=.8),
                   medianprops=dict(color="black", lw=1),
                   flierprops=dict(marker="o", ms=2.5, mfc=COR_ANTES, mec="none", alpha=.5),
                   whiskerprops=dict(lw=.8), capprops=dict(lw=.8))
        fora = ((s < lo) | (s > hi)).mean() * 100
        ax.set_title(f"{c} ({UNIDADES[c]})")
        ax.set_yticks([])
        ax.text(.98, .95, f"ausente {num[c].isna().mean()*100:.0f}%\nfora da faixa {fora:.1f}%",
                transform=ax.transAxes, ha="right", va="top", fontsize=6, color=TINTA_2)
    ax = eixos.flat[-1]
    anos = [_anos(df[c]).dropna() for c in ("Atendimento", "DN")]
    ax.boxplot(anos, vert=False, widths=.5, patch_artist=True,
               boxprops=dict(facecolor=COR_ANTES, alpha=.6, lw=.8),
               medianprops=dict(color="black", lw=1),
               flierprops=dict(marker="o", ms=2.5, mfc=COR_ANTES, mec="none", alpha=.5))
    ax.set_yticks([1, 2], ["Atend.", "DN"])
    ax.set_title("Ano das datas")
    fig.tight_layout(pad=.6)
    return salvar_figura(fig, "fig1_numericas_bruto")


def figura_categoricas(df):
    colunas = [ALVO, "SEXO", "PULSOS", "PPA", "B2", "SOPRO",
               "HDA 1", "HDA2", "MOTIVO1", "MOTIVO2", "Convenio"]
    fig, eixos = plt.subplots(3, 4, figsize=(7.1, 5.6))
    for ax, c in zip(eixos.flat, colunas):
        vc = df[c].fillna("(ausente)").value_counts()
        if len(vc) > 9:
            vc = pd.concat([vc.iloc[:8], pd.Series({f"(+{len(vc)-8} outras)": vc.iloc[8:].sum()})])
        vc = vc.iloc[::-1] / len(df) * 100
        rotulos = [str(r)[:24] for r in vc.index]
        cores = ["#c9c7c0" if r.startswith("(") else COR_ANTES for r in vc.index]
        ax.barh(rotulos, vc.values, color=cores, height=.7)
        ax.set_title(f"{c} ({df[c].nunique()} valores)")
        ax.tick_params(axis="y", labelsize=5.8)
        ax.set_xlabel("% dos registros", fontsize=6)
        ax.grid(axis="y", visible=False)
    # último painel: % de ausentes em todas as 21 variáveis
    ax = eixos.flat[-1]
    aus = (df.isna().mean() * 100).sort_values()
    ax.barh(aus.index, aus.values, color=COR_ANTES, height=.7)
    ax.set_title("% ausente (todas)")
    ax.tick_params(axis="y", labelsize=5)
    ax.set_xlabel("% dos registros", fontsize=6)
    ax.grid(axis="y", visible=False)
    fig.tight_layout(pad=.5, w_pad=.4, h_pad=.6)
    return salvar_figura(fig, "fig2_categoricas_bruto")


def executar():
    df = carregar_bruto()
    registrar_resultados("bruto_shape", list(df.shape))
    registrar_resultados("bruto_duplicatas_sem_id", int(df.drop(columns="ID").duplicated().sum()))
    registrar_resultados("bruto_ids_duplicados", int(df["ID"].duplicated().sum()))
    registrar_resultados("bruto_ausentes_pct", (df.isna().mean() * 100).round(1).to_dict())
    registrar_resultados("bruto_n_categorias", {c: int(df[c].nunique()) for c in CATEGORICAS + [ALVO]})
    salvar_tabela(resumo_categoricas(df, [ALVO] + CATEGORICAS), "tab_categoricas_bruto")
    figura_numericas(df)
    figura_categoricas(df)
    print(f"[1] perfil bruto: {df.shape[0]} linhas x {df.shape[1]} colunas")
    return df


if __name__ == "__main__":
    executar()
