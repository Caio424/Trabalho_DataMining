"""A2 - Figuras (PDF), tabelas LaTeX e macros com os números citados no artigo.

Todos os números do artigo saem daqui; nada é digitado à mão no .tex.
Uso:  python src/m06_figuras_tabelas.py
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import precision_recall_curve, roc_curve

from config import ARTIGO, COR_ANORMAL, COR_NORMAL, SAIDA_A2, TABELAS, TINTA, TINTA_2
from m01_atributos import carregar_xy
from m02_modelos import ROTULOS

# paleta categórica validada (skill dataviz, slots 1-4) + estilo de linha como 2º canal
CORES = {"logreg": "#2a78d6", "arvore": "#eb6834", "rf": "#1baf7a", "gb": "#eda100"}
LINHAS = {"logreg": "-", "arvore": "--", "rf": "-.", "gb": ":"}
CINZA = "#9a9892"
LARGURA = 3.5  # uma coluna IEEE, em polegadas

NOMES = {"IDADE": "Idade", "IMC": "IMC", "PA SISTOLICA": "PAS", "PA DIASTOLICA": "PAD", "FC": "FC",
         "SEXO": "Sexo", "Convenio": "Convênio", "PULSOS": "Pulsos", "B2": "B2", "SOPRO": "Sopro",
         "MOTIVO1": "Motivo 1", "MOTIVO2": "Motivo 2", "hda_ausente": "HDA ausente",
         "ppa_ord": "PPA", "ppa_ausente": "PPA ausente", "PPA": "PPA", "HDA 1": "HDA 1",
         "PA medida": "PA medida", "sint_cianose": "Sint.: cianose",
         "sint_desmaio_tontura": "Sint.: desmaio", "sint_dispneia": "Sint.: dispneia",
         "sint_dor_precordial": "Sint.: dor precordial", "sint_ganho_de_peso": "Sint.: ganho de peso",
         "sint_outro": "Sint.: outro", "sint_palpitacao": "Sint.: palpitação"}
METRICAS_TAB = [("acuracia", "Acur."), ("acuracia_bal", "Ac. bal."), ("precisao", "Prec."),
                ("recall", "Recall"), ("especificidade", "Espec."), ("f1", "F1"),
                ("auc_roc", "AUC-ROC"), ("auc_pr", "AUC-PR")]
ESTRATEGIA_TXT = {"nenhum": "Sem tratamento", "class_weight": "Pesos por classe",
                  "smote": "SMOTE", "subamostragem": "Subamostragem"}


def num(x, casas: int = 3) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def inteiro(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def _salvar(fig, caminho: Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def _eixos_leves(ax):
    ax.grid(True, color="#e4e3df", linewidth=0.5)
    ax.tick_params(length=2)


# ---------------------------------------------------------------- figuras
def figura_leakage(destino: Path):
    X, y, _ = carregar_xy("com_sopro")
    d = pd.DataFrame({"sopro": X["SOPRO"].fillna("Não informado"), "y": y})
    t = d.groupby("sopro")["y"].agg(["mean", "size"]).query("size >= 30").sort_values("mean")
    assoc = pd.read_csv(TABELAS / "tab_associacao_alvo.csv")
    assoc = assoc.assign(efeito=assoc["Efeito"].abs()).sort_values("efeito")

    fig, (a, b) = plt.subplots(2, 1, figsize=(LARGURA, 3.6), gridspec_kw={"height_ratios": [1, 2.4]})
    a.barh([f"{s} (n={inteiro(n)})" for s, n in zip(t.index, t["size"])], t["mean"] * 100,
           color=COR_ANORMAL, height=0.6)
    for i, v in enumerate(t["mean"] * 100):
        a.text(v + 1.5, i, f"{num(v, 1)}%", va="center", fontsize=6.5, color=TINTA)
    a.axvline(y.mean() * 100, color=TINTA_2, linestyle="--", linewidth=0.8)
    a.set_xlim(0, 110)
    a.set_xlabel("% Anormal")
    a.set_title("(a) % de Anormal por tipo de sopro", loc="left")
    _eixos_leves(a)

    cores = [COR_ANORMAL if v == "SOPRO" else COR_NORMAL for v in assoc["Variável"]]
    b.barh([NOMES.get(v, v) for v in assoc["Variável"]], assoc["efeito"], color=cores, height=0.6)
    b.set_xlabel("Associação com o alvo (V de Cramér ou |r|)")
    b.set_title("(b) Força da associação de cada atributo com o alvo", loc="left")
    _eixos_leves(b)
    fig.tight_layout(h_pad=0.8)
    _salvar(fig, destino / "figuras" / "fig1_leakage.pdf")


def figura_curvas(oof: pd.DataFrame, destino: Path):
    fig, (a, b) = plt.subplots(1, 2, figsize=(LARGURA * 2.05, 2.3))
    prevalencia = None
    for nome in ["logreg", "arvore", "rf", "gb"]:
        o = oof.query("experimento == 'principal' and modelo == @nome")
        prevalencia = o["y"].mean()
        fpr, tpr, _ = roc_curve(o["y"], o["proba"])
        prec, rec, _ = precision_recall_curve(o["y"], o["proba"])
        estilo = dict(color=CORES[nome], linestyle=LINHAS[nome], linewidth=1.4, label=ROTULOS[nome])
        a.plot(fpr, tpr, **estilo)
        b.plot(rec, prec, **estilo)
    a.plot([0, 1], [0, 1], color=CINZA, linewidth=0.8, linestyle=(0, (1, 2)), label="Acaso")
    b.axhline(prevalencia, color=CINZA, linewidth=0.8, linestyle=(0, (1, 2)), label="Acaso")
    a.set(xlabel="Taxa de falsos positivos (1 − especificidade)", ylabel="Recall (sensibilidade)",
          xlim=(0, 1), ylim=(0, 1.01))
    b.set(xlabel="Recall (sensibilidade)", ylabel="Precisão", xlim=(0, 1), ylim=(0, 1.01))
    a.set_title("(a) Curva ROC", loc="left")
    b.set_title("(b) Curva Precisão–Recall", loc="left")
    for ax in (a, b):
        _eixos_leves(ax)
        ax.set_aspect("equal")
    a.legend(loc="lower right", frameon=False, fontsize=6.5)
    fig.tight_layout(w_pad=1.5)
    _salvar(fig, destino / "figuras" / "fig2_curvas.pdf")


def figura_erros(confusao: pd.DataFrame, imp: pd.DataFrame, melhor: str, destino: Path):
    c = confusao.set_index("modelo").loc[melhor]
    m = np.array([[c["vn"], c["fp"]], [c["fn"], c["vp"]]])
    pct = m / m.sum(axis=1, keepdims=True) * 100
    fig, (a, b) = plt.subplots(1, 2, figsize=(LARGURA * 2.05, 2.1), gridspec_kw={"width_ratios": [1, 1.6]})
    azul = LinearSegmentedColormap.from_list("azul", ["#cde2fb", "#184f95"])
    a.imshow(pct, cmap=azul, vmin=0, vmax=100)
    for i in range(2):
        for j in range(2):
            a.text(j, i, f"{inteiro(m[i, j])}\n({num(pct[i, j], 1)}%)", ha="center", va="center",
                   fontsize=7, color="white" if pct[i, j] > 55 else TINTA)
    a.set_xticks([0, 1], ["Normal", "Anormal"])
    a.set_yticks([0, 1], ["Normal", "Anormal"])
    a.set(xlabel="Classe prevista", ylabel="Classe real")
    a.set_title(f"(a) Matriz de confusão – {ROTULOS[melhor]}", loc="left")
    a.tick_params(length=0)
    a.grid(False)
    for s in a.spines.values():
        s.set_visible(False)

    top = imp.query("modelo == @melhor").head(10).iloc[::-1]
    b.barh([NOMES.get(v, v) for v in top["atributo"]], top["queda_auc_media"], xerr=top["queda_auc_dp"],
           color=COR_NORMAL, height=0.6, error_kw={"elinewidth": 0.7, "capsize": 1.5, "ecolor": TINTA_2})
    b.set_xlabel("Queda média da AUC-ROC ao permutar o atributo")
    b.set_title("(b) Importância por permutação (10 maiores)", loc="left")
    _eixos_leves(b)
    fig.tight_layout(w_pad=1.5)
    _salvar(fig, destino / "figuras" / "fig3_erros_importancia.pdf")


# ---------------------------------------------------------------- tabelas
def _linha(*celulas) -> str:
    return " & ".join(celulas) + r" \\"


def tabela_dados(destino: Path):
    X, y, _ = carregar_xy("principal")
    linhas = [
        _linha("Instâncias (bruto $\\rightarrow$ limpo)", "12.873 $\\rightarrow$ " + inteiro(len(y))),
        _linha("Atributos de entrada (antes da codificação)", inteiro(X.shape[1])),
        _linha("Classe Normal / Anormal", f"{num((1 - y.mean()) * 100, 1)}\\% / {num(y.mean() * 100, 1)}\\%"),
    ]
    for col, rot in [("IDADE", "Idade"), ("IMC", "IMC"), ("PA SISTOLICA", "Pressão arterial (PAS/PAD)"),
                     ("FC", "Frequência cardíaca"), ("MOTIVO2", "Motivo 2")]:
        linhas.append(_linha(f"Ausentes: {rot}", f"{num(X[col].isna().mean() * 100, 1)}\\%"))
    linhas.append(_linha("Ausentes: PPA", f"{num(X['ppa_ausente'].mean() * 100, 1)}\\%"))
    linhas.append(_linha("Ausentes: HDA (histórico)", f"{num(X['hda_ausente'].mean() * 100, 1)}\\%"))
    tex = "\n".join([r"\begin{tabular}{@{}lr@{}}", r"\toprule", _linha("Característica", "Valor"),
                     r"\midrule", *linhas, r"\bottomrule", r"\end{tabular}"])
    (destino / "tabelas" / "tab_dados.tex").write_text(tex + "\n", encoding="utf-8")


def tabela_modelos(resumo: pd.DataFrame, destino: Path):
    r = resumo.query("experimento == 'principal'").set_index("modelo").loc[list(ROTULOS)]
    # o classificador trivial não concorre ao destaque (especificidade 1 por construção)
    melhores = {m: r.drop(index="dummy")[f"{m}_media"].max() for m, _ in METRICAS_TAB}
    linhas = []
    for nome, row in r.iterrows():
        cel = []
        for m, _ in METRICAS_TAB:
            txt = f"{num(row[f'{m}_media'])} ({num(row[f'{m}_dp'])})"
            cel.append(f"\\textbf{{{txt}}}" if np.isclose(row[f"{m}_media"], melhores[m]) else txt)
        linhas.append(_linha(ROTULOS[nome], *cel))
    tex = "\n".join([r"\begin{tabular}{@{}l" + "c" * len(METRICAS_TAB) + r"@{}}", r"\toprule",
                     _linha("Modelo", *[t for _, t in METRICAS_TAB]), r"\midrule", *linhas,
                     r"\bottomrule", r"\end{tabular}"])
    (destino / "tabelas" / "tab_modelos.tex").write_text(tex + "\n", encoding="utf-8")


def tabela_ablacao(resumo: pd.DataFrame, melhor: str, destino: Path):
    def valores(**filtro):
        q = resumo
        for k, v in filtro.items():
            q = q[q[k] == v]
        q = q.set_index("modelo")
        return [num(q.loc[n, f"{m}_media"]) for n in ("logreg", melhor) for m in ("auc_roc", "recall", "f1")]

    blocos = [
        ("Atributos", [("Com Sopro (vazamento)", dict(experimento="cenarios", cenario="com_sopro")),
                       ("Sem Sopro (principal)", dict(experimento="principal")),
                       ("Sem Sopro e Motivos", dict(experimento="cenarios", cenario="restrito"))]),
        ("Desbalanceamento", [(ESTRATEGIA_TXT[e], dict(experimento="desbalanceamento", estrategia=e))
                              for e in ESTRATEGIA_TXT]),
        ("Validação", [("Agrupada por paciente", dict(experimento="agrupado"))]),
    ]
    linhas = []
    for titulo, itens in blocos:
        linhas += [r"\midrule", rf"\multicolumn{{7}}{{@{{}}l}}{{\textit{{{titulo}}}}} \\"]
        linhas += [_linha(rot, *valores(**f)) for rot, f in itens]
    tex = "\n".join([
        r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
        rf" & \multicolumn{{3}}{{c}}{{Regressão Logística}} & \multicolumn{{3}}{{c}}{{{ROTULOS[melhor]}}} \\",
        r"\cmidrule(lr){2-4}\cmidrule(l){5-7}",
        _linha("Configuração", "AUC", "Rec.", "F1", "AUC", "Rec.", "F1"), *linhas,
        r"\bottomrule", r"\end{tabular}"])
    (destino / "tabelas" / "tab_ablacao.tex").write_text(tex + "\n", encoding="utf-8")


# ---------------------------------------------------------------- números
def numeros(origem: Path, resumo: pd.DataFrame, melhor: str, destino: Path):
    X, y, _ = carregar_xy("principal")
    t5 = json.loads((origem / "teste_5x2cv.json").read_text(encoding="utf-8"))
    params = json.loads((origem / "melhores_params.json").read_text(encoding="utf-8"))
    conf = pd.read_csv(origem / "confusao.csv").set_index("modelo")
    lim = pd.read_csv(origem / "limiar.csv").set_index("limiar")
    imp = pd.read_csv(origem / "importancia_resumo.csv").query("modelo == @melhor")

    def media(metrica, **filtro):
        q = resumo
        for k, v in filtro.items():
            q = q[q[k] == v]
        return q[f"{metrica}_media"].iloc[0]

    def dp(metrica, **filtro):
        q = resumo
        for k, v in filtro.items():
            q = q[q[k] == v]
        return q[f"{metrica}_dp"].iloc[0]

    m = {"nInstancias": inteiro(len(y)), "nAtributos": inteiro(X.shape[1]),
         "pctAnormal": num(y.mean() * 100, 1), "pctNormal": num((1 - y.mean()) * 100, 1),
         "melhorNome": ROTULOS[melhor],
         "tCincoDois": num(t5["t"], 2), "pCincoDois": num(t5["p"], 3),
         "erroLogreg": num(t5["erro_a"] * 100, 1), "erroMelhor": num(t5["erro_b"] * 100, 1)}
    chave = {"logreg": "Logreg", "arvore": "Arvore", "rf": "Rf", "gb": "Gb", "dummy": "Dummy"}
    met = {"auc_roc": "auc", "auc_pr": "aucPr", "recall": "recall", "f1": "fUm",
           "acuracia_bal": "acBal", "acuracia": "acur", "especificidade": "espec", "precisao": "prec"}
    for nome in ROTULOS:
        for mt, prefixo in met.items():
            m[f"{prefixo}{chave[nome]}"] = num(media(mt, experimento="principal", modelo=nome))
        m[f"aucDp{chave[nome]}"] = num(dp("auc_roc", experimento="principal", modelo=nome))
    for mt, prefixo in met.items():
        m[f"{prefixo}Melhor"] = m[f"{prefixo}{chave[melhor]}"]
    m["aucDpMelhor"] = m[f"aucDp{chave[melhor]}"]
    for nome, sufixo in (("logreg", "Logreg"), (melhor, "Melhor")):
        for cen, rot in (("com_sopro", "ComSopro"), ("restrito", "Restrito")):
            for mt, prefixo in (("auc_roc", "auc"), ("recall", "recall")):
                m[f"{prefixo}{rot}{sufixo}"] = num(media(mt, experimento="cenarios", cenario=cen, modelo=nome))
        for est, rot in (("class_weight", "Pesos"), ("smote", "Smote"), ("subamostragem", "Sub")):
            for mt, prefixo in (("recall", "recall"), ("especificidade", "espec"), ("f1", "fUm"),
                                ("auc_roc", "auc")):
                m[f"{prefixo}{rot}{sufixo}"] = num(media(mt, experimento="desbalanceamento",
                                                         estrategia=est, modelo=nome))
        m[f"aucAgrupado{sufixo}"] = num(media("auc_roc", experimento="agrupado", modelo=nome))
        m[f"recallAgrupado{sufixo}"] = num(media("recall", experimento="agrupado", modelo=nome))
        c = conf.loc[nome]
        for k in ("vp", "fn", "fp", "vn"):
            m[f"{k}{sufixo}"] = inteiro(c[k])
    for t, rot in ((0.5, "Cinquenta"), (0.3, "Trinta"), (0.4, "Quarenta")):
        linha = lim.loc[t]
        m[f"fnLimiar{rot}"] = inteiro(linha["fn"])
        m[f"fpLimiar{rot}"] = inteiro(linha["fp"])
        m[f"recallLimiar{rot}"] = num(linha["recall"])
        m[f"precLimiar{rot}"] = num(linha["precisao"])
        m[f"especLimiar{rot}"] = num(linha["especificidade"])
    for i, rot in enumerate(("Um", "Dois", "Tres", "Quatro", "Cinco")):
        m[f"imp{rot}"] = NOMES.get(imp["atributo"].iloc[i], imp["atributo"].iloc[i])
        m[f"impValor{rot}"] = num(imp["queda_auc_media"].iloc[i])
    m["cLogreg"] = num(params["principal"]["logreg"]["moda"]["modelo__C"], 2).rstrip("0").rstrip(",")
    m["paramsMelhor"] = ", ".join(
        f"{k.removeprefix('modelo__').replace('_', chr(92) + '_')} = "
        f"{num(v, 2).rstrip('0').rstrip(',') if isinstance(v, float) else v}"
        for k, v in params["principal"][melhor]["moda"].items())
    linhas = [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()]
    (destino / "numeros.tex").write_text("% gerado por src/m06_figuras_tabelas.py - não editar\n"
                                         + "\n".join(linhas) + "\n", encoding="utf-8")


def executar(origem: Path = SAIDA_A2, destino: Path = ARTIGO) -> None:
    (destino / "figuras").mkdir(parents=True, exist_ok=True)
    (destino / "tabelas").mkdir(parents=True, exist_ok=True)
    melhor = json.loads((origem / "resumo.json").read_text(encoding="utf-8"))["melhor_complexo"]
    oof = pd.read_csv(origem / "oof.csv")
    resumo = pd.read_csv(origem / "resumo_metricas.csv")
    figura_leakage(destino)
    figura_curvas(oof, destino)
    figura_erros(pd.read_csv(origem / "confusao.csv"), pd.read_csv(origem / "importancia_resumo.csv"),
                 melhor, destino)
    tabela_dados(destino)
    tabela_modelos(resumo, destino)
    tabela_ablacao(resumo, melhor, destino)
    numeros(origem, resumo, melhor, destino)


if __name__ == "__main__":
    executar()
