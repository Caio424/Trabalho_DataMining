# Roteiro da apresentação – A2 (15 minutos)

Deck: https://claude.ai/artifact/5vTCpFNtaavknFHSQhuqXp (as notas de cada slide trazem a fala completa).

> **Regra da avaliação:** todos apresentam, e qualquer integrante pode ser chamado para responder qualquer pergunta. Cada um deve ler a seção 3 inteira, não só a sua parte.

## 1. Divisão e tempo

| Slide | Conteúdo | Tempo | Quem |
|---|---|---|---|
| 1 | Capa e pergunta | 0:30 | Integrante 1 |
| 2 | Problema e objetivo | 1:00 | Integrante 1 |
| 3 | Dados | 1:00 | Integrante 1 |
| 4 | Data leakage: o Sopro | 1:30 | Integrante 2 |
| 5 | Pré-processamento sem vazamento | 1:30 | Integrante 2 |
| 6 | Protocolo de avaliação | 1:30 | Integrante 2 |
| 7 | Modelos e hiperparâmetros | 1:00 | Integrante 3 |
| 8 | Resultado principal | 2:00 | Integrante 3 |
| 9 | A diferença é real? | 1:30 | Integrante 3 |
| 10 | Desbalanceamento e limiar | 1:00 | Integrante 4 |
| 11 | Erros e atributos | 1:30 | Integrante 4 |
| 12 | Conclusão | 1:00 | Integrante 4 |
| | **Total** | **15:00** | |

Com 3 integrantes: o Integrante 4 assume os slides 10–12, e o Integrante 1 fica com os slides 1–4.

## 2. A frase de cada slide

Se o tempo apertar, diga só isto:

1. "Dá para prever, antes da consulta, quem tem doença cardíaca?"
2. "Classificação binária; o erro caro é o falso negativo, por isso olhamos recall."
3. "11.470 pacientes, 57/43, e ausências que não são aleatórias."
4. "O Sopro é o diagnóstico do médico disfarçado de atributo; excluímos."
5. "Tudo que aprende com os dados é ajustado só no treino."
6. "Validação aninhada 10×5: o laço interno escolhe hiperparâmetros e o externo mede."
7. "Baseline: Regressão Logística; complexos: Árvore, Random Forest e Gradient Boosting."
8. "Random Forest é a melhor (AUC 0,802), mas todos estão próximos."
9. "Significativo pelo 5×2cv (p = 0,018), mas o ganho é pequeno; o Sopro inflaria a AUC para 0,95."
10. "Baixar o limiar para 0,3 corta 58% dos doentes perdidos, com o triplo de alarmes."
11. "O modelo acerta o bebê com suspeita e perde a criança mais velha em rotina."
12. "Serve para priorizar a agenda, não para substituir o cardiologista."

## 3. Perguntas prováveis e respostas

### Dados e vazamento

| Pergunta | Resposta |
|---|---|
| Por que o Sopro é vazamento? | É um achado do exame físico feito pelo cardiologista na mesma consulta que dá o diagnóstico. Na triagem, antes da consulta, ele não existe. Com ele, a AUC iria de 0,80 para 0,95: esse ganho é emprestado do diagnóstico. |
| A B2 também não é achado de exame? | É, e está declarada como limitação. A associação dela com o alvo é muito menor (V = 0,24 contra 0,84 do Sopro). Um trabalho futuro é testar o modelo sem B2. |
| Os Motivos de encaminhamento não vazam? | Eles são informação **anterior** à consulta: o que o médico que encaminhou suspeitou. São legítimos para triagem. Medimos a dependência: sem eles, a AUC cai para 0,72. |
| Por que não usaram o UCMF_transformed.csv da A1? | Porque a mediana, a média e o desvio dele foram calculados na base inteira. Usar esse arquivo na validação seria vazamento. A A2 parte do arquivo limpo e refaz tudo dentro do pipeline. |
| E os pacientes repetidos? | Não há identificador de paciente. Agrupamos por data de nascimento + sexo e repetimos a validação com partição agrupada: a AUC ficou igual (0,801). Não há sinal de vazamento por repetição. |

### Metodologia

| Pergunta | Resposta |
|---|---|
| Por que validação aninhada? | Para escolher hiperparâmetros sem tocar no teste. O laço interno (5 folds no treino) escolhe; o externo (10 folds) mede em dados que a busca nunca viu. |
| Por que não hold-out? | Com 11.470 instâncias, o resultado ficaria refém de uma única divisão. A regra prática da disciplina indica 10-fold estratificado para esse tamanho. |
| Por que estratificado? | Para manter a proporção 57/43 em todo treino e teste. |
| O que exatamente fica dentro do pipeline? | Log, imputação pela mediana com indicador de ausência, padronização, one-hot e, quando usado, SMOTE ou subamostragem. Tudo é refeito em cada partição de treino. |
| Por que SMOTE só no treino? | Exemplos sintéticos no teste avaliariam o modelo em pacientes que não existem. A regra dos slides: a transformação é modelada no treino e só aplicada ao teste. |
| Por que AUC-ROC como critério de busca? | Mede a ordenação por risco sem depender do limiar, que discutimos à parte. Com desbalanceamento leve, a ROC é adequada. |
| Que hiperparâmetros foram escolhidos? | Regressão Logística: C = 0,1. Random Forest: profundidade livre, sqrt dos atributos e folha mínima 5. |

### Resultados

| Pergunta | Resposta |
|---|---|
| Qual o melhor modelo? | Random Forest, AUC 0,802 ± 0,015. O Gradient Boosting fica praticamente empatado (0,800). |
| A diferença é significativa? | Sim. Pelo teste t 5×2cv de Dietterich, t = 3,44 e p = 0,018 < 0,05. Mas o efeito é pequeno: o erro vai de 26,3% para 25,6%. |
| Por que 5×2cv e não teste t nos 10 folds? | Os folds compartilham dados de treino, o que subestima a variância e infla o erro tipo I. O 5×2cv foi proposto por Dietterich justamente para isso. |
| Então vale usar a Random Forest? | Se a prioridade é desempenho, sim. Se é interpretabilidade, a Regressão Logística é quase equivalente e mostra o sentido de cada atributo (razão de chances). |
| Por que o recall é só 0,59? | Porque o limiar padrão é 0,5. Baixando para 0,3, o recall vai a 0,83. O modelo ordena bem (AUC 0,80); o corte é que precisa ser escolhido pela clínica. |
| Por que SMOTE não mudou a AUC? | A reamostragem desloca as probabilidades, mas não a ordem dos pacientes. Ela muda o recall e a especificidade no limiar 0,5, não a AUC. |
| Quem o modelo erra? | Crianças mais velhas (mediana de 4,6 anos) encaminhadas para parecer de rotina: o perfil delas é igual ao dos Normais nos atributos disponíveis. São 41% dos Anormais no limiar 0,5. |
| Quais atributos importam mais? | Motivo 2, Motivo 1, B2 e FC, por permutação. Encaminhamento por sopro multiplica a chance por 3,72; B2 normal a reduz (razão de chances 0,18). |

### Reprodutibilidade e limitações

| Pergunta | Resposta |
|---|---|
| Como reproduzir? | `pip install -r requirements.txt` e `python main_a2.py`, com `random_state = 42`. Leva cerca de 50 minutos e gera os mesmos números. |
| Principais limitações? | Um único serviço e período (2003–2010); muitas ausências em pressão e PPA; B2 e Motivos próximos do julgamento clínico; sem identificador de paciente. |
| Como usaram IA? | Declarado no artigo: o Claude (Claude Code) apoiou o código, o protocolo e a primeira versão do texto; o grupo revisou e conferiu os resultados. **Ajustem a declaração ao uso real do grupo.** |

## 4. Antes de apresentar

- [ ] Trocar `[Integrante …]`, `[N]`, `[Instituição]` e `[link do repositório]` na capa e no slide 12.
- [ ] Ensaiar com cronômetro (meta: 14:30).
- [ ] Cada integrante ler a seção 3 inteira.
