"""Etapa 5 - Monta o relatório .docx (sem código) a partir das figuras, tabelas
e números calculados nas etapas anteriores, e confere o nº de páginas no Word.

Gera:
  Relatorio_A1_Parte1.docx  (+ .pdf, se o Microsoft Word estiver instalado)
"""
import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from config import ARQ_RELATORIO, FIGURAS, TABELAS, ler_resultados

FONTE = "Arial"
TAM_TEXTO = 10
TAM_TABELA = 8
LARGURA_UTIL_CM = 17.0
LIMITE_PAGINAS = 5


# ------------------------------------------------------------------ formatação pt-BR
def br(x, casas=1):
    if isinstance(x, (int,)) or (isinstance(x, float) and float(x).is_integer() and casas == 0):
        return f"{int(x):,}".replace(",", ".")
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pval(p):
    return "<0,001" if p < .001 else br(p, 3)


# ------------------------------------------------------------------ helpers docx
def configurar(doc):
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.left_margin = sec.right_margin = Cm(2.0)
    st = doc.styles["Normal"]
    st.font.name = FONTE
    st.font.size = Pt(TAM_TEXTO)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONTE)
    pf = st.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(0), Pt(4), 1.0
    for nome, tam in (("Heading 1", 11), ("Heading 2", 10)):
        h = doc.styles[nome]
        h.font.name, h.font.size, h.font.bold = FONTE, Pt(tam), True
        h.font.color.rgb = RGBColor(0, 0, 0)
        rfonts = h.element.rPr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts"); h.element.rPr.append(rfonts)
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(a), FONTE)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rfonts.get(qn(a)) is not None:
                del rfonts.attrib[qn(a)]
        h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(6), Pt(3)
        h.paragraph_format.keep_with_next = True


def paragrafo(doc, texto, negrito_inicio=None, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = alinhamento
    if negrito_inicio:
        p.add_run(negrito_inicio).bold = True
    p.add_run(texto)
    return p


def legenda(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(4), Pt(2)
    p.paragraph_format.keep_with_next = True
    tipo, _, resto = texto.partition(" – ")
    r = p.add_run(tipo + " – "); r.bold = True; r.font.size = Pt(9)
    r = p.add_run(resto); r.font.size = Pt(9)


def figura(doc, nome, texto_legenda, largura_cm=LARGURA_UTIL_CM):
    legenda(doc, texto_legenda)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    p.add_run().add_picture(str(FIGURAS / f"{nome}.png"), width=Cm(largura_cm))


def _sombrear(celula, cor="E4E3DF"):
    tcPr = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), cor)
    tcPr.append(shd)


def tabela(doc, df, texto_legenda, larguras_cm=None, tam=TAM_TABELA):
    legenda(doc, texto_legenda)
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, col in enumerate(df.columns):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(col)); r.bold = True; r.font.size = Pt(tam)
        _sombrear(c)
    for _, linha in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(linha):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run("" if pd.isna(v) else str(v))
            r.font.size = Pt(tam)
    for row in t.rows:
        # repete cabeçalho / evita quebra de linha da tabela entre páginas
        trPr = row._tr.get_or_add_trPr()
        el = OxmlElement("w:cantSplit"); trPr.append(el)
        for i, c in enumerate(row.cells):
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if larguras_cm:
                c.width = Cm(larguras_cm[i])
    hdr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); hdr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


# ------------------------------------------------------------------ tabelas do relatório
def tab1_descritiva():
    t = pd.read_csv(TABELAS / "tab_descritiva_antes_depois.csv")
    t = t.sort_values(["Variável", "Momento"], key=lambda s: s.map(
        {v: i for i, v in enumerate(["IDADE", "Peso", "Altura", "IMC", "PA SISTOLICA",
                                     "PA DIASTOLICA", "FC", "Bruto", "Limpo"])}))
    out = pd.DataFrame({
        "Variável": t["Variável"].where(t["Momento"] == "Bruto", ""),
        "Dado": t["Momento"],
        "n": t["n"].map(lambda v: br(int(v), 0)),
        "% aus.": t["% ausente"].map(br),
    })
    for c in ("Média", "DP", "Mín", "Q1", "Mediana", "Q3", "Máx", "Assimetria"):
        out[c] = t[c].map(lambda v: br(v, 1) if abs(v) < 1000 else br(v, 0))
    return out.rename(columns={"Assimetria": "Assim."})


def tab2_categoricas():
    b = pd.read_csv(TABELAS / "tab_categoricas_bruto.csv").set_index("Variável")
    l = pd.read_csv(TABELAS / "tab_categoricas_limpo.csv").set_index("Variável")
    return pd.DataFrame({
        "Variável": l.index,
        "Categorias (bruto → limpo)": [f"{b.loc[v,'Categorias']} → {l.loc[v,'Categorias']}" for v in l.index],
        "% ausente (bruto → limpo)": [f"{br(b.loc[v,'% ausente'])} → {br(l.loc[v,'% ausente'])}" for v in l.index],
        "Moda (limpo)": l["Moda"].values,
        "% da moda": [br(v) for v in l["% moda"].values],
    })


def tab3_qualidade():
    log = pd.read_csv(TABELAS / "tab_log_limpeza.csv")
    log = log[log["Registros afetados"] > 0]
    ordem = list(dict.fromkeys(log["Variável"]))
    linhas = []
    for v in ordem:
        g = log[log["Variável"] == v]
        linhas.append({
            "Variável": v,
            "Problema de qualidade": " • ".join(f"{p} (n={br(int(n),0)})" for p, n in zip(g["Problema"], g["Registros afetados"])),
            "Solução de limpeza": " • ".join(dict.fromkeys(g["Solução"])),
        })
    return pd.DataFrame(linhas)


def tab4_associacao():
    t = pd.read_csv(TABELAS / "tab_associacao_alvo.csv")
    forca = lambda e, tipo: ("forte" if abs(e) >= (.5 if tipo == "Categórica" else .5) else
                             "moderada" if abs(e) >= .3 else "fraca" if abs(e) >= .1 else "desprezível")
    med = lambda r: (f"{br(r['Mediana Normal'])} × {br(r['Mediana Anormal'])}" if r["Tipo"] == "Numérica" else "—")
    return pd.DataFrame({
        "Variável": t["Variável"],
        "Teste": t["Teste"],
        "Efeito": [f"{'V' if tp=='Categórica' else 'r'} = {br(e,2)}" for e, tp in zip(t["Efeito"], t["Tipo"])],
        "Magnitude": [forca(e, tp) for e, tp in zip(t["Efeito"], t["Tipo"])],
        "p-valor": t["p-valor"].map(pval),
        "Mediana Normal × Anormal": [med(r) for _, r in t.iterrows()],
    })


def tab5_transformacoes():
    return pd.read_csv(TABELAS / "tab_transformacoes.csv")


# ------------------------------------------------------------------ documento
def construir():
    R = ler_resultados()
    doc = Document()
    configurar(doc)
    lb = lambda k: R[k]
    n0, n1 = lb("bruto_shape")[0], lb("limpo_shape")[0]
    alvo = lb("limpo_alvo")
    cat = lb("categorias_alvo")
    ii = lb("idade_imc")
    tr = lb("transformado")
    assoc = pd.read_csv(TABELAS / "tab_associacao_alvo.csv").set_index("Variável")
    log = pd.read_csv(TABELAS / "tab_log_limpeza.csv")
    afet = lambda var, trecho: int(log[(log["Variável"] == var) & log["Problema"].str.contains(trecho, regex=False)]["Registros afetados"].sum())
    aus_b, aus_l = lb("bruto_ausentes_pct"), lb("limpo_ausentes_pct")
    desc = pd.read_csv(TABELAS / "tab_descritiva_antes_depois.csv").set_index(["Momento", "Variável"])
    d = lambda momento, var, est: desc.loc[(momento, var), est]

    # título
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("A1 – Parte 1: Pré-processamento de dados (limpeza e transformação)"); r.bold = True; r.font.size = Pt(12)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Conjunto UCMF – pacientes de cardiologia pediátrica (0 a 19 anos)").italic = True

    # 1. introdução
    doc.add_heading("1. Conjunto de dados e metodologia", level=1)
    paragrafo(doc,
        f"O arquivo bruto possui {br(n0,0)} registros e {lb('bruto_shape')[1]} variáveis: 7 numéricas "
        "(IDADE, Peso, Altura, IMC, PA sistólica, PA diastólica e FC), 2 datas (Atendimento e DN), "
        "11 categóricas e o identificador ID. A variável-alvo é NORMAL X ANORMAL (ausência/presença de "
        "patologia cardíaca); as demais são tratadas como variáveis independentes. O processamento foi "
        "feito em Python (pandas, SciPy e Matplotlib) em cinco etapas reprodutíveis: perfil do dado bruto, "
        "limpeza, análises comparativas e bivariadas, transformação e geração deste relatório. Para julgar a "
        "plausibilidade dos valores foram adotadas faixas fisiológicas amplas para 0–19 anos: IDADE 0–19 anos; "
        "Peso 1–150 kg; Altura 40–200 cm; IMC 10–40 kg/m² (curvas OMS 0–5 e 5–19 anos); FC 40–220 bpm "
        "(Fleming et al., 2011); PAS 60–200 mmHg e PAD 30–130 mmHg (Flynn et al., 2017). Valores fora dessas "
        "faixas são tratados como erro de registro, e não como casos clínicos extremos. Tabelas e figuras foram "
        "elaboradas pelo autor a partir do arquivo UCMF_raw.csv.")

    # 2. univariada
    doc.add_heading("2. Análise univariada", level=1)
    paragrafo(doc,
        "A Tabela 1 resume as variáveis numéricas antes e depois da limpeza, e a Figura 1 mostra sua distribuição "
        "no dado bruto, com a faixa plausível sombreada em verde. No dado bruto, IDADE vai de "
        f"{br(d('Bruto','IDADE','Mín'))} a {br(d('Bruto','IDADE','Máx'))} anos, IMC chega a {br(d('Bruto','IMC','Máx'),0)} kg/m², "
        f"PAS a {br(d('Bruto','PA SISTOLICA','Máx'),0)} mmHg e FC a {br(d('Bruto','FC','Máx'),0)} bpm, e Peso e Altura "
        f"têm muitos zeros ({br(afet('Peso','Zero'),0)} e {br(afet('Altura','Zero'),0)} registros após remover duplicatas), "
        "o que distorce média, desvio-padrão e assimetria. Depois da limpeza as distribuições ficam plausíveis: "
        f"a mediana de IDADE é {br(d('Limpo','IDADE','Mediana'))} anos (população majoritariamente pré-escolar), a mediana "
        f"do IMC é {br(d('Limpo','IMC','Mediana'))} kg/m² e a FC mediana é de {br(d('Limpo','FC','Mediana'),0)} bpm, "
        "compatível com a faixa etária. As variáveis ainda têm assimetria positiva moderada (cauda de crianças "
        "maiores/obesas), o que motiva a transformação logarítmica da Seção 6. A PA só foi medida em "
        f"{br(100-aus_l['PA SISTOLICA'],0)}% dos atendimentos.")
    tabela(doc, tab1_descritiva(), "Tabela 1 – Estatísticas descritivas das variáveis numéricas antes (bruto) e depois (limpo) da limpeza",
           [2.3, 1.1, 1.2, 1.1, 1.3, 1.3, 1.2, 1.1, 1.3, 1.1, 1.3, 1.2])
    figura(doc, "fig1_numericas_bruto",
           "Figura 1 – Boxplots das variáveis numéricas e do ano das datas no dado bruto (faixa verde = intervalo plausível)")
    paragrafo(doc,
        "As variáveis categóricas (Figura 2 e Tabela 2) mostram grafias diferentes para a mesma categoria "
        "(SEXO com 6 valores para 2 categorias; SOPRO com 'Sistólico'/'sistólico'; o próprio alvo com 'anormal' e "
        f"'Normais'), uma categoria 'Indeterminado' que na prática é ausência de informação e {lb('convenio_grafias')['bruto']} "
        "grafias de convênio. Todas são fortemente desbalanceadas: PULSOS e B2 têm mais de 94% na categoria 'Normal', e "
        f"HDA2 está {br(aus_b['HDA2'])}% vazia. No dado limpo, o alvo tem {br(alvo['Normal'],0)} registros Normais "
        f"({br(100*alvo['Normal']/n1)}%) e {br(alvo['Anormal'],0)} Anormais ({br(100*alvo['Anormal']/n1)}%), um "
        "desbalanceamento leve.")
    figura(doc, "fig2_categoricas_bruto",
           "Figura 2 – Frequência das categorias no dado bruto (cinza-claro = ausente/agrupado) e % de ausentes por variável",
           largura_cm=16.0)
    tabela(doc, tab2_categoricas(), "Tabela 2 – Resumo das variáveis categóricas antes e depois da limpeza",
           [3.2, 3.3, 3.3, 4.4, 2.0])

    # 3. qualidade e limpeza
    doc.add_heading("3. Problemas de qualidade e soluções de limpeza", level=1)
    paragrafo(doc,
        "A Tabela 3 relaciona, para cada variável, os problemas encontrados, a solução adotada e o número de registros "
        "afetados. Três decisões merecem destaque. (i) A IDADE registrada tem um erro sistemático: em média fica "
        f"{br((lb('idade_fator_erro')-1)*100)}% acima da diferença entre as datas, o que equivale a anos de ~{br(lb('idade_dias_por_ano_implicito'),0)} dias. "
        "Por isso ela foi recalculada como (Atendimento − DN)/365,25, depois de converter datas gravadas como número serial "
        "do Excel e descartar datas impossíveis. (ii) O IMC foi recalculado como Peso/Altura², já que o valor original era "
        "arredondado e continha valores absurdos. (iii) Os registros sem rótulo foram removidos, porque imputar o alvo "
        "introduziria viés. A PPA não foi recalculada, pois as tabelas clínicas de percentis exigem o percentil de estatura; "
        "as classes inválidas ('#VALUE!', que coincide com IDADE ausente, e 'Não Calculado') viraram ausentes. Na etapa de "
        "limpeza nenhum ausente foi imputado, para que as análises reflitam apenas valores observados. "
        f"Resultado: {br(n0,0)} → {br(n1,0)} registros.")
    tabela(doc, tab3_qualidade(), "Tabela 3 – Problemas de qualidade por variável e soluções de limpeza (n = registros afetados)",
           [2.6, 8.4, 6.0], tam=7.5)

    # 4. comparação de duas variáveis
    doc.add_heading("4. Comparação de duas variáveis após a limpeza: IDADE × IMC", level=1)
    figura(doc, "fig3_idade_imc",
           "Figura 3 – IDADE × IMC: (a) dado bruto; (b) dado limpo; (c) mediana e intervalo interquartil (IIQ) do IMC por faixa etária")
    im = ii["imc_mediano_por_idade"]
    paragrafo(doc,
        "IDADE e IMC foram escolhidas por serem as variáveis citadas no dicionário de dados como dependentes de faixas de "
        f"referência e por terem os erros mais visíveis. No dado bruto (Fig. 3a, n = {br(ii['n_bruto'],0)} pares), "
        f"{br(ii['fora_bruto_pct'])}% dos pontos estão fora do retângulo plausível: há um grupo de idades negativas "
        "(cerca de −100 anos, datas lidas no século errado), IMCs iguais a zero e valores acima de 100 kg/m², "
        "que obrigam a usar escala logarítmica. Depois da limpeza (Fig. 3b, "
        f"n = {br(ii['n_limpo'],0)}) todos os pontos estão na faixa esperada e a nuvem mostra o padrão biológico conhecido: "
        f"o IMC sobe no primeiro ano (mediana {br(im['1'])} kg/m²), cai até {br(min(im['3'], im['4'], im['5']))} kg/m² "
        f"entre 3 e 5 anos e volta a subir até {br(im['18'])} kg/m² aos 18 anos. Esse é o 'rebote de adiposidade' "
        "descrito nas curvas da OMS. Na Fig. 3c a curva mediana limpa é mais suave que a bruta (que tinha degraus por causa "
        f"do IMC arredondado), e a correlação de Spearman praticamente não muda (ρ = {br(ii['rho_bruto'],2)} → "
        f"{br(ii['rho_limpo'],2)}). Isso mostra que a limpeza removeu ruído sem distorcer a relação entre as variáveis. "
        "A heterocedasticidade (maior dispersão do IMC nos mais velhos) é real e reforça o uso de log no IMC.")

    # 5. bivariada
    doc.add_heading("5. Análise bivariada: variáveis independentes × alvo", level=1)
    paragrafo(doc,
        "Para as numéricas foi usado o teste de Mann-Whitney (as distribuições não são normais), com tamanho de efeito "
        "r rank-bisserial (r > 0 indica valores maiores no grupo Anormal). Para as categóricas, o teste qui-quadrado com "
        "V de Cramér. Com n > 5.000, até efeitos triviais dão p < 0,05, então a interpretação se baseia na magnitude do "
        "efeito (Tabela 4).")
    figura(doc, "fig4_numericas_alvo",
           "Figura 4 – Distribuição das variáveis numéricas por classe do alvo (sem outliers) e balanço das classes")
    s = lambda v: assoc.loc[v, "Efeito"]
    paragrafo(doc,
        f"Pacientes com cardiopatia são mais novos (mediana de {br(assoc.loc['IDADE','Mediana Anormal'])} × "
        f"{br(assoc.loc['IDADE','Mediana Normal'])} anos; r = {br(s('IDADE'),2)}) e, em consequência, mais leves e "
        f"mais baixos (r = {br(s('Peso'),2)} e {br(s('Altura'),2)}), além de terem IMC menor (r = {br(s('IMC'),2)}), "
        "o que é compatível com o déficit de crescimento das cardiopatias congênitas. A FC é maior no grupo Anormal "
        f"({br(assoc.loc['FC','Mediana Anormal'],0)} × {br(assoc.loc['FC','Mediana Normal'],0)} bpm; r = +{br(s('FC'),2)}), "
        "em parte porque esse grupo é mais jovem (FC e IDADE têm ρ = −0,68). As PAs quase não diferem entre os grupos "
        f"(|r| < 0,05), mas o fato de a PA ter sido medida importa: {br(cat['PA medida']['Não'][0])}% dos pacientes sem "
        f"PA registrada são Anormais, contra {br(cat['PA medida']['Sim'][0])}% dos que tiveram PA medida.")
    figura(doc, "fig5_categoricas_alvo",
           "Figura 5 – Percentual de pacientes Anormais por categoria (linha tracejada = taxa geral; categorias com n < 30 agrupadas)")
    paragrafo(doc,
        f"Entre as categóricas, SOPRO tem associação muito forte (V = {br(s('SOPRO'),2)}): "
        f"{br(cat['SOPRO']['Sistólico'][0])}% dos pacientes com sopro sistólico são Anormais, contra "
        f"{br(cat['SOPRO']['Ausente'][0])}% sem sopro. Também se destacam MOTIVO2 (V = {br(s('MOTIVO2'),2)}; "
        f"'Sopro' {br(cat['MOTIVO2']['Sopro'][0])}% e 'Cardiopatia congênita' {br(cat['MOTIVO2']['Cardiopatia congênita'][0])}% × "
        f"'Cirurgia' {br(cat['MOTIVO2']['Cirurgia'][0])}%), MOTIVO1 (V = {br(s('MOTIVO1'),2)}) e B2 (V = {br(s('B2'),2)}), "
        "já que qualquer B2 diferente de 'Normal' tem mais de 85% de Anormais. PULSOS alterados também indicam "
        "cardiopatia, mas são raros (V = 0,10). Os sintomas de HDA 1, o convênio e a PPA têm associação fraca, e SEXO "
        f"não se associa ao alvo (p = {pval(assoc.loc['SEXO','p-valor'])}). "
        "Alerta para a modelagem: SOPRO, B2 e MOTIVO1 = 'Cardiopatia já estabelecida' são achados do mesmo exame que "
        "define o diagnóstico ou refletem um diagnóstico prévio. Por isso podem causar vazamento de informação "
        "(data leakage) se o objetivo for triagem antes do exame.")
    tabela(doc, tab4_associacao(), "Tabela 4 – Associação de cada variável independente com o alvo, em ordem decrescente de efeito",
           [3.0, 2.4, 2.1, 2.1, 1.6, 3.6])

    # 6. transformações
    doc.add_heading("6. Transformações e justificativas", level=1)
    paragrafo(doc,
        "A Tabela 5 lista as transformações aplicadas ao conjunto limpo para gerar a base de modelagem. O resultado tem "
        f"{br(tr['shape'][0],0)} registros e {tr['shape'][1]} colunas numéricas (incluindo o alvo binário), sem valores "
        "ausentes. A ordem importa: o log é aplicado antes da imputação, para que a assimetria seja medida apenas nos "
        "valores observados, e a padronização vem por último. Na Parte 2, os parâmetros de imputação e padronização "
        "(medianas, médias e desvios) devem ser reajustados apenas no conjunto de treino e depois aplicados ao teste, "
        "para evitar vazamento de informação.")
    tabela(doc, tab5_transformacoes(), "Tabela 5 – Transformações realizadas no conjunto de dados e justificativas",
           [3.2, 4.6, 9.2], tam=7.5)

    # referências
    doc.add_heading("Referências", level=2)
    for ref in (
        "FLEMING, S. et al. Normal ranges of heart rate and respiratory rate in children from birth to 18 years of age: a systematic review of observational studies. The Lancet, v. 377, n. 9770, p. 1011-1018, 2011.",
        "FLYNN, J. T. et al. Clinical Practice Guideline for Screening and Management of High Blood Pressure in Children and Adolescents. Pediatrics, v. 140, n. 3, e20171904, 2017.",
        "WORLD HEALTH ORGANIZATION. WHO Child Growth Standards (0–5 anos) e Growth Reference Data for 5–19 years. Genebra: WHO, 2006/2007.",
    ):
        p = paragrafo(doc, ref, alinhamento=WD_ALIGN_PARAGRAPH.LEFT)
        for r in p.runs:
            r.font.size = Pt(8)
        p.paragraph_format.space_after = Pt(1)

    doc.save(ARQ_RELATORIO)
    return ARQ_RELATORIO


def contar_paginas_word(caminho):
    """Abre no Word (se disponível), conta páginas e exporta PDF."""
    try:
        import win32com.client
    except ImportError:
        return None
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        d = word.Documents.Open(str(caminho), ReadOnly=True)
        d.Repaginate()
        paginas = d.ComputeStatistics(2)  # wdStatisticPages
        d.ExportAsFixedFormat(str(caminho.with_suffix(".pdf")), 17)  # wdExportFormatPDF
        d.Close(False)
        return paginas
    finally:
        word.Quit()


def executar():
    caminho = construir()
    paginas = contar_paginas_word(caminho)
    if paginas is None:
        print(f"[5] relatório salvo em {caminho} (Word indisponível: confira o nº de páginas manualmente)")
    else:
        status = "OK" if paginas <= LIMITE_PAGINAS else f"ATENÇÃO: excede {LIMITE_PAGINAS}"
        print(f"[5] relatório salvo em {caminho} — {paginas} páginas ({status})")
    return paginas


if __name__ == "__main__":
    executar()
