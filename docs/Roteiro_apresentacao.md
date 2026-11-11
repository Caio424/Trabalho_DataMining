# Roteiro da apresentação — Etapa de Limpeza (slides 5, 6 e 7)

Guia para você apresentar a sua parte **sem deixar dúvidas**. Para cada slide: o que dizer, o que a plateia
pode estranhar e a frase que evita a dúvida antes de ela surgir.

> **Tempo total:** 4 a 5 minutos. **Regra de ouro:** explique o *porquê* antes do *número*. Quem entende o motivo não pergunta o resultado.

## Sumário

1. [Antes de começar: checklist](#1-antes-de-começar-checklist)
2. [Vocabulário que você precisa dizer em voz alta](#2-vocabulário-que-você-precisa-dizer-em-voz-alta)
3. [Ponte do slide 4 do grupo](#3-ponte-do-slide-4-do-grupo)
4. [Slide 5 — Etapa-Limpeza](#4-slide-5--etapa-limpeza)
5. [Slide 6 — Como tratamos os erros?](#5-slide-6--como-tratamos-os-erros)
6. [Slide 7 — Tabela Geral (Mestre)](#6-slide-7--tabela-geral-mestre)
7. [Fechamento e ponte para o próximo colega](#7-fechamento-e-ponte-para-o-próximo-colega)
8. [Dúvidas que vão aparecer (e a resposta pronta)](#8-dúvidas-que-vão-aparecer-e-a-resposta-pronta)
9. [Armadilhas: frases a evitar](#9-armadilhas-frases-a-evitar)
10. [Versão curta (2 minutos)](#10-versão-curta-2-minutos)
11. [Cola de números](#11-cola-de-números)

---

## 1. Antes de começar: checklist

| ✔ | Item | Por quê |
|---|---|---|
| ☐ | Corrigir "Altura **0m**" para "Altura **0 cm**" no slide 4 do grupo | Altura 0 m é um erro de unidade que gera dúvida |
| ☐ | Combinar com quem apresentou o slide 4 que os números dele são do **arquivo bruto** | Evita contradição entre 149 (IMC fora da faixa) e 49 |
| ☐ | Ler o guia [Limpeza_dos_dados.md](Limpeza_dos_dados.md), seções 4 e 8 | É onde estão as decisões e as limitações |
| ☐ | Ensaiar com cronômetro | A tabela do slide 7 é a parte que mais estoura o tempo |
| ☐ | Decidir quais 3 linhas da tabela você vai destacar | Não leia a tabela inteira |
| ☐ | Saber de cor: 12.873 → 11.470 / 987 / 416 / 34 regras | São os números que sempre são perguntados |

---

## 2. Vocabulário que você precisa dizer em voz alta

Seus colegas e o professor podem não conhecer estes termos. Explique **na primeira vez** que usar.

| Termo | Diga assim |
|---|---|
| **Ausente (NaN)** | "Ausente quer dizer que o valor fica em branco; **a linha continua**, só aquela célula é esvaziada." |
| **Plausibilidade** | "Plausível é o que **poderia existir** numa criança de 0 a 19 anos. Não é o mesmo que normal." |
| **Imputar** | "Imputar é **preencher um valor faltante com uma estimativa**, como a média. Nós não fizemos isso na limpeza." |
| **Número serial do Excel** | "Quando o Excel guarda uma data como número de dias. Por exemplo, 38574 é 10 de agosto de 2005." |
| **DP (desvio-padrão)** | "Mede o quanto os valores se espalham. Um valor absurdo faz o desvio-padrão explodir." |
| **IMC** | "Índice de massa corporal: peso dividido pela altura ao quadrado." |
| **PPA / HAS** | "Classificação de pressão arterial: Normal, Pré-hipertensão, Hipertensão estágio 1 e estágio 2." |
| **Alvo** | "A variável que queremos prever: Normal ou Anormal, isto é, se há patologia cardíaca." |
| **Derivado** | "Um valor calculado a partir de outros. A idade vem das datas; o IMC vem de peso e altura." |

---

## 3. Ponte do slide 4 do grupo

O slide anterior mostra os problemas (pressão ausente em 60%, altura zero em 35%, gráficos de valores fora da faixa).

> **Diga:** "Vocês viram os problemas. Eu vou mostrar **o que fizemos com cada um** e por quê."

**Dúvida que isso evita:** "e agora?". A plateia sai do slide 4 sabendo que os dados estavam ruins; você responde a isso.

---

## 4. Slide 5 — Etapa-Limpeza

**Tempo: 1:30.** Objetivo: a plateia entender a **lógica** antes de ver os casos.

### 4.1 Passo a passo

| Ordem | O que fazer | Tempo |
|---|---|---|
| 1 | Apontar o número grande no canto: **12.873 → 11.470** | 20 s |
| 2 | Explicar os 5 princípios (esquerda) | 50 s |
| 3 | Explicar a ordem das etapas (direita) | 30 s |
| 4 | Apontar o indicador de etapas embaixo | 5 s |

### 4.2 O que dizer

**Número grande (12.873 → 11.470):**
> "Saímos de **12.873 para 11.470 registros**. Foram **987 duplicatas** e **416 linhas sem rótulo**."

**Dúvida que isso evita:** "perderam 1.400 linhas, e por quê?". Explique já: duplicatas contam em dobro e linhas sem o alvo não servem para treinar o modelo.

**Princípios (diga os cinco, destaque os dois primeiros):**

| # | Princípio | Frase para evitar dúvida |
|---|---|---|
| 1 | Valor impossível vira ausente | "A **linha não é apagada**. Só a célula errada é esvaziada, porque as outras colunas daquele paciente podem estar certas." |
| 2 | Plausibilidade, não normalidade | "Uma FC de 200 num recém-nascido pode ser real. Uma de 9.288 não. A faixa só barra o **impossível**, não o raro." |
| 3 | Derivados são recalculados | "A idade vem das datas e o IMC vem de peso e altura. Se a fonte está certa, o derivado calculado é o confiável." |
| 4 | Nada é imputado na limpeza | "Não preenchemos ausentes agora. Isso fica para a transformação, para a análise refletir só o que foi observado." |
| 5 | Toda regra é registrada | "São **34 regras**, e cada uma conta quantos registros alterou. Dá para auditar." |

**Dúvida que o princípio 2 evita:** "vocês não apagaram casos reais?". Já responda aqui que a faixa é larga de propósito.

**Ordem das etapas (direita):**
> "A ordem importa porque **uma etapa depende da outra**: datas antes da idade, peso e altura antes do IMC, e pressão antes da PPA. Se o IMC fosse calculado antes de limpar peso e altura, herdaria o erro."

Você **não precisa** explicar as 8 etapas uma por uma. Cite os três pares de dependência e pronto.

**Indicador de etapas (embaixo):**
> "Estamos na etapa 2 do nosso fluxo: depois do perfil, antes das análises comparativas."

### 4.3 Dúvidas prováveis neste slide

| Pergunta | Resposta |
|---|---|
| "Por que 11.470 e não os 12.873?" | "987 duplicatas e 416 sem rótulo. Duplicatas contam em dobro; sem rótulo não dá para treinar." |
| "O que é 'ausente'?" | Veja o vocabulário (seção 2). |
| "Por que não imputaram?" | "Imputar antes de analisar mascara o padrão real de falta. Fazemos na etapa de transformação." |

---

## 5. Slide 6 — Como tratamos os erros?

**Tempo: 1:30.** Objetivo: mostrar que vocês **investigaram**, não só filtraram. Conte duas histórias, não leia as seis linhas.

### 5.1 Estrutura da tabela (explique em 10 s)
> "Cada linha é um **tipo de erro**: à esquerda o erro, no meio por que é erro, e à direita o método."

### 5.2 Linha 1 — Zeros como "não medido" (conte esta história)
> "Peso zero aparecia em **1.652 registros** e altura zero em **3.455**. Zero quilo não existe, então o zero **escondia uma medida que não foi feita**. Transformamos em ausente."

**Dúvida que isso evita:** "por que a ausência de peso e altura aumentou depois da limpeza?". Diga já:
> "Isso faz a ausência parecer maior depois, mas ela **já existia**, disfarçada de zero."

### 5.3 Linha 5 — Derivados incorretos (conte esta história)
> "A idade original estava errada **de forma sistemática**. Comparamos com a diferença entre as datas e ela era cerca de **3,8% maior**, como se o ano tivesse **352 dias**. Por isso recalculamos a idade a partir das datas."

**Como explicar que vocês descobriram isso (evita "como vocês sabem?"):**
> "Pegamos os registros que tinham a idade e as duas datas, dividimos uma pela outra, e a **mediana da razão deu 1,0377**. 365,25 dividido por 1,0377 dá 352."

### 5.4 As outras linhas (uma frase cada)

| Linha | Frase |
|---|---|
| 2. Valores impossíveis | "IMC 848, pressão sistólica 990, FC 9.288: barramos com faixas de plausibilidade; fora da faixa vira ausente." |
| 3. Formatos misturados | "Datas guardadas como número do Excel e a FC como texto, com faixas como '80-90'. Convertemos." |
| 4. Grafias inconsistentes | "O mesmo sexo escrito de três jeitos e **367 grafias de convênio**. Padronizamos o texto." |
| 6. Registros inutilizáveis | "987 duplicatas e 416 sem rótulo. Removidos." |

### 5.5 Dúvidas prováveis neste slide

| Pergunta | Resposta |
|---|---|
| "O que é 'fora da faixa'?" | "Fora do intervalo plausível para 0 a 19 anos; mostramos as faixas no slide 3 do grupo." |
| "A FC de '80-90', como converteram?" | "Pelo ponto médio da faixa: 85." |
| "Convênio: 367 viraram quantos?" | "18 categorias; as raras, com menos de 1%, foram agrupadas em 'OUTROS'." |
| "Por que a idade estava errada?" | "Provavelmente a planilha original usou um divisor de ano errado. Não temos como confirmar, mas o fator é consistente." |

---

## 6. Slide 7 — Tabela Geral (Mestre)

**Tempo: 1:30 a 2:00.** Objetivo: **provar** com antes e depois. **Não leia a tabela.** Ela é consulta; você narra três linhas.

### 6.1 Como abrir (10 s)
> "Esta tabela resume tudo, variável por variável: o problema, por que é problema, o método e o resultado. Vou destacar **três linhas**."

### 6.2 As três linhas

**1. IDADE** (a que tem a melhor história)
> "A idade ia de **−113 a 72 anos**. Idade negativa porque o atendimento estava em branco ou antes do nascimento; acima de 19 porque está fora do escopo do estudo. Recalculamos pelas datas e aplicamos a faixa de 0 a 19."

**2. IMC** (a que tem os melhores números)
> "O IMC chegava a **848** e o desvio-padrão era **15**. Recalculamos a partir de peso e altura e aplicamos a faixa de 10 a 40. O máximo caiu para **39,5** e o desvio-padrão para **3,4**."

**3. PPA** (a que mostra decisão metodológica)
> "A PPA tinha erro de fórmula, '#VALUE!', e 'Não Calculado'. Viraram ausentes. As nove classes foram agrupadas em **quatro níveis ordenados**."

### 6.3 Pontos que a tabela gera dúvida (diga antes que perguntem)

| Ponto na tabela | Por que gera dúvida | O que dizer |
|---|---|---|
| Resultado de **Peso e Altura**: "mín. −40 → 1" e "0 → 40" | Parece que a faixa foi imposta de forma arbitrária | "Eram valores como −40 kg e altura 10 cm: impossíveis." |
| **Peso/Altura ficam com mais ausentes** | Parece que a limpeza piorou | "Os zeros eram ausência disfarçada. A limpeza só revelou." |
| **PPA com 81,9% ausente** | Parece que perdemos quase tudo | "A PPA já era quase toda 'Não Calculado'. Não a recalculamos porque exige o percentil de estatura." |
| **DP, "Máx."** | Siglas | "DP é desvio-padrão; Máx. é o valor máximo." |
| **Linha "Convenio e MOTIVO1/2"** | Pode parecer superficial | "Foram só padronizações de texto." |

### 6.4 Fechamento do slide (15 s)
> "O resultado é um conjunto com valores **plausíveis**, **sem nenhum valor inventado**, pronto para as análises comparativas."

### 6.5 Dúvidas prováveis neste slide

| Pergunta | Resposta |
|---|---|
| "Esses limites são da OMS?" | "São faixas amplas de plausibilidade **baseadas em** OMS, Fleming (2011) e Flynn (2017); os números exatos são nossos." |
| "Por que a faixa do IMC é 10 a 40?" | "Para barrar o impossível. Um teste com faixa mais larga, de 8 a 60, mudou a correlação com o alvo de −0,195 para −0,200, praticamente nada." |
| "Removeram obesidade grave real?" | "No máximo 1 caso entre 49 parecia real; o resto tinha peso ou altura incoerentes." |
| "O que é 'ordinal' na PPA?" | "Os quatro níveis têm ordem de gravidade: Normal, Pré-HAS, HAS-1 e HAS-2." |

---

## 7. Fechamento e ponte para o próximo colega

> "Em resumo: de 12.873 registros ficamos com **11.470**, com valores impossíveis tratados, sem nenhum dado inventado, e com **34 regras documentadas**. Agora o [nome] vai mostrar as **análises comparativas** com esse conjunto limpo."

**Dúvida que isso evita:** "e agora?". A plateia entende o encadeamento do pipeline.

---

## 8. Dúvidas que vão aparecer (e a resposta pronta)

### 8.1 Sobre números que parecem se contradizer

| Parece contraditório | Explicação (diga com calma) |
|---|---|
| **Slide 4 do grupo:** IMC fora da faixa = **149**. **Seu slide:** 49 | O 149 conta a **coluna original** do arquivo bruto (109 zeros + 17 acima de 40 + 23 abaixo de 10). O 49 conta o que sobrou **depois de recalcular o IMC** e remover as duplicatas. |
| **Slide 4:** idade fora da faixa = **216**. **Tabela de limpeza:** 197 | 216 é a coluna original (122 negativas + 94 acima de 19). Depois do recálculo pelas datas, 197 ficam fora de 0 a 19. |
| **Slide 4:** FC fora da faixa = **16**. **Limpeza:** 17 | Faixas como "200-300" viram 250 no ponto médio e caem fora de 40 a 220. |
| **Slide 4:** altura zero em **35%**. **Seu slide:** 3.455 zeros | 35% é 4.460 de 12.873 no **arquivo bruto**; 3.455 são os zeros que sobraram **depois de remover duplicatas e linhas sem rótulo**. |
| **12.873** brutos × **11.470** limpos | 987 duplicatas e 416 linhas sem rótulo. |

> **Frase-chave:** "Os números do slide 4 contam o arquivo bruto; os meus contam depois de cada etapa de limpeza."

### 8.2 Sobre decisões metodológicas

| Pergunta | Resposta pronta |
|---|---|
| "Por que não apagaram as linhas com erro?" | "Um valor errado não invalida as outras ~20 colunas do paciente." |
| "Por que não preencheram os ausentes?" | "Preencher antes de analisar esconde o padrão real de falta. Fazemos na transformação, com indicador de ausência." |
| "Por que recalcularam em vez de corrigir?" | "Idade e IMC são derivados. Recalcular a partir da fonte elimina o erro na origem." |
| "Como sabem que a idade original estava errada?" | "Comparamos com Atendimento − DN: a razão mediana foi 1,0377, equivalente a um ano de 352 dias." |
| "Por que removeram as linhas sem alvo?" | "Imputar o alvo é inventar a resposta que o modelo deve prever." |
| "As faixas eliminam casos reais?" | "São largas de propósito. Dos 49 IMC removidos, só 1 parecia real; testamos faixa mais larga e o resultado quase não mudou." |
| "'Indeterminado' em SEXO por que virou ausente?" | "Parece campo não preenchido; a maioria eram registros quase vazios." |
| "Por que não recalcularam a PPA?" | "Exige o percentil de estatura, e a altura tinha 30% de ausentes. Recalcular seria inventar." |

### 8.3 Sobre o futuro e a generalização

| Pergunta | Resposta pronta |
|---|---|
| "E se uma criança nascer em 2016 e for prever?" | "O modelo não usa datas, só a idade calculada. A regra que barra datas depois de 2010 vale só para este arquivo histórico." |
| "Os dados são de 2003 a 2010; valem hoje?" | "Boa pergunta: o modelo pode se comportar diferente numa população mais recente. É uma limitação a considerar na próxima parte." |

### 8.4 Pergunta difícil: "O que ficou imperfeito?"

Responda **com honestidade**; isso passa mais segurança do que fingir perfeição.

> "A parte mais fraca é o **Convenio**. Padronizamos caixa e pontuação, mas alguns sinônimos, como 'REAL' e 'REAL S', continuam separados, e a categoria 'OUTROS' concentra 15% dos registros. Testamos unir os sinônimos: mudaria só **3,1% das linhas** e a associação com o alvo, de 0,126 para 0,121. Ou seja, **não altera a conclusão**."

---

## 9. Armadilhas: frases a evitar

| Evite dizer | Por quê | Diga |
|---|---|---|
| "Limpamos **todos** os erros" | Impossível garantir | "Tratamos os erros que identificamos" |
| "As faixas são **da OMS**" | Os números exatos são nossos | "**Baseadas** na OMS e na literatura" |
| "O Convenio está **padronizado**" | Há sinônimos separados | "Padronizado em caixa e pontuação" |
| "Imputamos os ausentes" | Não fizemos na limpeza | "**Não imputamos** na limpeza" |
| "Removemos os outliers" | Só removemos o **impossível** | "Anulamos valores **impossíveis**, não os extremos" |
| "Altura 0m" | Unidade errada | "Altura **0 cm**" |
| "A idade estava ruim porque datas no século errado" | **Isso está errado.** As idades de ≈ −100 anos têm **Atendimento em branco** | "A planilha subtraiu uma data em branco (1900) da data de nascimento" |
| "Eu acho que…" sobre números | Passa insegurança | "O resultado foi…" |

---

## 10. Versão curta (2 minutos)

Use se o tempo for cortado.

| Slide | O que dizer (≈ 40 s cada) |
|---|---|
| **5** | "12.873 → 11.470 registros. Cinco princípios: valor impossível vira ausente (a linha fica); faixas de plausibilidade, não de normalidade; derivados são recalculados; nada é imputado; toda regra é registrada. A ordem importa porque uma etapa depende da outra." |
| **6** | "Seis tipos de erro. Dois exemplos: zeros que escondiam medidas não feitas, e a idade, que estava 3,8% acima do real, como se o ano tivesse 352 dias; recalculamos pelas datas." |
| **7** | "Três exemplos do antes e depois: IDADE de −113 a 72 para 0 a 19; IMC máximo de 848 para 39,5; PPA com erros de fórmula virando ausente e 9 classes virando 4 níveis. Resultado: dados plausíveis, nada inventado." |

---

## 11. Cola de números

| Número | Significado | Onde aparece |
|---|---|---|
| **12.873** | Registros brutos | Slide 5 |
| **11.470** | Registros limpos | Slide 5 |
| **987** | Duplicatas removidas | Slide 5, 6, 7 |
| **416** | Linhas sem rótulo removidas | Slide 5, 6, 7 |
| **34** | Regras de limpeza | Slide 5 |
| **57% / 43%** | Normal / Anormal (limpo) | Slide 7 |
| **1.652** | Zeros em Peso (limpo) | Slide 6 |
| **3.455** | Zeros em Altura (limpo) | Slide 6 |
| **848 → 39,5** | IMC máximo | Slides 6 e 7 |
| **15,0 → 3,4** | DP do IMC | Slide 7 |
| **990 → 180** | PAS máxima | Slide 7 |
| **9.288 → 214** | FC máxima | Slide 7 |
| **−113 a 72 → 0 a 19** | Intervalo da IDADE | Slide 7 |
| **352 dias** | Ano implícito na IDADE original | Slides 6 e 7 |
| **+3,8%** | Excesso da IDADE original | Slides 6 e 7 |
| **9.183** | PPA anuladas | Slide 7 |
| **9 → 4** | Classes da PPA | Slide 7 |
| **367 → 18** | Categorias de Convenio | Slides 6 e 7 |
| **523** | "Indeterminado" em SEXO | Slide 7 |
| **81,9%** | PPA ausente depois da limpeza | Slide 7 |

---

## Pendências antes de apresentar

| Pendência | Situação |
|---|---|
| O relatório `.docx` ainda diz que as idades de ≈ −100 anos vêm de "datas lidas no século errado" (a causa real é Atendimento em branco) | **Não corrigido** |
| Convenio ainda tem sinônimos separados | **Não corrigido** (impacto pequeno, ver seção 8.4) |
| Regra de datas posteriores a 2010 fixa no código | **Não corrigida** (só afeta este arquivo histórico) |
| Slide 4 do grupo: "Altura 0m" | **A corrigir por vocês** |

Se o relatório e os slides forem entregues juntos, corrija o texto do relatório para que ambos digam a mesma coisa.
