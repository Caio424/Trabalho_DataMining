"""Etapa 3 - Comparação de duas variáveis após a limpeza e análise bivariada vs alvo.

Gera:
  figuras/fig3_idade_imc.png          IDADE × IMC antes/depois da limpeza
  figuras/fig4_numericas_alvo.png     boxplots das numéricas por classe do alvo
  figuras/fig5_categoricas_alvo.png   % Anormal por categoria
  tabelas/tab_associacao_alvo.csv     ranking de associação com o alvo
"""
import numpy as np
import pandas as pd
from scipy import stats

from config import (ALVO, ARQ_LIMPO, COR_ANORMAL, COR_ANTES, COR_DEPOIS, COR_FAIXA, COR_NORMAL,
                    FAIXAS, NUMERICAS, ORDEM_PPA, TINTA_2, UNIDADES, registrar_resultados,
                    salvar_figura, salvar_tabela)
from p01_perfil import carregar_bruto, numericas_brutas
import matplotlib.pyplot as plt

N_MIN_CATEGORIA = 30   # categorias menores são agrupadas só na figura
CAT_BIVARIADA = ["SEXO", "PULSOS", "PPA", "B2", "SOPRO", "HDA 1", "MOTIVO1", "MOTIVO2", "Convenio"]


def carregar_limpo():
    return pd.read_csv(ARQ_LIMPO, parse_dates=["Atendimento", "DN"])


# ------------------------------------------------------------ estatísticas
def mann_whitney(df, col):
    a = df.loc[df[ALVO] == "Anormal", col].dropna()
    n = df.loc[df[ALVO] == "Normal", col].dropna()
    u, p = stats.mannwhitneyu(a, n, alternative="two-sided")
    r = 2 * u / (len(a) * len(n)) - 1       # rank-biserial: >0 => Anormal maior
    return {"Variável": col, "Tipo": "Numérica", "Teste": "Mann-Whitney",
            "Estatística": u, "p-valor": p, "Efeito": r, "Medida de efeito": "r rank-bisserial",
            "Mediana Normal": n.median(), "Mediana Anormal": a.median(), "n": len(a) + len(n)}


def cramer(df, col):
    tab = pd.crosstab(df[col], df[ALVO])
    chi2, p, gl, _ = stats.chi2_contingency(tab)
    v = np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape) - 1)))
    return {"Variável": col, "Tipo": "Categórica", "Teste": "Qui-quadrado",
            "Estatística": chi2, "p-valor": p, "Efeito": v, "Medida de efeito": "V de Cramér",
            "n": int(tab.values.sum())}


def tabela_associacao(df):
    linhas = [mann_whitney(df, c) for c in NUMERICAS]
    linhas += [cramer(df, c) for c in CAT_BIVARIADA]
    aux = df.assign(**{"PA medida": np.where(df["PA SISTOLICA"].notna(), "Sim", "Não")})
    linhas.append(cramer(aux, "PA medida"))
    t = pd.DataFrame(linhas)
    t["|Efeito|"] = t["Efeito"].abs()
    return t.sort_values("|Efeito|", ascending=False).drop(columns="|Efeito|")


# ------------------------------------------------------------ figuras
def figura_idade_imc(bruto, limpo):
    b = numericas_brutas(bruto)[["IDADE", "IMC"]].dropna()
    l = limpo[["IDADE", "IMC"]].dropna()
    fig, eixos = plt.subplots(1, 3, figsize=(7.1, 2.35), gridspec_kw=dict(width_ratios=[1, 1, 1.1]))

    ax = eixos[0]
    ax.add_patch(plt.Rectangle((0, 10), 19, 30, color=COR_FAIXA, alpha=.15, lw=0))
    ax.scatter(b["IDADE"], b["IMC"], s=3, color=COR_ANTES, alpha=.35, lw=0)
    ax.set_yscale("symlog", linthresh=50)
    ax.set_title(f"(a) Bruto (n = {len(b):,})".replace(",", "."))
    ax.set_xlabel("IDADE (anos)"); ax.set_ylabel("IMC (kg/m², escala symlog)")

    ax = eixos[1]
    ax.add_patch(plt.Rectangle((0, 10), 19, 30, color=COR_FAIXA, alpha=.15, lw=0))
    ax.scatter(l["IDADE"], l["IMC"], s=3, color=COR_DEPOIS, alpha=.25, lw=0)
    ax.set_xlim(-.5, 19.5); ax.set_ylim(8, 42)
    ax.set_title(f"(b) Limpo (n = {len(l):,})".replace(",", "."))
    ax.set_xlabel("IDADE (anos)"); ax.set_ylabel("IMC (kg/m²)")

    ax = eixos[2]
    bins = np.arange(0, 20, 1)
    for dados, cor, rot in ((b[(b.IDADE >= 0) & (b.IDADE < 19)], COR_ANTES, "Bruto"),
                            (l, COR_DEPOIS, "Limpo")):
        g = dados.groupby(pd.cut(dados["IDADE"], bins, right=False), observed=True)["IMC"]
        med, q1, q3 = g.median(), g.quantile(.25), g.quantile(.75)
        x = bins[:-1][:len(med)] + .5
        ax.fill_between(x, q1.values, q3.values, color=cor, alpha=.15, lw=0)
        ax.plot(x, med.values, color=cor, lw=2, marker="o", ms=3, label=f"{rot}: mediana e IIQ")
    ax.set_xlabel("IDADE (faixa de 1 ano)"); ax.set_ylabel("IMC (kg/m²)")
    ax.set_title("(c) IMC mediano por idade")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(pad=.5)

    rho_b = stats.spearmanr(b["IDADE"], b["IMC"]).statistic
    rho_l = stats.spearmanr(l["IDADE"], l["IMC"]).statistic
    registrar_resultados("idade_imc", {
        "n_bruto": len(b), "n_limpo": len(l),
        "rho_bruto": round(rho_b, 3), "rho_limpo": round(rho_l, 3),
        "fora_bruto_pct": round(100 * ((b.IMC < 10) | (b.IMC > 40) | (b.IDADE < 0) | (b.IDADE > 19)).mean(), 1),
        "imc_mediano_por_idade": l.groupby(l.IDADE.astype(int))["IMC"].median().round(1).to_dict(),
    })
    return salvar_figura(fig, "fig3_idade_imc")


def figura_numericas_alvo(df, assoc):
    fig, eixos = plt.subplots(2, 4, figsize=(7.1, 3.3))
    efeitos = assoc.set_index("Variável")
    for ax, c in zip(eixos.flat, NUMERICAS):
        dados = [df.loc[df[ALVO] == k, c].dropna() for k in ("Normal", "Anormal")]
        bp = ax.boxplot(dados, widths=.55, patch_artist=True, showfliers=False,
                        medianprops=dict(color="black", lw=1),
                        whiskerprops=dict(lw=.8), capprops=dict(lw=.8))
        for caixa, cor in zip(bp["boxes"], (COR_NORMAL, COR_ANORMAL)):
            caixa.set(facecolor=cor, alpha=.75, lw=.6)
        ax.set_xticks([1, 2], ["Normal", "Anormal"])
        e = efeitos.loc[c]
        p = "p<0,001" if e["p-valor"] < .001 else f"p={e['p-valor']:.3f}".replace(".", ",")
        r = f"r={e['Efeito']:+.2f}".replace(".", ",")
        ax.set_title(f"{c} ({UNIDADES[c]})\n{r}; {p}", fontsize=7.5, linespacing=1.3)
        ax.grid(axis="x", visible=False)
    ax = eixos.flat[-1]
    vc = df[ALVO].value_counts().reindex(["Normal", "Anormal"])
    ax.bar(vc.index, vc.values, color=[COR_NORMAL, COR_ANORMAL], width=.55, alpha=.85)
    for i, v in enumerate(vc.values):
        ax.text(i, v, f"{v:,}\n({v/vc.sum()*100:.1f}%)".replace(",", "."), ha="center",
                va="bottom", fontsize=6)
    ax.set_ylim(0, vc.max() * 1.3)
    ax.set_title("Alvo (NORMAL X ANORMAL)")
    ax.grid(axis="x", visible=False)
    fig.tight_layout(pad=.5, h_pad=.8)
    return salvar_figura(fig, "fig4_numericas_alvo")


def figura_categoricas_alvo(df, assoc):
    base = (df[ALVO] == "Anormal").mean() * 100
    efeitos = assoc.set_index("Variável")
    fig, eixos = plt.subplots(3, 3, figsize=(7.1, 4.7))
    for ax, c in zip(eixos.flat, CAT_BIVARIADA):
        s = df[c].copy()
        contagem = s.value_counts()
        raras = contagem[contagem < N_MIN_CATEGORIA].index
        if c != "PPA" and len(raras) > 0:
            s[s.isin(raras)] = f"Outras (n<{N_MIN_CATEGORIA})"
        g = df.assign(**{c: s}).dropna(subset=[c]).groupby(c)[ALVO]
        taxa = g.apply(lambda s: (s == "Anormal").mean() * 100)
        n = g.size()
        if c == "PPA":
            taxa, n = taxa.reindex(ORDEM_PPA), n.reindex(ORDEM_PPA)
        else:
            taxa = taxa.sort_values()
            n = n.reindex(taxa.index)
        if c == "Convenio":  # mostra só os maiores
            top = n.sort_values().index[-8:]
            taxa, n = taxa.reindex(top).sort_values(), n.reindex(top)
            n = n.reindex(taxa.index)
        rot = [f"{str(k)[:22]} (n={v})" for k, v in zip(taxa.index, n.values)]
        ax.barh(rot, taxa.values, color=COR_ANORMAL, alpha=.85, height=.65)
        ax.axvline(base, color=TINTA_2, lw=.8, ls="--")
        ax.set_xlim(0, 100)
        ax.set_xlabel("% Anormal", fontsize=6)
        ax.tick_params(axis="y", labelsize=5.6)
        ax.set_title(f"{c} (V={efeitos.loc[c, 'Efeito']:.2f})".replace(".", ","))
        ax.grid(axis="y", visible=False)
    fig.tight_layout(pad=.5, w_pad=.5, h_pad=.7)
    registrar_resultados("taxa_base_anormal_pct", round(base, 1))
    return salvar_figura(fig, "fig5_categoricas_alvo")


def resumo_categorias_alvo(df):
    """% Anormal por categoria (usado no texto do relatório)."""
    out = {}
    for c in CAT_BIVARIADA:
        g = df.dropna(subset=[c]).groupby(c)[ALVO]
        out[c] = {str(k): [round((s == "Anormal").mean() * 100, 1), int(len(s))] for k, s in g}
    pa = np.where(df["PA SISTOLICA"].notna(), "Sim", "Não")
    out["PA medida"] = {k: [round((df.loc[pa == k, ALVO] == "Anormal").mean() * 100, 1),
                            int((pa == k).sum())] for k in ("Sim", "Não")}
    return out


def executar():
    bruto = carregar_bruto()
    limpo = carregar_limpo()
    assoc = tabela_associacao(limpo)
    salvar_tabela(assoc, "tab_associacao_alvo")
    corr = limpo[NUMERICAS].corr(method="spearman").round(2)
    salvar_tabela(corr.reset_index().rename(columns={"index": "Variável"}), "tab_correlacao_spearman")
    registrar_resultados("correlacao_spearman", corr.to_dict())
    registrar_resultados("categorias_alvo", resumo_categorias_alvo(limpo))
    figura_idade_imc(bruto, limpo)
    figura_numericas_alvo(limpo, assoc)
    figura_categoricas_alvo(limpo, assoc)
    print("[3] bivariada: ranking de associação salvo")
    return assoc


if __name__ == "__main__":
    executar()
