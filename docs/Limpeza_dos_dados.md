# Limpeza dos dados do UCMF — guia completo

Documento de estudo sobre **tudo** que foi feito na etapa de limpeza do conjunto `UCMF_raw.csv`
(A1 – Parte 1). Serve para você entender, explicar e defender cada decisão.

> **Como ler:** a Seção 1 dá a visão geral; a Seção 3 é a tabela-mestre (todas as regras em uma página);
> a Seção 4 explica cada regra em detalhe; a Seção 8 lista as **limitações e correções pendentes** —
> leia antes de apresentar o trabalho.

**Código correspondente:** [src/p02_limpeza.py](../src/p02_limpeza.py) (regras),
[src/config.py](../src/config.py) (faixas e mapeamentos), [src/p01_perfil.py](../src/p01_perfil.py) (perfil do dado bruto).

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Glossário rápido](#2-glossário-rápido)
3. [Tabela-mestre: problema → solução](#3-tabela-mestre-problema--solução)
4. [Passo a passo detalhado](#4-passo-a-passo-detalhado)
5. [Resultado: antes × depois](#5-resultado-antes--depois)
6. [Faixas de plausibilidade](#6-faixas-de-plausibilidade)
7. [Testes de sensibilidade](#7-testes-de-sensibilidade)
8. [Limitações, correções e pendências](#8-limitações-correções-e-pendências)
9. [O que a limpeza NÃO faz](#9-o-que-a-limpeza-não-faz)
10. [Perguntas prováveis e respostas](#10-perguntas-prováveis-e-respostas)
11. [Reprodutibilidade e mapa regra → código](#11-reprodutibilidade-e-mapa-regra--código)

---

## 1. Visão geral

### 1.1 O conjunto de dados

| Item | Valor |
|---|---|
| Arquivo | `UCMF_raw.csv` |
| Registros | 12.873 |
| Colunas | 21 (1 ID, 2 datas, 7 numéricas, 11 categóricas incluindo o alvo) |
| População | Crianças e jovens de 0 a 19 anos, com ou sem patologia cardíaca |
| Variável-alvo | `NORMAL X ANORMAL` (ausência/presença de patologia cardíaca) |

### 1.2 O que a limpeza entregou, em números

| Indicador | Bruto | Limpo |
|---|---|---|
| Linhas | 12.873 | **11.470** |
| Colunas | 21 | 21 |
| Alvo: Normal / Anormal | 6.744 / 4.959 (+1.168 vazios, +2 grafias erradas) | **6.576 / 4.894** (57,3% / 42,7%) |
| Regras de limpeza aplicadas | — | 34 (todas registradas em log) |
| Células ausentes | — | ≈ 21% do total (50.935 de 240.870) |

**Fluxo de linhas:**

| Etapa | Linhas |
|---|---|
| Arquivo bruto | 12.873 |
| − duplicatas (idênticas exceto pelo ID) | − 987 |
| = após remover duplicatas | 11.886 |
| − sem rótulo (alvo ausente) | − 416 |
| = **conjunto limpo** | **11.470** |

### 1.3 Fluxo da limpeza (ordem de execução)

```
UCMF_raw.csv
   │
   ├─ 1. Duplicatas ............. remove linhas idênticas (ignorando ID)
   ├─ 2. Alvo ................... padroniza grafias; remove linhas sem rótulo
   ├─ 3. Datas e IDADE .......... converte datas; recalcula IDADE; valida faixa 0–19
   ├─ 4. Peso, Altura, IMC ...... zeros → ausente; faixas; recalcula IMC
   ├─ 5. PAS, PAD ............... faixas; PAS ≤ PAD → ausente
   ├─ 6. PPA .................... erros → ausente; agrupa 9 → 4 níveis; checa coerência com PA
   ├─ 7. FC ..................... texto → número; faixa → ponto médio; valida faixa
   └─ 8. Categóricas ............ SEXO, SOPRO, PULSOS, Convenio, MOTIVO1/2, HDA
   │
   ▼
saida/UCMF_clean.csv   +   saida/tabelas/tab_log_limpeza.csv (o "diário" de cada regra)
```

### 1.4 Por que essa ordem?

| Regra de ordem | Motivo |
|---|---|
| Duplicatas **primeiro** | Para que todas as contagens seguintes não sejam infladas por registros repetidos |
| Alvo **cedo** | Linhas sem rótulo não servem para a modelagem; tirá-las antes evita gastar regras com elas |
| Datas **antes** de IDADE | A IDADE é recalculada a partir das datas, que precisam estar convertidas |
| Peso e Altura **antes** do IMC | O IMC é recalculado de Peso/Altura². Se Peso/Altura ainda tivessem lixo, o IMC herdaria o erro |
| PA **antes** da PPA | A PPA só faz sentido se existir PA válida que a sustente |

### 1.4 Os 5 princípios que guiaram tudo

| # | Princípio | Por quê |
|---|---|---|
| 1 | **Valor impossível vira ausente (NaN); a linha não é apagada** | Apagar a linha joga fora as outras ~20 colunas, que podem estar corretas |
| 2 | **Faixas de plausibilidade, não de normalidade** | Uma FC de 200 bpm num recém-nascido é rara mas possível; 9.288 bpm é erro. A faixa só barra o fisiologicamente impossível, para não apagar casos clínicos reais |
| 3 | **Se o dado é derivado, recalcule a partir da fonte** | IDADE vem das datas; IMC vem de Peso e Altura. Recalcular é mais confiável que "consertar" o valor original |
| 4 | **Nada é imputado na limpeza** | Assim, a análise do dado limpo reflete só o que foi realmente observado. A imputação fica para a etapa de transformação |
| 5 | **Cada regra é contada e registrada** | Transparência: dá para auditar quantos registros cada regra mexeu (vira a Tabela 3 do relatório) |

---

## 2. Glossário rápido

| Termo | Significado neste trabalho |
|---|---|
| **NaN / ausente** | Valor faltante. Pode ser original (célula vazia) ou criado pela limpeza (valor impossível apagado) |
| **Ausente disfarçado** | Valor que aparece como "preenchido" mas na verdade significa "não medido". Ex.: Peso = 0 |
| **Outlier** | Valor muito distante dos demais. **Atenção:** nem todo outlier é erro; só removi os *impossíveis* |
| **Plausibilidade** | O valor poderia existir no mundo real para esta população (0–19 anos)? |
| **Número serial do Excel** | Data guardada como contagem de dias desde 30/12/1899 (ex.: `38574` = 10/08/2005) |
| **Duplicata** | Linhas iguais em todas as colunas, exceto o ID |
| **Grafia inconsistente** | Mesma categoria escrita de formas diferentes ("M", "Masculino", "masculino") |
| **Imputação** | Preencher um ausente com um valor estimado (mediana, média etc.). **Não feita aqui** |
| **Assimetria (skew)** | Medida de quão "torta" é a distribuição. 0 = simétrica; valores grandes = cauda longa causada por extremos |
| **Mediana** | Valor central; não é afetada por extremos (por isso é preferida à média em dados sujos) |
| **DP** | Desvio-padrão (dispersão dos dados) |
| **IIQ** | Intervalo interquartil (Q3 − Q1) |
| **Alvo** | A variável que se quer prever: `NORMAL X ANORMAL` |
| **Data leakage** | "Vazamento": usar na modelagem uma informação que o modelo não teria na vida real ou que já entrega a resposta |

---

## 3. Tabela-mestre: problema → solução

Contagens do log (`tab_log_limpeza.csv`), calculadas **depois** de remover duplicatas e linhas sem rótulo
(por isso podem diferir das contagens no arquivo bruto).

| # | Variável | Problema de qualidade | Registros | Solução | Tipo de ação |
|---|---|---|---|---|---|
| 1 | (linhas) | Duplicatas exatas (exceto ID) | 987 | Remover | Remoção de linhas |
| 2 | Alvo | Grafias erradas ("anormal", "Normais") | 2 | Padronizar para Normal/Anormal | Padronização |
| 3 | Alvo | Rótulo ausente | 416 | Remover linhas | Remoção de linhas |
| 4 | Atendimento | Data como serial do Excel | 304 | Converter (origem 30/12/1899) | Conversão |
| 5 | Atendimento | Data posterior a 2010 (ex.: 2023, 2066) | 2 | Ausente | Anulação |
| 6 | DN | Data como serial do Excel | 121 | Converter | Conversão |
| 7 | DN | Texto livre/formato inválido ("5 anos", "??") | 116 | Ausente | Anulação |
| 8 | DN | Data posterior a 2010 | 10 | Ausente | Anulação |
| 9 | IDADE | Erro sistemático (~3,8% acima do real) | 7.759 | Recalcular de (Atendimento − DN) ÷ 365,25 | Recálculo |
| 10 | IDADE | Fora de [0; 19] (inclui 119 negativas) | 197 | Ausente | Anulação |
| 11 | Peso | Zero usado como "não medido" | 1.652 | Ausente | Anulação |
| 12 | Peso | Fora de [1; 150] kg | 4 | Ausente | Anulação |
| 13 | Altura | Zero usado como "não medido" | 3.455 | Ausente | Anulação |
| 14 | Altura | Fora de [40; 200] cm | 12 | Ausente | Anulação |
| 15 | IMC | Inconsistente com Peso/Altura² (ex.: 848) e arredondado | 120 | Recalcular = Peso ÷ Altura² | Recálculo |
| 16 | IMC | Fora de [10; 40] kg/m² | 49 | Ausente | Anulação |
| 17 | PAS | Fora de [60; 200] mmHg | 2 | Ausente | Anulação |
| 18 | PAD | Fora de [30; 130] mmHg | 2 | Ausente | Anulação |
| 19 | PAS/PAD | PAS ≤ PAD (impossível) | 1 | Par vira ausente | Anulação |
| 20 | PPA | "#VALUE!" e "Não Calculado" | 9.183 | Ausente | Anulação |
| 21 | PPA | 9 classes (PAS/PAD separadas) | 2.072 | Agrupar em 4 níveis ordinais | Agrupamento |
| 22 | PPA | Classe sem PA válida que a sustente | 1 | Ausente | Anulação |
| 23 | FC | Texto com faixas ("80-90", "156 a 168") | 16 | Ponto médio da faixa | Conversão |
| 24 | FC | Fora de [40; 220] bpm | 17 | Ausente | Anulação |
| 25 | SEXO | 5 grafias para 2 categorias | 873 | Padronizar para M/F | Padronização |
| 26 | SEXO | "Indeterminado" | 523 | Ausente | Anulação |
| 27 | SOPRO | Caixa/acento ("Sistólico"/"sistólico") | 735 | Padronizar | Padronização |
| 28 | PULSOS | Caixa/espaço ("Normais"/"NORMAIS") | 3 | Padronizar | Padronização |
| 29 | Convenio | 367 grafias; cauda longa | 1.721 | Caixa/pontuação padronizadas; categorias < 1% → "OUTROS" | Padronização + agrupamento |
| 30 | Convenio | Ausente | 3.158 | Categoria "NAO INFORMADO" | Categoria explícita |
| 31 | MOTIVO1 | Código numérico no texto ("5 - Parecer…") | 11.329 | Remover prefixo | Padronização |
| 32 | MOTIVO2 | Código numérico no texto ("5 - Cirurgia") | 8.158 | Remover prefixo | Padronização |
| 33 | HDA 1 | "Palpitacao" sem acento | — | Corrigir para "Palpitação" | Padronização |
| 34 | HDA2 | 96,5% ausente | 11.068 | Mantida (tratada na transformação) | Sem alteração |

> **Os 7 tipos de ação** usados: remoção de linhas, padronização, conversão, recálculo, anulação (valor → ausente),
> agrupamento e categoria explícita para ausentes.

---

## 4. Passo a passo detalhado

Cada subseção segue o mesmo molde: **O que vimos → Por que é problema → O que fizemos → Por que assim → Alternativas descartadas → Efeito**.

### 4.1 Duplicatas

| | |
|---|---|
| **O que vimos** | 987 linhas idênticas em todas as colunas, exceto o `ID` (nenhum ID repetido) |
| **Por que é problema** | Um paciente contado duas vezes pesa em dobro nas estatísticas. Na modelagem, a mesma pessoa pode cair no treino **e** no teste, inflando o desempenho |
| **O que fizemos** | Removemos as duplicatas, mantendo a primeira ocorrência |
| **Por que assim** | Comparamos tudo **menos o ID**, pois o ID era o único campo que diferia |
| **Alternativa descartada** | Manter tudo e confiar no ID — descartada porque o ID não identifica o paciente de fato (é só um número de linha) |
| **Efeito** | − 987 linhas |

**Detalhe importante:** 752 das 987 duplicatas eram de linhas **sem alvo** (1.168 sem alvo no bruto → 416 depois de remover
as duplicatas). Ou seja, a maioria era de registros quase vazios repetidos.

**Ressalva:** em linhas com muitas colunas vazias, duas pessoas diferentes poderiam ser "idênticas" por acaso. Considerei o risco pequeno.

---

### 4.2 Variável-alvo `NORMAL X ANORMAL`

| Valor bruto | Registros (bruto) | Tratamento |
|---|---|---|
| Normal | 6.744 | Mantido |
| Anormal | 4.959 | Mantido |
| anormal | 1 | → Anormal |
| Normais | 1 | → Normal |
| (vazio) | 1.168 | **Linha removida** |

| | |
|---|---|
| **Por que remover linhas sem rótulo** | O alvo é exatamente o que o modelo deve prever. Imputá-lo seria **inventar a resposta**, introduzindo viés |
| **Alternativa descartada** | Aprendizado semissupervisionado (usar linhas sem rótulo) — fora do escopo desta atividade |
| **Efeito** | − 416 linhas (após as duplicatas). Alvo final: 6.576 Normais (57,3%) e 4.894 Anormais (42,7%) — desbalanceamento **leve** |

---

### 4.3 Datas (`Atendimento` e `DN`) e `IDADE`

Esta é a parte mais técnica. Há **quatro** problemas encadeados.

#### 4.3.1 Datas em formatos misturados

| Formato encontrado | Exemplo | Tratamento |
|---|---|---|
| `dd/mm/aa` (normal) | `11/05/06` | Lido normalmente |
| `dd/mm/aaaa` | `11/05/2006` | Lido normalmente |
| **Número serial do Excel** (5 dígitos) | `38574` | Convertido: data = 30/12/1899 + N dias |
| Texto livre | `5 anos`, `3a`, `??`, `Ago/99` | **Vira ausente** |

- **Por que 30/12/1899?** É a "origem" usada pelo Excel (já compensa um bug histórico do Excel com o ano de 1900).
- **Por que o serial aparece?** Quando uma célula do Excel é formatada como número em vez de data, o valor "vaza" como contagem de dias.
- **Por que texto livre vira ausente e não é aproveitado?** "5 anos" daria uma idade, não uma data, e eram poucos casos (116 em DN). Converter seria um chute.
- **Efeito:** 304 seriais em Atendimento, 121 em DN, 116 textos em DN.

#### 4.3.2 Datas impossíveis (depois de 2010)

- Os atendimentos do conjunto vão de 2003 a 2010 (com poucos antes). Datas como **2023** e **2066** são erros de digitação do ano.
- Regra: qualquer data **posterior a 31/12/2010** → ausente (2 em Atendimento, 10 em DN).
- Detalhe técnico: o ano de 2 dígitos é lido assim: `00–68` → 2000–2068; `69–99` → 1969–1999. Por isso um `68` vira 2068 (futuro) e é barrado.

> ⚠️ **Divergência do plano:** na Seção 1 aprovada eu disse que datas futuras receberiam "−100 anos". Na implementação, elas viram
> **ausente**. O resultado final é equivalente (um DN de 2068 virar 1968 daria 42 anos, fora de 0–19, e acabaria ausente de qualquer forma),
> mas o texto aprovado e o código diferem.

#### 4.3.3 O erro sistemático da IDADE

| | |
|---|---|
| **O que vimos** | Comparando `IDADE` original com (Atendimento − DN) onde as duas existem, a IDADE é **em mediana 3,77% maior** (fator 1,0377) |
| **Interpretação** | 365,25 ÷ 1,0377 = **352 dias por ano**. Parece que a planilha original usou um divisor errado |
| **O que fizemos** | **Recalculamos**: IDADE = (Atendimento − DN) em dias ÷ 365,25 |
| **Por que 365,25** | É a duração média do ano contando anos bissextos |
| **Se faltar data mas existir IDADE** | Usamos a IDADE original ÷ 1,0377 (correção pelo fator). Foram 225 casos |
| **Por que recalcular em vez de só corrigir pelo fator** | As datas são a fonte primária; a IDADE é derivada. Recalcular elimina o erro na origem |
| **Efeito** | 7.759 valores alterados |

Exemplo ilustrativo: Atendimento 17/02/09, DN 11/03/94 → IDADE original 15,50 → recalculada **14,94**.

#### 4.3.4 Idades negativas e fora de 0–19

Foram 122 idades negativas no bruto, com **duas causas diferentes**:

| Causa | Quantas | Exemplo | Como identificamos |
|---|---|---|---|
| **Atendimento em branco** | 48 (valores de −100 a −113) | Atendimento vazio, DN `17/10/02`, IDADE −106,66 | Todos têm Atendimento vazio. A planilha provavelmente subtraiu "data zero" (1900) da DN |
| **Atendimento anterior ao nascimento** | 74 (valores de −50 a 0) | Atendimento `12/06/01`, DN `08/05/05`, IDADE −4,05 | Erro real de digitação do ano |

Além disso, **94 idades > 19 anos** (até 71,8), fora do escopo do estudo (0–19 anos, segundo o dicionário).

- **Regra:** depois do recálculo, IDADE fora de [0; 19] → **ausente** (197 valores, dos quais 119 negativas).
- **Por que 0 é aceito:** recém-nascido atendido no próprio dia tem idade 0,00 — é legítimo.

> ⚠️ **Correção necessária no relatório:** o texto da Seção 4 do `.docx` atribui as idades de ≈ −100 anos a "datas lidas no
> século errado". **Isso está errado** — a causa é Atendimento em branco (ver tabela acima). Ver Seção 8.

---

### 4.4 Peso, Altura e IMC

#### 4.4.1 Zeros = "não medido" (ausente disfarçado)

| Variável | Zeros no bruto | Zeros no conjunto limpo* | Proporção no bruto |
|---|---|---|---|
| Peso | 2.609 | 1.652 | 20,3% |
| Altura | 4.460 | 3.455 | 34,6% |

\* após remover duplicatas e linhas sem rótulo (os registros quase vazios tinham muitos zeros).

| | |
|---|---|
| **Por que é problema** | Peso = 0 kg e Altura = 0 cm são impossíveis. O zero estava sendo usado como "não medido". Isso destrói média, desvio-padrão e correlações |
| **O que fizemos** | Zero → ausente |
| **Evidência** | Em 1.908 registros o Peso era positivo mas a Altura era zero — claramente "altura não medida" |

> **Efeito colateral que parece piora mas não é:** a % de ausentes em Peso foi de 2,5% → 17,1% e em Altura de 0% → 30,2%.
> Isso **revelou** a ausência que já existia disfarçada. A ausência *efetiva* no bruto era ~22,7% (Peso) e ~34,6% (Altura).

#### 4.4.2 Faixas de Peso e Altura

| Variável | Faixa | Registros removidos | O que eram |
|---|---|---|---|
| Peso | [1; 150] kg | 4 | −40 kg; 0,3 kg (aos 9,5 anos); 0,5 kg (aos 11,5 anos); 157 kg (com 46 cm de altura) |
| Altura | [40; 200] cm | 12 | 10, 11, 12, 15, 16, 19, 31, 33, 36, 37, 38 e 39 cm |

Quase todos são erros evidentes (ex.: 10 cm de altura aos 9,5 anos). **Só ~2 podem ser reais**: um bebê de 1,2 kg com 36 cm aos 0,04 ano
(prematuro extremo) e outro de 1,7 kg com 38 cm sem idade registrada. Impacto: 16 valores em 11.470 linhas (**0,14%**).

#### 4.4.3 IMC recalculado

| | |
|---|---|
| **O que vimos** | O IMC original estava arredondado para inteiro (19,0; 14,0…) e continha absurdos (máximo **848**, 109 zeros) |
| **O que fizemos** | **Recalculamos** o IMC = Peso (kg) ÷ Altura (m)². Isso substitui todos os valores do IMC |
| **Por que** | IMC é derivado: se Peso e Altura estão corretos, o IMC calculado é o certo. E mantém casas decimais |
| **Ordem** | Feito **depois** de limpar Peso e Altura, para não herdar erro |
| **Efeito** | 120 valores mudaram materialmente (diferença > 1 kg/m², criados onde faltava, ou anulados porque Peso/Altura ficaram ausentes) |

Depois, aplicamos a faixa **[10; 40] kg/m²**, que removeu 49 valores:

| Lado do corte | Quantos | Observação |
|---|---|---|
| Acima de 40 | 9 | 8 são erros evidentes de Peso/Altura (ex.: 127 kg com 123 cm aos 6 anos). **Só 1 plausível**: 58 kg, 117 cm, 7,7 anos (IMC 42,4) |
| Abaixo de 10 | 40 | Maioria com Peso/Altura incoerentes; 7 estão entre 9,95 e 10 |

**Como o IMC bruto se comportava:** 17 valores acima de 40 (12 acima de 50, 6 acima de 100), todos com Peso/Altura impossíveis
(ex.: 21,7 kg com 16 cm → IMC 848).

---

### 4.5 Pressão arterial: `PA SISTOLICA` (PAS) e `PA DIASTOLICA` (PAD)

| Regra | Faixa | Removidos | Exemplos |
|---|---|---|---|
| PAS | [60; 200] mmHg | 2 | 990, 700 |
| PAD | [30; 130] mmHg | 2 | 6 |
| PAS ≤ PAD | — | 1 par | fisiologicamente impossível (a sistólica é sempre maior) |

**Por que faixas largas?** Em adolescentes com hipertensão estágio 2, PAS de 160–180 é possível. O objetivo é só barrar o impossível.

**Ausência alta (≈ 55–60%):** a PA só foi registrada em parte dos atendimentos. É provável (não testei) que esteja concentrada em
crianças maiores, pois a PA costuma ser medida de rotina a partir de certa idade. O que **verifiquei** é que a ausência é informativa:
**48,0%** dos pacientes sem PA são Anormais, contra **36,0%** dos com PA medida. Por isso, na transformação, criamos o indicador `pa_ausente`.

---

### 4.6 `PPA` (hipertensão arterial sistêmica)

A PPA é calculada a partir de PAS, PAD, sexo, idade e altura, usando tabelas clínicas.

| Valor bruto | Registros (bruto) | Significado | Tratamento |
|---|---|---|---|
| Normal | 1.790 | PA normal | Mantido → **Normal** |
| Pre-Hipertensão PAS / PAD | 48 / 73 | Pré-hipertensão | → **Pré-HAS** |
| HAS-1 PAS / PAD | 48 / 26 | Hipertensão estágio 1 | → **HAS-1** |
| HAS-2 PAS / PAD | 73 / 21 | Hipertensão estágio 2 | → **HAS-2** |
| `#VALUE!` | 1.496 | **Erro de fórmula do Excel** | → ausente |
| Não Calculado | 9.081 | Não calculado | → ausente |
| (vazio) | 217 | — | ausente |

Três decisões:

| Decisão | Motivo |
|---|---|
| **Erros viram ausente** | `#VALUE!` é erro de fórmula, não um nível de PA. A contagem (1.496) coincide exatamente com a de IDADE ausente (1.496), sugerindo que a fórmula depende da idade — **mas não conferi linha a linha** |
| **Agrupar 9 → 4 níveis ordinais** (Normal < Pré-HAS < HAS-1 < HAS-2) | Os sufixos "PAS"/"PAD" só indicam *qual componente* definiu a classe; clinicamente é o mesmo estágio. Agrupar reduz categorias raras e cria uma **escala ordinal** |
| **NÃO recalcular a PPA** | As tabelas oficiais (AAP 2017) exigem **percentil de estatura**, e a Altura tem 30% de ausentes. Eu também não tenho as tabelas oficiais embutidas. Recalcular exigiria inventar |

**Incoerência encontrada:** 2.495 pacientes **tinham PA medida** mas a PPA estava "Não Calculado" (e 352 estavam como `#VALUE!`). Esses valores
foram anulados (9.183 no total).

**Checagem de coerência:** uma classe (1 registro) sem PA válida que a sustente foi anulada.

**Resultado:** PPA tem 81,9% de ausentes no limpo. As classes válidas ficam: Normal 1.784, Pré-HAS 120, HAS-1 73, HAS-2 94.

---

### 4.7 Frequência cardíaca (`FC`)

| Problema | Exemplos | Registros | Tratamento |
|---|---|---|---|
| Coluna armazenada como **texto** | — | — | Convertida para número |
| Faixas digitadas | `80-90`, `92-100`, `156 a 168`, `170-150` | 16 | **Ponto médio** da faixa |
| Valores impossíveis | 8, 9.288 (até uma faixa "200-300" → 250) | 17 | Fora de [40; 220] → ausente |

- **Por que ponto médio?** É a melhor estimativa de uma faixa sem enviesar para cima ou para baixo.
- **Por que 40–220 bpm?** Cobre recém-nascidos (FC alta) até crianças maiores/atletas (FC baixa), barrando só o impossível (referência: Fleming et al., 2011).

---

### 4.8 Variáveis categóricas

#### 4.8.1 Método padrão: normalizar + dicionário

Para cada coluna: **(1)** passar para minúsculas, **(2)** remover acentos, **(3)** tirar espaços das pontas, **(4)** mapear por um
dicionário (em [src/config.py](../src/config.py)) para o nome canônico. O que não está no dicionário vira ausente.

**Por que esse método?** É transparente e auditável: cada mapeamento é explícito, e nada é "adivinhado" por algoritmo.

#### 4.8.2 `SEXO`

| Valor bruto | Bruto | Final |
|---|---|---|
| M | 6.065 | M |
| Masculino | 584 | M |
| masculino | 79 | M |
| F | 4.477 | F |
| Feminino | 247 | F |
| **Indeterminado** | 1.417 | **ausente** |
| (vazio) | 4 | ausente |

- **Por que "Indeterminado" → ausente?** Num ambulatório de cardiologia pediátrica, "indeterminado" parece "não preenchido", não um achado clínico.
  Reforço: no bruto, 748 desses registros nem tinham alvo — eram registros quase vazios (que a remoção de duplicatas e de linhas sem rótulo eliminou em grande parte; ficaram 523).
- **Resultado:** 2 categorias (M = 59,0%, F) e 4,6% de ausentes.

#### 4.8.3 `SOPRO` e `PULSOS`

| Variável | Problema | Resultado |
|---|---|---|
| SOPRO | "Sistólico"/"sistólico", "Contínuo"/"contínuo", "Sistolico e diastólico" | 7 grafias → **5 categorias**: Ausente, Sistólico, Contínuo, Diastólico, Sistólico e diastólico |
| PULSOS | "Normais"/"NORMAIS", "Amplos"/"AMPLOS", espaço extra em "Diminuídos " | 7 grafias → **5 categorias**: Normais, Amplos, Diminuídos, Femorais diminuídos, Outro |

#### 4.8.4 `Convenio` (seguro de saúde)

| Etapa | O que | Resultado |
|---|---|---|
| 1 | Maiúsculas, sem acento, sem pontuação final (`REAL S.` → `REAL S`) | 367 grafias → **231 valores** |
| 2 | Categorias com **menos de 1%** dos convênios informados (≈ 83 registros) → `OUTROS` | **18 categorias** finais |
| 3 | Ausente → `NAO INFORMADO` | 3.158 registros (27,5%) |

**Categorias finais** (18): NAO INFORMADO 3.158 · GS 1.988 · **OUTROS 1.721** · UR 1.388 · CAMED 531 · GRUPO 459 · SB 436 · MEDIAL 350 ·
REAL S 254 · SA 224 · IDEAL 154 · NORCLIN 152 · SEMEPE 123 · FUSEX 123 · SULA 114 · UG 114 · CC 95 · REAL 86.

| Decisão | Motivo |
|---|---|
| Padronizar caixa/pontuação | "Camed" e "CAMED" são o mesmo convênio |
| Agrupar raros em "OUTROS" | Evita centenas de categorias minúsculas (teste qui-quadrado exige contagens mínimas; one-hot geraria colunas quase vazias) |
| Ausente como categoria própria | A falta de convênio pode ser informativa (ex.: atendimento particular/público) e a categoria completa facilita a codificação |

> ⚠️ **Esta é a parte mais fraca da limpeza** — ver Seção 8.1 (sinônimos não unidos e "OUTROS" com 15%).

#### 4.8.5 `MOTIVO1` e `MOTIVO2`

| Problema | Exemplo | Tratamento |
|---|---|---|
| Código numérico embutido | `5 - Parecer cardiológico`, `6 - Sopro` | Prefixo removido → `Parecer cardiológico`, `Sopro` |
| Acentos faltando | `Cardiopatia congenica`, `Cardiopatia na familia` | → `congênita`, `família` |

O número parece indicar o **grupo** do motivo (1 = cardiopatia estabelecida, 2 = check-up, 5 = parecer, 6 = suspeita, 7 = outro) e, no
MOTIVO2, o grupo do MOTIVO1 (não verifiquei linha a linha). Por isso o prefixo é redundante e foi removido.

#### 4.8.6 `HDA 1` e `HDA2`

- `HDA 1`: só correção de acento (`Palpitacao` → `Palpitação`). Mantém 8 categorias; 25,9% ausente.
- `HDA2`: 96,5% ausente (muito esparsa). **Não tratada na limpeza**; na transformação ela é unida a HDA 1 em indicadores de sintoma.
- `B2`: sem problemas de grafia (5 categorias mantidas).

---

## 5. Resultado: antes × depois

### 5.1 Variáveis numéricas

| Variável | Momento | n | % ausente | Média | DP | Mín | Mediana | Máx | Assimetria |
|---|---|---|---|---|---|---|---|---|---|
| **IDADE** | Bruto | 11.377 | 11,6 | 4,9 | 8,8 | **−113,2** | 4,0 | **71,8** | −7,8 |
| | Limpo | 10.696 | 6,7 | 5,0 | 4,5 | 0,0 | 3,8 | 19,0 | 0,8 |
| **Peso** | Bruto | 12.555 | 2,5 | 16,6 | 17,0 | **−40,0** | 12,8 | 157,0 | 1,5 |
| | Limpo | 9.507 | 17,1 | 20,8 | 16,4 | 1,0 | 16,0 | 127,0 | 1,4 |
| **Altura** | Bruto | 12.873 | 0,0 | 66,1 | 56,0 | **0,0** | 69,0 | 198,0 | 0,1 |
| | Limpo | 8.003 | 30,2 | 100,9 | 35,3 | 40,0 | 99,0 | 198,0 | 0,2 |
| **IMC** | Bruto | 8.146 | 36,7 | 17,5 | 15,0 | 0,0 | 17,0 | **848,0** | **43,2** |
| | Limpo | 7.587 | 33,9 | 17,3 | 3,4 | 10,1 | 16,7 | 39,5 | 1,3 |
| **PAS** | Bruto | 5.143 | 60,0 | 101,8 | 18,9 | 60,0 | 100,0 | **990,0** | **26,6** |
| | Limpo | 5.099 | 55,5 | 101,5 | 11,6 | 60,0 | 100,0 | 180,0 | 1,2 |
| **PAD** | Bruto | 5.133 | 60,1 | 62,6 | 9,1 | **6,0** | 60,0 | 120,0 | 0,9 |
| | Limpo | 5.089 | 55,6 | 62,7 | 9,0 | 35,0 | 60,0 | 120,0 | 1,0 |
| **FC** | Bruto | 10.989 | 14,6 | 96,6 | 92,7 | 8,0 | 92,0 | **9.288,0** | **89,5** |
| | Limpo | 10.761 | 6,2 | 95,2 | 18,0 | 43,0 | 92,0 | 214,0 | 1,2 |

**Como interpretar:**

| Observação | O que mostra |
|---|---|
| Assimetria do IMC: 43,2 → 1,3; FC: 89,5 → 1,2; PAS: 26,6 → 1,2 | Os valores enormes eram causados **só pelos erros**. Depois da limpeza ficam em 1–1,3, que é assimetria real (cauda de crianças maiores) |
| DP do IMC: 15,0 → 3,4; FC: 92,7 → 18,0 | Os extremos inflavam a dispersão |
| Medianas quase não mudam (exceto Peso/Altura) | A mediana já era robusta; a limpeza removeu o que distorcia a **média** e o **DP** |
| Mediana de Peso/Altura **sobe** (12,8 → 16,0 kg; 69 → 99 cm) | Os zeros "puxavam" a mediana para baixo |
| % ausente de Peso/Altura/IMC | Ver nota abaixo |

> **Cuidado ao comparar % de ausentes:** o número de linhas muda (12.873 → 11.470), então as porcentagens não são totalmente comparáveis.
> E em Peso/Altura/IMC a % sobe porque os zeros (ausência disfarçada) passaram a contar como ausentes.

**Ausência efetiva no bruto (contando zeros e erros como ausentes):**

| Variável | Ausente "declarado" | Ausente "efetivo" | Limpo |
|---|---|---|---|
| Peso | 2,5% | ≈ 22,7% (318 vazios + 2.609 zeros + 1 negativo) | 17,1% |
| Altura | 0,0% | ≈ 34,6% (4.460 zeros) | 30,2% |
| IMC | 36,7% | ≈ 37,6% (4.727 vazios + 109 zeros) | 33,9% |
| PPA | 1,7% | ≈ 83,9% (217 vazios + 1.496 `#VALUE!` + 9.081 "Não Calculado") | 81,9% |

### 5.2 Variáveis categóricas

| Variável | Categorias (bruto → limpo) | % ausente (bruto → limpo) | Moda (limpo) | % da moda |
|---|---|---|---|---|
| NORMAL X ANORMAL | 4 → 2 | 9,1 → 0,0 | Normal | 57,3 |
| SEXO | 6 → 2 | 0,0 → 4,6 | M | 59,0 |
| Convenio | 374 → 18 | 31,9 → 0,0 | NAO INFORMADO | 27,5 |
| PULSOS | 7 → 5 | 9,3 → 0,3 | Normais | 98,7 |
| PPA | 9 → 4 | 1,7 → 81,9 | Normal | 86,1 |
| B2 | 5 → 5 | 9,2 → 0,2 | Normal | 94,9 |
| SOPRO | 7 → 5 | 9,1 → 0,1 | Ausente | 61,9 |
| HDA 1 | 8 → 8 | 33,2 → 25,9 | Assintomático | 76,2 |
| HDA2 | 8 → 8 | 96,8 → 96,5 | Palpitação | 20,6 |
| MOTIVO1 | 5 → 5 | 8,2 → 1,2 | Parecer cardiológico | 45,5 |
| MOTIVO2 | 16 → 16 | 27,2 → 22,1 | Cirurgia | 31,7 |

*(Por que a % ausente de várias variáveis cai? Porque as linhas removidas — duplicatas e sem rótulo — eram, em grande parte, quase vazias.)*

### 5.3 Datas

| Variável | % ausente (bruto → limpo) |
|---|---|
| Atendimento | 7,6 → 0,8 |
| DN | 10,7 → 5,1 |
| IDADE | 11,6 → 6,7 |

---

## 6. Faixas de plausibilidade

| Variável | Faixa aceita | Referência que orientou | Removidos |
|---|---|---|---|
| IDADE | 0 a 19 anos | Dicionário de dados (população do estudo) | 197 |
| Peso | 1 a 150 kg | OMS (curvas de crescimento) | 4 |
| Altura | 40 a 200 cm | OMS | 12 |
| IMC | 10 a 40 kg/m² | OMS (IMC para idade, 0–5 e 5–19 anos) | 49 |
| PAS | 60 a 200 mmHg | Flynn et al., AAP 2017 | 2 |
| PAD | 30 a 130 mmHg | Flynn et al., AAP 2017 | 2 |
| FC | 40 a 220 bpm | Fleming et al., Lancet 2011 | 17 |

> **Aviso de honestidade:** os números exatos acima são **limites amplos escolhidos por mim, orientados** por essas referências — **não** são valores
> copiados literalmente delas (as referências trazem curvas e percentis, não "limites de erro"). Por isso, na defesa, diga
> "faixas de plausibilidade fisiológica amplas, baseadas em", e não "valores definidos pela OMS".

**Por que faixas amplas (plausibilidade) e não de normalidade?**
O objetivo da limpeza é remover **erro de registro**, não casos clínicos raros. Uma criança com IMC 14 (baixo peso) ou PA 150 (hipertensa) é
justamente o tipo de caso que interessa à pesquisa; apagá-lo seria viés.

---

## 7. Testes de sensibilidade

Para saber se as decisões mais discutíveis mudam as conclusões, refiz as análises com regras alternativas.

### 7.1 Faixa do IMC

| Cenário | n | Correlação com o alvo (r) | Média | Mediana | DP |
|---|---|---|---|---|---|
| **Atual: [10; 40]** | 7.587 | −0,195 | 17,33 | 16,74 | 3,38 |
| Ampliada: [8; 60] | 7.620 | −0,200 | 17,33 | 16,73 | 3,50 |
| Sem nenhum corte | 7.636 | −0,201 | 17,35 | — | 4,08 |

**Conclusão:** o r (rank-bisserial, Mann-Whitney) passa de −0,195 para −0,200: a decisão **não altera** a conclusão (associação fraca com o alvo).

### 7.2 Convenio: unir sinônimos e mudar o limiar de "OUTROS"

Sinônimos prováveis unidos (por semelhança de texto): NORCLIN/NORCLINICAS/NORCLINICA/NORCL · SULA/SUL AMERICA/SUL AM · REAL/REAL S ·
MEDISERV/MEDISERVICE/MEDISE · PARTICULAR/PART · TABELA/TAB · UR/U RECIFE.

| Cenário | Categorias | "OUTROS" | V de Cramér | % Anormal em "OUTROS" |
|---|---|---|---|---|
| **Atual** (limiar 1%) | 18 | 15,0% | 0,126 | 48,1% |
| Sinônimos unidos (limiar 1%) | 17 | 12,7% | 0,121 | 47,8% |
| Sinônimos unidos, limiar 0,5% | 26 | 7,7% | 0,151 | — |
| Sinônimos unidos, limiar 0,2% | 40 | 4,8% | 0,163 | — |

*(% Anormal geral: 42,7%.)*

**Conclusões:**
- Unir os sinônimos mexe em apenas **353 linhas (3,1%)**.
- O V de Cramér fica entre **0,12 e 0,16** em todos os cenários → associação **fraca**; a posição de Convenio no ranking (~10ª) não muda.
- O V sobe quando há mais categorias porque, com mais categorias pequenas, o V tende a subir mesmo sem relação real.
- "OUTROS" tem 48% de Anormais (vs. 43% geral): **não distorce** o resultado.

---

## 8. Limitações, correções e pendências

Esta seção é o "ponto cego" — leia antes de apresentar.

### 8.1 Convenio (a falha mais real)

| Problema | Detalhe |
|---|---|
| Sinônimos separados | Contagens no conjunto limpo: NORCLIN (152) separada de NORCLINICAS (81), NORCLINICA (36) e NORCL (26); SULA (114) separada de SUL AMERICA (53) e SUL AM (26); REAL (86) separada de REAL S (254); MEDISERVICE (36), MEDISERV (24) e MEDISE (23); PARTICULAR (45) e PART (33); TABELA (23) e TAB (21); UR (1.388) e U RECIFE (45) |
| "OUTROS" com 15% (1.721 registros, 215 grafias distintas) | Mistura convênios muito diferentes. Os maiores grupos dentro dele são, em boa parte, **sinônimos de operadoras** que ficaram abaixo do limiar |
| **PARTICULAR (45) e SUS (66) escondidos em "OUTROS"** | São categorias com sentido próprio (acesso/condição socioeconômica) e mereciam ficar separadas |
| Não dá para **confirmar** que as siglas são sinônimos | O dicionário de dados não explica as siglas. "REAL" = "REAL S" é suposição por semelhança de texto |

**Correção recomendada (ainda NÃO aplicada):** mapa manual de sinônimos (~10 linhas), manter PARTICULAR e SUS separados. Impacto esperado: pequeno (Seção 7.2).

### 8.2 Erros e divergências no relatório/plano

| Item | O que está errado/diferente | Situação |
|---|---|---|
| Texto da Seção 4 do `.docx` | Atribui idades de ≈ −100 anos a "datas lidas no século errado". **Causa real: Atendimento em branco** | **Pendente de correção** |
| Rótulo no log ("Ano de 2 dígitos lido no século errado") | Na prática só captura datas posteriores a 2010 | **Pendente de correção** |
| Plano aprovado dizia "datas futuras recebem −100 anos" | Implementado como "vira ausente" (resultado equivalente) | Divergência documentada (Seção 4.3.2) |
| "`#VALUE!` coincide com IDADE ausente" (relatório) | Só conferi que as **contagens** são iguais (1.496), não linha a linha | Afirmação a atenuar |
| PA ausente "concentrada em crianças pequenas" | Hipótese **não testada** | Tratar como hipótese |
| MOTIVO2 prefixo = grupo do MOTIVO1 | Não conferi linha a linha | Tratar como hipótese |

### 8.3 Decisões que um avaliador pode questionar

| Decisão | Risco | Mitigação |
|---|---|---|
| Faixa do IMC [10; 40] | Remover obesidade grave real | Só 1 caso plausível removido; teste de sensibilidade (Seção 7.1) |
| Altura < 40 cm e Peso < 1 kg | Remover prematuros extremos reais | ~2 casos prováveis em 16; as colunas nem entram no CSV transformado |
| Remover duplicatas ignorando ID | Duas pessoas diferentes "idênticas" em linhas quase vazias | Risco considerado pequeno |
| Remover 416 linhas sem rótulo | Perda de dados | Imputar o alvo introduziria viés |
| "Indeterminado" → ausente | Pode ter sentido clínico | Maioria eram registros quase vazios |
| Não recalcular PPA | Perde ~83% da informação de PPA | Recalcular exigiria tabelas oficiais e percentil de estatura |
| Datas > 2010 → ausente | Ajuste do limite é arbitrário | Os atendimentos reais vão de 2003–2010 |
| IDADE sem data corrigida por fator (225 casos) | Pressupõe que o erro é sempre ~3,8% | Medido em dados com ambas as informações |

---

## 9. O que a limpeza NÃO faz

| Não fizemos | Por quê | Onde é tratado |
|---|---|---|
| **Imputação** de ausentes | Evita criar dado artificial antes de analisar o real | Etapa de transformação (mediana + indicadores de ausência) |
| **Remoção de outliers estatísticos** | Valores extremos mas possíveis (PAS 180, FC 214) são informação clínica | Mantidos; assimetria tratada com log(1+x) na transformação |
| **Padronização/normalização** (z-score) | Não é "limpeza" | Transformação |
| **Codificação** (one-hot, ordinal) | Idem | Transformação |
| **Remoção de colunas** (ID, Peso, Altura…) | Decisão de modelagem | Transformação |
| **Recalcular a PPA** | Falta de percentil de estatura/tabelas oficiais | Mantida com ausentes + indicador `ppa_ausente` |
| **Balanceamento do alvo** | Desbalanceamento é leve (57/43) | Parte 2, se necessário |

---

## 10. Perguntas prováveis e respostas

| Pergunta | Resposta curta |
|---|---|
| **Por que não apagou as linhas com erro?** | Um valor impossível não invalida os outros ~20 campos. Anular só o campo preserva informação. |
| **Por que não imputou os ausentes?** | Imputar antes de analisar mascara o padrão real de falta. Fica para a transformação, junto com indicadores de ausência. |
| **Por que recalculou IDADE e IMC?** | São variáveis derivadas. A IDADE original tinha erro sistemático (~3,8%) e o IMC tinha valores absurdos (848). Recalcular da fonte (datas; Peso/Altura) é mais confiável. |
| **Como você sabe que a IDADE estava errada?** | Comparei com (Atendimento − DN) onde ambas existem: a razão mediana é 1,0377, equivalente a um ano de 352 dias. |
| **Por que remover as linhas sem alvo?** | Imputar o alvo é inventar a resposta que o modelo deve prever. |
| **Os cortes de faixa não eliminam casos reais?** | São faixas de plausibilidade amplas. Dos 49 IMC removidos, só 1 parece real; teste de sensibilidade com [8; 60] mudou r de −0,195 para −0,200. |
| **De onde vêm os limites?** | Orientados por OMS (crescimento), AAP 2017 (PA) e Fleming 2011 (FC) — mas os valores exatos são limites amplos escolhidos por mim, não valores literais dessas fontes. |
| **Por que a ausência de Peso e Altura aumentou?** | Os zeros eram ausência disfarçada. A ausência *efetiva* já era ~22,7% (Peso) e ~34,6% (Altura). |
| **Por que "Indeterminado" virou ausente?** | Parece campo não preenchido; 748 desses registros nem tinham alvo. |
| **Por que não recalculou a PPA?** | Exige percentil de estatura (Altura tem 30% ausente) e tabelas oficiais. |
| **O Convenio foi bem padronizado?** | Parcialmente. Caixa e pontuação sim; sinônimos não. Unir sinônimos prováveis mudaria 3,1% das linhas e o V de Cramér de 0,126 para 0,121. |
| **A limpeza interfere nos resultados?** | Reduz o ruído (assimetria do IMC 43 → 1,3) sem distorcer relações: a correlação IDADE × IMC (Spearman) praticamente não muda (0,355 → 0,356). |

---

## 11. Reprodutibilidade e mapa regra → código

### 11.1 Como rodar

```
python main.py            # roda as 5 etapas e gera tudo em ./saida
python src/p02_limpeza.py # roda só a limpeza
```

### 11.2 Arquivos gerados pela limpeza

| Arquivo | Conteúdo |
|---|---|
| `saida/UCMF_clean.csv` | Conjunto limpo (11.470 × 21) |
| `saida/tabelas/tab_log_limpeza.csv` | Log: variável, problema, solução, nº de registros |
| `saida/tabelas/tab_descritiva_antes_depois.csv` | Estatísticas antes/depois (Seção 5.1) |
| `saida/tabelas/tab_categoricas_limpo.csv` | Resumo das categóricas após a limpeza |
| `saida/resultados.json` | Números usados no texto do relatório |

### 11.3 Onde está cada regra no código ([src/p02_limpeza.py](../src/p02_limpeza.py))

| Regra | Função / trecho |
|---|---|
| Duplicatas, alvo | bloco 1–2 de `executar()` |
| Conversão de datas (dd/mm/aa, dd/mm/aaaa, serial) | `parse_data()` |
| Datas > 2010; recálculo da IDADE; fator 1,0377 | `limpar_datas_idade()` |
| Faixas de plausibilidade (todas as numéricas) | `fora_da_faixa()` + `FAIXAS` em `config.py` |
| Zeros em Peso/Altura; IMC recalculado | blocos 4 de `executar()` |
| PAS ≤ PAD | bloco 5 |
| PPA (erros, agrupamento, coerência com PA) | bloco 6 + `MAP_PPA` em `config.py` |
| FC (texto, faixas, ponto médio) | bloco 7 |
| Padronização categórica | `normalizar()` + `mapear()` + `MAP_SEXO/SOPRO/PULSOS/ALVO` em `config.py` |
| Convenio (caixa, limiar 1%, "NAO INFORMADO") | bloco 8; `LIMIAR_RARO_CONVENIO` em `config.py` |
| Log de cada regra | classe `Log` |

---

*Documento gerado a partir dos resultados de `main.py` e dos testes de sensibilidade realizados na conversa.
Números conferidos contra `tab_log_limpeza.csv`, `tab_descritiva_antes_depois.csv` e `tab_categoricas_limpo.csv`.*
