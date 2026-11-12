# A2 – Achados dos experimentos (roteiro da seção de Resultados)

Fonte: `saida/a2/` gerado por `python main_a2.py` (validação cruzada aninhada estratificada 10×5, `random_state = 42`, 11.470 pacientes, 2.913 s de execução). Todos os números abaixo aparecem no artigo por macros de `artigo/numeros.tex`.

## 1. Qual modelo é melhor, e por quanto?

| Modelo | AUC-ROC | Recall | Especificidade | F1 | Acurácia bal. |
|---|---|---|---|---|---|
| Classe majoritária | 0,500 | 0,000 | 1,000 | 0,000 | 0,500 |
| Regressão Logística (baseline) | 0,787 ± 0,012 | 0,587 | 0,850 | 0,656 | 0,719 |
| Árvore de Decisão | 0,774 ± 0,018 | 0,572 | 0,846 | 0,643 | 0,709 |
| **Random Forest** | **0,802 ± 0,015** | 0,590 | 0,862 | 0,665 | 0,726 |
| Gradient Boosting | 0,801 ± 0,015 | 0,592 | 0,859 | 0,665 | 0,726 |

- A Random Forest é o melhor modelo complexo, com o Gradient Boosting praticamente empatado.
- O ganho sobre o baseline é **pequeno**: +0,015 de AUC e 0,7 ponto percentual de erro (26,3% → 25,6%).
- Hiperparâmetros mais escolhidos no laço interno: Regressão Logística C = 0,1; Random Forest com `max_depth = None`, `max_features = sqrt`, `min_samples_leaf = 5`.

## 2. A diferença é estatisticamente significativa?

Atualizado após a revisão: o teste F combinado de Alpaydin, que usa as 10 diferenças (o t usa só a primeira), também é significativo: **F = 5,58, p = 0,036**.

Sim. O teste t 5×2cv (Dietterich) entre Regressão Logística e Random Forest dá **t = 3,44 e p = 0,018 < 0,05**. Leitura: a vantagem da floresta é consistente entre partições, mas o tamanho do efeito é modesto. Para uma triagem, os dois modelos têm comportamento muito parecido; a floresta ganha em capacidade de ordenar pacientes por risco, não em uma mudança de patamar.

## 3. Quanto o SOPRO inflava o resultado?

| Cenário | AUC (RL / RF) | Recall (RL / RF) |
|---|---|---|
| Com SOPRO | 0,945 / 0,953 | 0,871 / 0,875 |
| Sem SOPRO (principal) | 0,787 / 0,802 | 0,587 / 0,590 |

O SOPRO sozinho eleva a AUC em cerca de 0,15. Sopro sistólico → 95,9% Anormal; sopro ausente → 10,1%. É um achado do exame do próprio cardiologista, registrado na mesma consulta que define o diagnóstico; um modelo que o usa estaria "lendo" a conclusão do médico, não prevendo. Por isso foi excluído.

## 4. Quanto o resultado depende dos MOTIVOs de encaminhamento (e da B2)?

Sem a B2 (outro achado de ausculta), a AUC fica em **0,772 (RL) e 0,788 (RF)**: perda pequena. Sem os MOTIVOs, cerca de 74% da discriminação acima do acaso ainda permanece (RF), então eles são os atributos mais importantes, mas não concentram "a maior parte" do sinal.

Sem SOPRO e sem MOTIVO1/MOTIVO2, a AUC cai para **0,697 (RL) e 0,722 (RF)**, e o recall para 0,41–0,45. Os motivos de encaminhamento são os atributos mais importantes (MOTIVO2 é o 1º e MOTIVO1 o 2º na importância por permutação da floresta). Eles são informação **anterior** à consulta (o que o médico que encaminhou suspeitou), então são legítimos para triagem, mas mostram que boa parte do sinal vem da suspeita clínica prévia, não de medidas objetivas.

## 5. Desbalanceamento e limiar

Desbalanceamento leve (57,3% / 42,7%). Nenhuma estratégia muda a AUC (a ordenação dos pacientes é a mesma); o que muda é onde o limiar 0,5 corta.

| Random Forest | Recall | Especificidade | F1 |
|---|---|---|---|
| Sem tratamento | 0,591 | 0,861 | 0,665 |
| Pesos por classe | 0,642 | 0,821 | 0,682 |
| SMOTE | 0,622 | 0,836 | 0,675 |
| Subamostragem | 0,653 | 0,809 | 0,684 |

Mover o limiar tem efeito maior e mais controlável (Random Forest, previsões fora da amostra):

| Limiar | Recall | Precisão | Falsos negativos | Falsos positivos |
|---|---|---|---|---|
| 0,50 | 0,590 | 0,761 | 2.008 | 905 |
| 0,40 | 0,688 | 0,694 | 1.528 | 1.487 |
| 0,30 | 0,826 | 0,589 | 853 | 2.814 |

Leitura clínica: em triagem, baixar o limiar para 0,30 reduz os doentes não detectados de 2.008 para 853 (−58%), ao custo de triplicar os falsos alarmes. A escolha do limiar é uma decisão clínica de custo, não estatística. A tabela é descritiva: não foi usada para escolher o modelo.

## 6. Que pacientes o modelo deixa passar?

Matriz de confusão da Random Forest (limiar 0,5): VN 5.671, FP 905, FN 2.008, VP 2.886, ou seja, 41% dos Anormais não são detectados.

| Grupo | n | Idade mediana | FC mediana | MOTIVO1 mais comum |
|---|---|---|---|---|
| VP | 2.886 | 1,1 ano | 100 | Suspeita de cardiopatia (66%) |
| FN | 2.008 | 4,6 anos | 92 | Parecer cardiológico (59%) |
| FP | 905 | 1,3 ano | 100 | Suspeita de cardiopatia (63%) |
| VN | 5.671 | 5,3 anos | 88 | Parecer cardiológico (67%) |

O modelo aprendeu o perfil "bebê encaminhado por suspeita de cardiopatia". Ele erra os Anormais mais velhos encaminhados para parecer de rotina (por exemplo, antes de cirurgia), cujo perfil nos atributos disponíveis é igual ao dos Normais. Os falsos positivos são o espelho: bebês com suspeita que se revelaram normais.

## 7. Atributos mais relevantes

- Importância por permutação (Random Forest, queda da AUC): MOTIVO2 0,075; MOTIVO1 0,038; B2 0,033; FC 0,023; HDA ausente 0,013; Idade 0,010.
- Razão de chances (Regressão Logística): B2 normal 0,18 (protege); MOTIVO2 "Sopro" 3,72; B2 hiperfonética 2,79; HDA ausente 0,48; MOTIVO1 "Cardiopatia já estabelecida" 1,81.
- B2 (segunda bulha) também é achado de exame, como o SOPRO, mas com associação bem menor (V = 0,24 contra 0,84). Fica no modelo principal; sem ela a AUC cai só para 0,788 (RF), e o modelo sem B2 é o recomendado para triagem estritamente pré-consulta.

## 8. Pacientes repetidos mudam a conclusão?

Não. Com partição agrupada por data de nascimento + sexo, a AUC é 0,788 (RL) e 0,801 (RF), igual à partição comum. Não há sinal de vazamento por repetição de pacientes.

## 9. Limitações

- Dados de um único serviço e de 2003–2010.
- PPA com 81,9% de ausentes e pressão arterial com 55,5%.
- B2 e MOTIVOs são informação próxima do julgamento clínico.
- Convênio com sinônimos não unificados (herdado da A1).
- O agrupamento por data de nascimento + sexo é uma aproximação: não há identificador real de paciente.
