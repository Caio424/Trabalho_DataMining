# A1 Parte 1 — Pré-processamento do UCMF (design)

## Objetivo
Relatório `.docx` (máx. 5 folhas, Arial 10, sem código/screenshots) sobre limpeza e
transformação de `UCMF_raw.csv`, gerado por um pipeline Python modular. O pipeline
também exporta `UCMF_clean.csv` e `UCMF_transformed.csv` para a Parte 2 (modelagem).

Variável-alvo: `NORMAL X ANORMAL` (Anormal = 1). "Variáveis dependentes" no enunciado
é interpretado como "independentes".

## Estrutura
```
main.py                 roda as etapas em ordem
src/config.py           caminhos, faixas clínicas, mapeamentos, estilo dos gráficos
src/p01_perfil.py       carga + univariada (bruto) → figuras 1-2, tabelas 1-2
src/p02_limpeza.py      regras de limpeza + log → UCMF_clean.csv, tabela 3
src/p03_bivariada.py    IDADE×IMC antes/depois (fig 3) + análise vs alvo (fig 4-5, tabela 4)
src/p04_transformacao.py imputação/codificação/escala → UCMF_transformed.csv, tabela 5
src/p05_relatorio.py    monta saida/Relatorio_A1_Parte1.docx e verifica nº de páginas
saida/figuras, saida/tabelas, saida/*.csv
```

## Seção 1 — Limpeza (aprovada)
| Variável | Problema | Solução |
|---|---|---|
| linhas | 987 duplicatas ignorando ID | remover duplicatas exatas |
| alvo | grafias; 1.168 ausentes | padronizar Normal/Anormal; remover linhas sem alvo |
| Atendimento, DN | serial Excel; século errado (2066) | converter serial; datas futuras −100 anos |
| IDADE | superestimada ~3,7%; negativas; >19 | recalcular (Atendimento−DN)/365,25; fora de [0,19] → NaN |
| Peso, Altura | zeros = não medido; extremos | 0 → NaN; limites pediátricos (Peso 1–150 kg, Altura 40–200 cm) |
| IMC | 848, zeros | recalcular Peso/Altura²; fora de [10,40] → NaN |
| PAS, PAD | 990 etc. | fora de [60,200] / [30,130] → NaN; PAS ≤ PAD → NaN |
| PPA | #VALUE!, Não Calculado | → NaN; agrupar em Normal / Pré-HAS / HAS-1 / HAS-2 |
| FC | texto, faixas, 8 e 9288 | faixa → ponto médio; fora de [40,220] → NaN |
| SEXO, SOPRO, PULSOS, B2 | caixa/acentos | mapear canônico; Indeterminado → NaN |
| Convenio | 375 grafias | caixa/pontuação; <1% → "OUTROS"; NaN → "NAO INFORMADO" |
| HDA 1/HDA2 | HDA2 97% ausente | indicadores binários de sintoma (união das duas) |
| MOTIVO1/2 | prefixo numérico | padronizar texto (remove código) |

Sem imputação nesta etapa.

## Seção 2 — Análises (aprovada)
- Univariada: tabela descritiva numérica antes/depois; resumo categóricas; grade de
  histogramas/boxplots (bruto); barras das categóricas (bruto).
- Comparação pós-limpeza: IDADE × IMC (dispersão antes/depois com faixas de referência).
- Bivariada vs alvo: boxplots + Mann-Whitney + r rank-biserial (numéricas);
  % Anormal por categoria + qui-quadrado + V de Cramér (categóricas); ranking.
- Alerta de vazamento para MOTIVO1 "Cardiopatia já estabelecida"/SOPRO.

## Seção 3 — Transformações
1. Remover identificadores/redundâncias: ID, Atendimento, DN (informação já em IDADE),
   Peso e Altura (colineares com IDADE, r > 0,9 — verificado no pipeline; IMC mantém a
   informação de composição corporal).
2. HDA 1 ∪ HDA2 → 7 indicadores binários de sintoma + hda_ausente.
3. Indicadores de ausência (pa_ausente, imc_ausente, ppa_ausente) para variáveis com >20% NaN.
4. PPA ordinal (0–3), ausente → 0 + indicador.
5. log(1+x) nas contínuas com |assimetria| > 1 medida nos valores observados (IMC, PAS, FC),
   aplicado ANTES da imputação.
6. Imputação das contínuas pela mediana.
   (Na Parte 2 o imputador/padronizador deve ser ajustado só no treino — registrado no relatório.)
7. Padronização z-score das contínuas.
8. One-hot das nominais (inclui SEXO) com "Nao informado"; categorias n<30 → "Outro".
9. Alvo → ALVO_ANORMAL (1 = Anormal).
Resultado: 11.470 × 72, sem ausentes.

## Notas de formatação
Corpo em Arial 10; tabelas em Arial 7,5–8 e legendas em 9 para caber em 5 páginas.

## Critérios de sucesso
- Todas as 21 variáveis cobertas na univariada e na tabela de qualidade.
- Relatório ≤ 5 páginas (verificado via Word COM), Arial 10, sem código.
- Pipeline reprodutível com `python main.py`.
