# A2 – Modelagem e artigo IEEE (UCMF) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar a A2 completa até 18/11/2026: experimento reprodutível de classificação Normal × Anormal no UCMF, artigo curto no template IEEE (2 colunas, até 5 páginas), repositório público e apresentação de 15 minutos.

**Architecture:** O código da A1 (`src/p01`–`p05`) continua gerando `saida/UCMF_clean.csv`. A A2 acrescenta módulos `src/m01`–`m06` que partem do arquivo limpo e fazem **todo** o pré-processamento ajustável (imputação, padronização, codificação, reamostragem) dentro de um `Pipeline` do scikit-learn, reajustado em cada partição de treino. Os experimentos gravam CSV/JSON em `saida/a2/`; figuras, tabelas e números do artigo são gerados a partir desses arquivos, nunca digitados à mão.

**Tech Stack:** Python 3.13, pandas 2.2, scikit-learn 1.6, imbalanced-learn 0.14, scipy, matplotlib, pytest; artigo em LaTeX (`IEEEtran`, modo `conference`) compilado com Tectonic (alternativa: Overleaf).

**Spec:** `Descrição das avaliações.pdf`, seção "A2: Parte 2" e seus critérios de avaliação. Apoio metodológico: os quatro PDFs `slides - *.pdf` (Prof. Rogerio Salvini). Não há documento de design separado: as decisões estão na seção "Decisões" abaixo.

## Global Constraints

- Artigo no template de conferências da IEEE, **2 colunas e máximo de 5 páginas**.
- Resumo único de **100–150 palavras** com: problema, dataset, algoritmos comparados e principal resultado.
- Seções e orçamento de páginas: Cabeçalho e Resumo ~0,5; Introdução ~0,5; Dados e Análise Exploratória ~1 (com data leakage e 1 ou 2 gráficos); Metodologia ~1; Resultados e Discussão ~1,5; Conclusão e Referências ~0,5.
- **Pelo menos 2 algoritmos: um baseline simples e outro mais complexo.**
- O atributo que indica data leakage **deve ser excluído da análise**.
- Tabela comparativa de métricas, interpretação dos erros (matriz de confusão) e importância dos atributos.
- Ajustes básicos de hiperparâmetros; protocolo de validação correto; **nenhum vazamento de dados**.
- Link do repositório público (GitHub ou Colab) **no rodapé da primeira página**; código organizado; `random_state` fixado (`RANDOM_STATE = 42` em todo o projeto).
- Sem trechos de código e sem capturas de tela no artigo.
- Uso de IA generativa informado no artigo: qual, onde, como e para quê.
- Texto em português; número decimal com vírgula nas tabelas e figuras.
- Entrega **somente pelo SIGAA até 18/11/2026**; apresentação de **15 minutos** entre 18/11 e 27/11, com ênfase em metodologia e resultados; slides padronizados, numerados e com pouco texto.

## Decisões

Você pediu o plano sem perguntas, então estas escolhas são minhas. Cada uma pode ser trocada antes da execução.

| # | Decisão | Motivo |
|---|---|---|
| D1 | Tarefa: classificação binária; classe positiva = **Anormal** (patologia cardíaca) | É a variável-alvo do estudo de caso; em triagem, deixar de detectar um Anormal (falso negativo) é o erro mais caro |
| D2 | Atributo de leakage excluído: **SOPRO** | Na A1 teve V de Cramér = 0,84; sopro sistólico → 95,9% Anormal, ausente → 10,1%. Sozinho quase determina o alvo |
| D3 | Três cenários de atributos: `principal` (sem SOPRO), `com_sopro` (só para medir o tamanho do vazamento), `restrito` (sem SOPRO, MOTIVO1 e MOTIVO2) | MOTIVO1 "Cardiopatia já estabelecida" (71,3% Anormal) e MOTIVO2 "Sopro" (76,2%) carregam parte da mesma informação; o cenário restrito mostra quanto o resultado depende deles |
| D4 | Parte de `saida/UCMF_clean.csv`, **não** de `UCMF_transformed.csv` | O transformado da A1 ajustou mediana, média e desvio no conjunto inteiro, o que seria vazamento na validação |
| D5 | Mesmos atributos da A1: IDADE, IMC, PAS, PAD, FC, SEXO, Convenio, PULSOS, B2, MOTIVO1, MOTIVO2, PPA ordinal, 7 indicadores de sintoma (HDA 1 ∪ HDA2) e indicadores de ausência. ID, Atendimento, DN, Peso e Altura ficam de fora | Mantém coerência com o relatório da A1 já entregue |
| D6 | Modelos: DummyClassifier (piso), **Regressão Logística (baseline simples)**, Árvore de Decisão, **Random Forest** e **Gradient Boosting** (`HistGradientBoostingClassifier`) como complexos | Cobre o exigido (baseline + complexo) com modelos citados nas aulas, todos do scikit-learn |
| D7 | Validação: **validação cruzada aninhada** – externo `StratifiedKFold(10)`, interno `StratifiedKFold(5)` com `GridSearchCV` | N = 11.470 cai na faixa "Grande" da regra prática do professor (Stratified 10-Fold, 1 execução); o laço interno faz o ajuste de hiperparâmetros sem tocar no teste |
| D8 | Métrica de seleção no laço interno: AUC-ROC. Relatadas: acurácia, acurácia balanceada, precisão, recall (sensibilidade), especificidade, F1, AUC-ROC e AUC-PR, como média ± desvio-padrão dos 10 folds | Desbalanceamento leve (57,3% / 42,7%), caso em que a ROC é adequada; as demais mostram o custo em cada classe |
| D9 | Desbalanceamento: experimento principal sem tratamento; experimento à parte compara "nenhum", `class_weight="balanced"`, SMOTE e subamostragem aleatória, sempre dentro do pipeline; análise descritiva do limiar de decisão | Segue os níveis dos slides (decisão, algoritmo, dados) e a regra de reamostrar só o treino |
| D10 | Comparação estatística: **teste t 5×2cv de Dietterich** entre o baseline e o melhor modelo complexo, sobre a taxa de erro, α = 0,05 | É o teste indicado nos slides para dois modelos em um único dataset |
| D11 | Verificação de pacientes repetidos: repetir a avaliação com `StratifiedGroupKFold` agrupando por DN + SEXO | O ID é único por linha, mas 2.495 combinações DN + SEXO aparecem em mais de uma linha (6.111 linhas); se forem retornos do mesmo paciente, dividir entre treino e teste vaza informação |
| D12 | Importância dos atributos por **permutação** nos folds de teste, calculada sobre as colunas originais; coeficientes da Regressão Logística como razão de chances | Não fragmenta variáveis categóricas em dummies e vale para qualquer modelo |
| D13 | Artigo em LaTeX com `IEEEtran`; compilação local com Tectonic | O template LaTeX garante o formato "rigorosamente"; não há LaTeX instalado na máquina |

**O que só você ou o grupo pode confirmar** (não bloqueia a execução; cada item é um parâmetro isolado):

1. Qual atributo o professor apontou como leakage na A1. Se não for SOPRO, basta trocar `CENARIOS["principal"]` na Task 1.
2. Nomes completos dos integrantes, número do grupo e instituição, para o cabeçalho do artigo.
3. Se o `UCMF_raw.csv` pode ir para um repositório **público**. A Task 9 para e pergunta antes de publicar.
4. Conta e nome do repositório no GitHub.

## Review Focus

1. **Pré-processamento ajustado fora do treino** → métricas infladas sem erro visível. Teste: rótulos embaralhados devem dar AUC ≈ 0,5 e o padronizador deve guardar a média só do treino (Task 2 e Task 3).
2. **Categoria que aparece só no fold de teste** (Convenio e MOTIVO2 têm categorias raras) → o pipeline deve prever sem falhar (Task 2).
3. **Coluna numérica toda ausente num subconjunto de treino** (PPA tem 81,9% de ausentes; PAS, 55%) → o número de colunas de saída não pode mudar (Task 2).
4. **Mesmo paciente no treino e no teste** → a partição agrupada não pode dividir um grupo (Task 3).
5. **Número do artigo diferente do resultado real** por cópia manual ou por reexecução → os valores entram no LaTeX por macros geradas; rodar duas vezes deve produzir arquivos idênticos (Task 3 e Task 7).

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/config.py` (modificar) | Constantes da A2: `RANDOM_STATE`, `CENARIOS`, listas de colunas, `SINTOMAS`, caminhos `saida/a2/` |
| `src/m01_atributos.py` | Do CSV limpo para `X`, `y`, `grupos`; só operações linha a linha, sem nada ajustado |
| `src/m02_modelos.py` | Pré-processador, catálogo de modelos e grades, montagem do pipeline |
| `src/m03_validacao.py` | Métricas, validação aninhada, partição agrupada, teste 5×2cv |
| `src/m04_experimentos.py` | Executa os experimentos e grava os resultados em `saida/a2/` |
| `src/m05_interpretacao.py` | Matriz de confusão, limiar, importância, perfil dos erros |
| `src/m06_figuras_tabelas.py` | Figuras PDF, tabelas `.tex` e `numeros.tex` |
| `main_a2.py` | Orquestra limpeza (se faltar o CSV limpo) → m04 → m05 → m06 |
| `tests/test_m01.py` … `test_m06.py`, `tests/conftest.py` | Testes |
| `artigo/main.tex`, `artigo/refs.bib`, `artigo/tabelas/`, `artigo/figuras/`, `artigo/numeros.tex` | Artigo IEEE |
| `requirements.txt`, `README.md`, `.gitignore` | Reprodutibilidade |

## Cronograma

| Dia | Entregável |
|---|---|
| Qua 11/11 | Plano aprovado; Tasks 1 e 2 |
| Qui 12/11 | Tasks 3 e 4 |
| Sex 13/11 | Task 5 (execução completa) e Task 6 |
| Sáb 14/11 | Task 7 e primeira versão da Task 8 |
| Dom 15/11 | Artigo fechado (Task 8) e repositório público (Task 9) |
| Seg 16/11 | Slides e roteiro (Task 10); leitura do grupo |
| Ter 17/11 | Folga para correções; ensaio; **envio no SIGAA** (Task 11) |
| Qua 18/11 | Prazo final; apresentações podem começar neste dia |

---

### Task 1: Configuração da A2 e montagem dos atributos

**Files:**
- Modify: `src/config.py` (acrescentar bloco "A2" ao final)
- Create: `src/m01_atributos.py`, `tests/conftest.py`, `tests/test_m01.py`, `requirements.txt`, `.gitignore`

**Interfaces:**
- Consumes: `p03_bivariada.carregar_limpo() -> pd.DataFrame` (lê `saida/UCMF_clean.csv`); `config.ALVO`, `config.ORDEM_PPA`.
- Produces em `config.py`:
  - `RANDOM_STATE = 42`
  - `SAIDA_A2 = SAIDA / "a2"`, `FIGURAS_A2 = SAIDA_A2 / "figuras"`, `ARTIGO = RAIZ / "artigo"` (criados na importação)
  - `NUM_LOG = ["IMC", "PA SISTOLICA", "FC"]`, `NUM_LINEAR = ["IDADE", "PA DIASTOLICA"]`
  - `NOMINAIS = ["SEXO", "Convenio", "PULSOS", "B2", "SOPRO", "MOTIVO1", "MOTIVO2"]`
  - `SINTOMAS = ["Cianose", "Desmaio/tontura", "Dispneia", "Dor precordial", "Ganho de peso", "Outro", "Palpitação"]`
  - `CENARIOS = {"principal": ["SOPRO"], "com_sopro": [], "restrito": ["SOPRO", "MOTIVO1", "MOTIVO2"]}` (valor = colunas excluídas)
- Produces em `m01_atributos.py`:
  - `montar_atributos(df: pd.DataFrame, cenario: str = "principal") -> pd.DataFrame`
  - `carregar_xy(cenario: str = "principal") -> tuple[pd.DataFrame, pd.Series, pd.Series]` devolvendo `(X, y, grupos)`; `y` é 1 para Anormal; `grupos` é `DN + "|" + SEXO`, e a linha sem DN recebe um grupo próprio (`"linha_<índice>"`).

`montar_atributos` cria `sint_<slug>` (1 se o sintoma está em HDA 1 ou HDA2), `hda_ausente`, `ppa_ord` (posição em `ORDEM_PPA`, ausente = 0) e `ppa_ausente`; remove `ID`, `Atendimento`, `DN`, `Peso`, `Altura`, `HDA 1`, `HDA2`, `PPA`, o alvo e as colunas do cenário. Não imputa, não padroniza e não codifica as demais colunas.

- [ ] **Step 1: Escrever os testes que falham** em `tests/test_m01.py` (o `conftest.py` põe `src/` no `sys.path`)

```python
def test_dimensoes_e_alvo():
    X, y, grupos = carregar_xy("principal")
    assert len(X) == len(y) == len(grupos) == 11470
    assert set(y.unique()) == {0, 1}
    assert int(y.sum()) == 4894

def test_cenario_principal_exclui_sopro_e_identificadores():
    X, _, _ = carregar_xy("principal")
    proibidas = {"SOPRO", "ID", "Atendimento", "DN", "Peso", "Altura",
                 "HDA 1", "HDA2", "PPA", "NORMAL X ANORMAL"}
    assert proibidas.isdisjoint(X.columns)

def test_cenarios_diferem_so_nas_colunas_excluidas():
    p, c, r = (set(carregar_xy(k)[0].columns) for k in ("principal", "com_sopro", "restrito"))
    assert c - p == {"SOPRO"}
    assert p - r == {"MOTIVO1", "MOTIVO2"}

def test_atributos_derivados():
    X, _, _ = carregar_xy("principal")
    assert sum(col.startswith("sint_") for col in X.columns) == 7
    assert set(X["ppa_ord"].unique()) <= {0, 1, 2, 3}
    assert X["ppa_ausente"].mean() == pytest.approx(0.819, abs=0.002)

def test_nada_e_imputado_aqui():
    X, _, _ = carregar_xy("principal")
    assert X["IMC"].isna().sum() > 0

def test_grupos_sem_dn_sao_unicos():
    _, _, grupos = carregar_xy("principal")
    sem_dn = grupos[grupos.str.startswith("linha_")]
    assert sem_dn.is_unique and len(sem_dn) == 587
```

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m01.py -v` → FAIL com `ModuleNotFoundError: m01_atributos`.
- [ ] **Step 3: Implementar** o bloco A2 em `config.py` e as duas funções em `m01_atributos.py`; criar `requirements.txt` com as versões instaladas (`pandas`, `numpy`, `scikit-learn`, `imbalanced-learn`, `scipy`, `matplotlib`, `pytest`) e `.gitignore` (`__pycache__/`, `.pytest_cache/`, `artigo/*.aux`, `artigo/*.log`).
- [ ] **Step 4: Rodar e ver passar** – `python -m pytest tests/test_m01.py -v` → 6 passed.
- [ ] **Step 5: Commit** – `git init` (o diretório ainda não é um repositório), depois `git add` do código existente e do novo, `git commit -m "feat(a2): configuração e montagem dos atributos"`. **Não** adicionar `UCMF_raw.csv` nem `saida/UCMF_*.csv` até a decisão da Task 9.

---

### Task 2: Pré-processador e pipelines dos modelos

**Files:**
- Create: `src/m02_modelos.py`, `tests/test_m02.py`

**Interfaces:**
- Consumes: `carregar_xy`, `NUM_LOG`, `NUM_LINEAR`, `NOMINAIS`, `RANDOM_STATE`.
- Produces:
  - `montar_preprocessador(X: pd.DataFrame) -> ColumnTransformer`
  - `MODELOS: dict[str, tuple[BaseEstimator, dict]]` com as chaves `"dummy"`, `"logreg"`, `"arvore"`, `"rf"`, `"gb"`; o dicionário de grade usa o prefixo `modelo__`
  - `ROTULOS = {"dummy": "Classe majoritária", "logreg": "Regressão Logística", "arvore": "Árvore de Decisão", "rf": "Random Forest", "gb": "Gradient Boosting"}`
  - `montar_pipeline(nome: str, X: pd.DataFrame, estrategia: str = "nenhum") -> Pipeline` com passos nomeados `"prep"`, `"amostra"` (só quando houver reamostragem) e `"modelo"`; `estrategia` ∈ `{"nenhum", "class_weight", "smote", "subamostragem"}`

Pré-processador, só com as colunas presentes em `X`:

| Grupo | Colunas | Passos |
|---|---|---|
| Numéricas com log | `NUM_LOG` | `FunctionTransformer(np.log1p)` → `SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)` → `StandardScaler()` |
| Numéricas lineares | `NUM_LINEAR` | mesmo, sem o log |
| Nominais | `NOMINAIS` ∩ colunas de `X` | `SimpleImputer(strategy="constant", fill_value="Nao informado")` → `OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=30, sparse_output=False)` |
| Demais (`sint_*`, `hda_ausente`, `ppa_ord`, `ppa_ausente`) | restante | `passthrough` |

Modelos e grades (todos com `random_state=RANDOM_STATE` quando existir):

| Chave | Estimador | Grade |
|---|---|---|
| `dummy` | `DummyClassifier(strategy="most_frequent")` | `{}` |
| `logreg` | `LogisticRegression(max_iter=2000)` | `C`: 0,01; 0,1; 1; 10 |
| `arvore` | `DecisionTreeClassifier()` | `max_depth`: 3, 5, 7, 10, None; `min_samples_leaf`: 1, 10, 50 |
| `rf` | `RandomForestClassifier(n_estimators=300, n_jobs=-1)` | `max_depth`: None, 10, 20; `min_samples_leaf`: 1, 5; `max_features`: "sqrt", 0,3 |
| `gb` | `HistGradientBoostingClassifier(max_iter=200)` | `learning_rate`: 0,05; 0,1; `max_depth`: 3, 6, None; `l2_regularization`: 0, 1 |

Estratégias: `class_weight` define `class_weight="balanced"` no estimador (no `dummy`, não faz nada); `smote` insere `SMOTE(random_state=RANDOM_STATE)` e `subamostragem` insere `RandomUnderSampler(random_state=RANDOM_STATE)` depois de `prep`, usando `imblearn.pipeline.Pipeline`.

- [ ] **Step 1: Escrever os testes que falham**

```python
def test_padronizador_usa_so_o_treino(xy):
    X, y, _ = xy
    tr, te = X.iloc[:8000], X.iloc[8000:]
    pipe = montar_pipeline("logreg", X).fit(tr, y.iloc[:8000])
    media = pipe.named_steps["prep"].named_transformers_["num_linear"].named_steps["padroniza"].mean_[0]
    assert media == pytest.approx(tr["IDADE"].fillna(tr["IDADE"].median()).mean())
    assert media != pytest.approx(X["IDADE"].fillna(X["IDADE"].median()).mean())

def test_categoria_inedita_no_teste_nao_quebra(xy):
    X, y, _ = xy
    pipe = montar_pipeline("logreg", X).fit(X.iloc[:2000], y.iloc[:2000])
    novo = X.iloc[2000:2005].copy()
    novo["Convenio"] = "CONVENIO NUNCA VISTO"
    assert pipe.predict_proba(novo).shape == (5, 2)

def test_coluna_toda_ausente_no_treino_mantem_largura(xy):
    X, y, _ = xy
    tr = X.iloc[:2000].copy()
    tr["PA SISTOLICA"] = np.nan
    larg_a = montar_pipeline("logreg", X).fit(tr, y.iloc[:2000])[:-1].transform(X.iloc[2000:2010]).shape[1]
    larg_b = montar_pipeline("logreg", X).fit(X.iloc[:2000], y.iloc[:2000])[:-1].transform(X.iloc[2000:2010]).shape[1]
    assert larg_a == larg_b

def test_reamostragem_so_no_ajuste(xy):
    X, y, _ = xy
    pipe = montar_pipeline("logreg", X, estrategia="smote").fit(X.iloc[:2000], y.iloc[:2000])
    assert len(pipe.predict(X.iloc[2000:2500])) == 500

@pytest.mark.parametrize("nome", ["dummy", "logreg", "arvore", "rf", "gb"])
def test_todos_os_modelos_ajustam_e_grade_e_valida(xy, nome):
    X, y, _ = xy
    pipe = montar_pipeline(nome, X)
    assert set(MODELOS[nome][1]) <= set(pipe.get_params())
    pipe.fit(X.iloc[:1500], y.iloc[:1500])

def test_cenario_restrito_monta_sem_motivos():
    X, y, _ = carregar_xy("restrito")
    montar_pipeline("logreg", X).fit(X.iloc[:1500], y.iloc[:1500])
```

A fixture `xy` (em `conftest.py`, escopo de sessão) devolve `carregar_xy("principal")` embaralhado com `sample(frac=1, random_state=42)`. Os transformadores do `ColumnTransformer` se chamam `"num_log"`, `"num_linear"`, `"nominais"`; os passos internos, `"log"`, `"imputa"`, `"padroniza"`, `"codifica"`.

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m02.py -v` → FAIL (`ModuleNotFoundError`).
- [ ] **Step 3: Implementar** `m02_modelos.py` conforme as duas tabelas acima.
- [ ] **Step 4: Rodar e ver passar** – `python -m pytest tests/test_m02.py -v` → 10 passed.
- [ ] **Step 5: Commit** – `git commit -m "feat(a2): pré-processador e pipelines dos modelos"`.

---

### Task 3: Métricas, validação aninhada e partição agrupada

**Files:**
- Create: `src/m03_validacao.py`, `tests/test_m03.py`

**Interfaces:**
- Consumes: `montar_pipeline`, `MODELOS`, `RANDOM_STATE`.
- Produces:
  - `METRICAS = ["acuracia", "acuracia_bal", "precisao", "recall", "especificidade", "f1", "auc_roc", "auc_pr"]`
  - `calcular_metricas(y_true, proba, limiar: float = 0.5) -> dict[str, float]` (chaves = `METRICAS`; `precisao` com `zero_division=0`)
  - `particoes(y, grupos=None, n_splits: int = 10) -> list[tuple[np.ndarray, np.ndarray]]` – `StratifiedKFold(shuffle=True, random_state=RANDOM_STATE)`, ou `StratifiedGroupKFold` com os mesmos argumentos quando `grupos` é dado
  - `validacao_aninhada(nome, X, y, *, estrategia="nenhum", grupos=None, n_externo=10, n_interno=5, params_fixos: dict | None = None, importancia=False) -> ResultadoCV`
  - `ResultadoCV` (dataclass): `metricas: pd.DataFrame` (uma linha por fold, colunas `fold` + `METRICAS`), `oof: pd.DataFrame` (`indice`, `fold`, `y`, `proba`), `params: list[dict]` (melhor combinação por fold), `importancia: pd.DataFrame | None` (`fold`, `atributo`, `queda_auc`)

Regras: o laço interno é `GridSearchCV(scoring="roc_auc", cv=StratifiedKFold(n_interno, shuffle=True, random_state=RANDOM_STATE), n_jobs=-1, refit=True)`; se a grade for vazia ou `params_fixos` for dado, ajusta o pipeline direto. Com `importancia=True`, calcula `permutation_importance(melhor, X_teste, y_teste, scoring="roc_auc", n_repeats=5, random_state=RANDOM_STATE)` em cada fold externo, sobre as colunas originais de `X`.

- [ ] **Step 1: Escrever os testes que falham** (usam `X.iloc[:1200]`, `n_externo=3`, `n_interno=2` para rodar em segundos)

```python
def test_metricas_em_caso_conhecido():
    m = calcular_metricas(np.array([1, 1, 1, 0, 0, 0, 0, 0]),
                          np.array([.9, .8, .2, .7, .1, .1, .1, .1]))
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["especificidade"] == pytest.approx(4 / 5)
    assert m["precisao"] == pytest.approx(2 / 3)
    assert m["acuracia_bal"] == pytest.approx((2 / 3 + 4 / 5) / 2)

def test_particoes_estratificadas_e_disjuntas(xy):
    _, y, _ = xy
    ps = particoes(y)
    assert len(ps) == 10
    assert sorted(np.concatenate([te for _, te in ps])) == list(range(len(y)))
    for _, te in ps:
        assert y.iloc[te].mean() == pytest.approx(y.mean(), abs=0.01)

def test_particao_agrupada_nao_divide_grupo(xy):
    _, y, grupos = xy
    for tr, te in particoes(y, grupos=grupos):
        assert set(grupos.iloc[tr]).isdisjoint(grupos.iloc[te])

def test_cada_instancia_avaliada_uma_vez(amostra):
    X, y = amostra
    r = validacao_aninhada("logreg", X, y, n_externo=3, n_interno=2)
    assert len(r.metricas) == 3 and len(r.params) == 3
    assert sorted(r.oof["indice"]) == list(range(len(y)))

def test_execucao_e_deterministica(amostra):
    X, y = amostra
    a = validacao_aninhada("rf", X, y, n_externo=3, n_interno=2, params_fixos={})
    b = validacao_aninhada("rf", X, y, n_externo=3, n_interno=2, params_fixos={})
    pd.testing.assert_frame_equal(a.metricas, b.metricas)

def test_rotulos_embaralhados_dao_auc_de_acaso(amostra):
    X, y = amostra
    y_emb = pd.Series(np.random.default_rng(42).permutation(y.to_numpy()), index=y.index)
    r = validacao_aninhada("logreg", X, y_emb, n_externo=3, n_interno=2)
    assert 0.42 < r.metricas["auc_roc"].mean() < 0.58

def test_dummy_tem_auc_meio(amostra):
    X, y = amostra
    assert validacao_aninhada("dummy", X, y, n_externo=3).metricas["auc_roc"].mean() == pytest.approx(0.5)

def test_importancia_usa_colunas_originais(amostra):
    X, y = amostra
    r = validacao_aninhada("logreg", X, y, n_externo=3, n_interno=2, importancia=True)
    assert set(r.importancia["atributo"]) == set(X.columns)
```

A fixture `amostra` devolve `(X.iloc[:1200], y.iloc[:1200])` da fixture `xy`.

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m03.py -v` → FAIL.
- [ ] **Step 3: Implementar** `m03_validacao.py`.
- [ ] **Step 4: Rodar e ver passar** – `python -m pytest tests/test_m03.py -v` → 8 passed.
- [ ] **Step 5: Commit** – `git commit -m "feat(a2): validação aninhada, métricas e partição agrupada"`.

---

### Task 4: Teste t 5×2cv de Dietterich

**Files:**
- Modify: `src/m03_validacao.py`
- Test: `tests/test_m03.py`

**Interfaces:**
- Produces:
  - `estatistica_5x2cv(diferencas: np.ndarray) -> tuple[float, float]` – recebe matriz 5×2 com `p_i^(j) = erro_A − erro_B` e devolve `(t, p_bicaudal)` com 5 graus de liberdade
  - `teste_5x2cv(nome_a: str, nome_b: str, X, y, n_interno: int = 3) -> dict` com chaves `"t"`, `"p"`, `"diferencas"` (lista 5×2), `"erro_a"`, `"erro_b"` (médias das 10 execuções)

Fórmula (slides "Comparação de modelos", p. 35–36): para cada replicação `i`, `p̄_i = (p_i^(1) + p_i^(2)) / 2` e `s_i² = (p_i^(1) − p̄_i)² + (p_i^(2) − p̄_i)²`; `t = p_1^(1) / sqrt((1/5) · Σ s_i²)`. O numerador é só a diferença da primeira replicação no primeiro fold. Valor crítico para α = 0,05: 2,571.

`teste_5x2cv` usa, na replicação `i`, `StratifiedKFold(n_splits=2, shuffle=True, random_state=RANDOM_STATE + i)`; os dois modelos recebem as mesmas partições e cada um é um `GridSearchCV` (laço interno de `n_interno` folds, `scoring="roc_auc"`), de modo que o ajuste de hiperparâmetros também fica dentro do treino.

- [ ] **Step 1: Escrever os testes que falham**

```python
def test_estatistica_5x2cv_exemplo_calculado_a_mao():
    d = np.array([[.02, .01], [.03, .01], [.01, .02], [.02, .02], [.03, .02]])
    t, p = estatistica_5x2cv(d)
    assert t == pytest.approx(2.3905, abs=1e-3)
    assert 0.05 < p < 0.10

def test_estatistica_5x2cv_sem_variancia_nao_divide_por_zero():
    t, p = estatistica_5x2cv(np.zeros((5, 2)))
    assert t == 0.0 and p == 1.0

def test_teste_5x2cv_modelo_contra_si_mesmo(amostra):
    X, y = amostra
    r = teste_5x2cv("logreg", "logreg", X, y, n_interno=2)
    assert r["t"] == 0.0 and np.allclose(r["diferencas"], 0)
```

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m03.py -k 5x2cv -v` → FAIL.
- [ ] **Step 3: Implementar** as duas funções.
- [ ] **Step 4: Rodar e ver passar** – 3 passed.
- [ ] **Step 5: Commit** – `git commit -m "feat(a2): teste t 5x2cv"`.

---

### Task 5: Execução dos experimentos

**Files:**
- Create: `src/m04_experimentos.py`, `main_a2.py`, `tests/test_m04.py`

**Interfaces:**
- Consumes: `carregar_xy`, `validacao_aninhada`, `teste_5x2cv`, `MODELOS`, `CENARIOS`, `SAIDA_A2`.
- Produces: `executar(n_amostra: int | None = None, n_externo: int = 10, n_interno: int = 5, destino: Path = SAIDA_A2) -> None`, que grava:

| Arquivo | Conteúdo |
|---|---|
| `metricas_cv.csv` | `experimento`, `cenario`, `modelo`, `estrategia`, `fold` + `METRICAS` |
| `oof.csv` | `experimento`, `cenario`, `modelo`, `estrategia`, `indice`, `fold`, `y`, `proba` |
| `melhores_params.json` | `{cenario: {modelo: {"por_fold": [...], "moda": {...}}}}` |
| `importancia.csv` | `modelo`, `fold`, `atributo`, `queda_auc` (cenário principal) |
| `teste_5x2cv.json` | saída de `teste_5x2cv` + nomes dos dois modelos |
| `resumo.json` | `melhor_complexo`, tempo de execução, versões das bibliotecas, `RANDOM_STATE` |

Experimentos, nesta ordem (coluna `experimento`):

1. `principal` – cenário `principal`, os cinco modelos, validação aninhada 10×5, `importancia=True` para `logreg` e para os complexos. Define `melhor_complexo` = maior AUC-ROC média entre `arvore`, `rf` e `gb`.
2. `cenarios` – cenários `com_sopro` e `restrito`, só `logreg` e `melhor_complexo`, validação aninhada 10×5.
3. `desbalanceamento` – cenário `principal`, `logreg` e `melhor_complexo`, as quatro estratégias, com `params_fixos` = moda dos melhores parâmetros do experimento 1.
4. `agrupado` – cenário `principal`, `logreg` e `melhor_complexo`, `grupos` informados, `params_fixos` = mesma moda.
5. `5x2cv` – `teste_5x2cv("logreg", melhor_complexo, X, y)`.

`main_a2.py` executa `p02_limpeza.executar()` se `saida/UCMF_clean.csv` não existir, depois `m04`, `m05` e `m06`. Com `n_amostra`, usa uma subamostra estratificada (para os testes).

- [ ] **Step 1: Escrever o teste que falha** (execução reduzida em diretório temporário)

```python
def test_execucao_reduzida_gera_todos_os_arquivos(tmp_path):
    executar(n_amostra=900, n_externo=3, n_interno=2, destino=tmp_path)
    for nome in ["metricas_cv.csv", "oof.csv", "melhores_params.json",
                 "importancia.csv", "teste_5x2cv.json", "resumo.json"]:
        assert (tmp_path / nome).exists()
    m = pd.read_csv(tmp_path / "metricas_cv.csv")
    assert set(m["experimento"]) == {"principal", "cenarios", "desbalanceamento", "agrupado"}
    principal = m[m["experimento"] == "principal"]
    assert set(principal["modelo"]) == {"dummy", "logreg", "arvore", "rf", "gb"}
    assert set(m.loc[m["experimento"] == "desbalanceamento", "estrategia"]) == {
        "nenhum", "class_weight", "smote", "subamostragem"}
    assert json.loads((tmp_path / "resumo.json").read_text())["melhor_complexo"] in {"arvore", "rf", "gb"}

def test_execucao_reduzida_e_reprodutivel(tmp_path):
    executar(n_amostra=900, n_externo=3, n_interno=2, destino=tmp_path / "a")
    executar(n_amostra=900, n_externo=3, n_interno=2, destino=tmp_path / "b")
    pd.testing.assert_frame_equal(pd.read_csv(tmp_path / "a" / "metricas_cv.csv"),
                                  pd.read_csv(tmp_path / "b" / "metricas_cv.csv"))
```

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m04.py -v` → FAIL.
- [ ] **Step 3: Implementar** `m04_experimentos.py` e `main_a2.py`.
- [ ] **Step 4: Rodar e ver passar** – 2 passed.
- [ ] **Step 5: Execução completa** – `python src/m04_experimentos.py` (estimativa: 40 a 90 minutos; rodar em segundo plano). Conferir depois, com um script curto, e **registrar os valores observados**:
  - `dummy` no experimento principal: AUC-ROC = 0,5 e acurácia ≈ 0,573;
  - nos dois modelos, AUC-ROC de `com_sopro` > `principal` ≥ `restrito`;
  - desvio-padrão da AUC-ROC entre folds menor que 0,03 para todos os modelos;
  - se a AUC-ROC do cenário `principal` passar de 0,95, **parar e investigar** outro atributo que vaze antes de seguir.
- [ ] **Step 6: Commit** – `git add src main_a2.py tests saida/a2 && git commit -m "feat(a2): experimentos e resultados"`.

---

### Task 6: Interpretação dos resultados

**Files:**
- Create: `src/m05_interpretacao.py`, `tests/test_m05.py`

**Interfaces:**
- Consumes: os arquivos de `saida/a2/` da Task 5; `carregar_xy`; `calcular_metricas`.
- Produces: `executar(origem: Path = SAIDA_A2) -> None`, que grava em `origem`:

| Arquivo | Conteúdo |
|---|---|
| `resumo_metricas.csv` | média e desvio-padrão por `experimento`, `cenario`, `modelo`, `estrategia` |
| `confusao.csv` | `modelo`, `vn`, `fp`, `fn`, `vp` – previsões fora da amostra (OOF) somadas, limiar 0,5, para `logreg` e `melhor_complexo` |
| `limiar.csv` | para `melhor_complexo`: limiar de 0,20 a 0,80 em passos de 0,05, com `recall`, `precisao`, `especificidade`, `f1`, `fn`, `fp` |
| `importancia_resumo.csv` | `modelo`, `atributo`, `queda_auc_media`, `queda_auc_dp`, em ordem decrescente |
| `razao_chances.csv` | Regressão Logística ajustada no conjunto inteiro com os parâmetros da moda: `termo`, `coeficiente`, `razao_chances` (os 10 maiores em módulo) |
| `perfil_erros.csv` | para `melhor_complexo`: mediana de IDADE e FC e distribuição de MOTIVO1 e de `hda_ausente` em cada grupo VP, FN, FP, VN |

A tabela de limiar é **descritiva**: mostra o compromisso entre sensibilidade e precisão e não é usada para escolher modelo nem para relatar desempenho final.

- [ ] **Step 1: Escrever os testes que falham** (reusam a execução reduzida da Task 5 por uma fixture de sessão `saida_reduzida`)

```python
def test_confusao_soma_o_total(saida_reduzida):
    c = pd.read_csv(saida_reduzida / "confusao.csv")
    assert (c[["vn", "fp", "fn", "vp"]].sum(axis=1) == 900).all()

def test_limiar_monotono(saida_reduzida):
    l = pd.read_csv(saida_reduzida / "limiar.csv").sort_values("limiar")
    assert l["recall"].is_monotonic_decreasing and l["fn"].is_monotonic_increasing
    assert len(l) == 13

def test_resumo_tem_uma_linha_por_combinacao(saida_reduzida):
    r = pd.read_csv(saida_reduzida / "resumo_metricas.csv")
    assert not r.duplicated(["experimento", "cenario", "modelo", "estrategia"]).any()
    assert {"auc_roc_media", "auc_roc_dp", "recall_media", "f1_media"} <= set(r.columns)

def test_perfil_de_erros_tem_os_quatro_grupos(saida_reduzida):
    assert set(pd.read_csv(saida_reduzida / "perfil_erros.csv")["grupo"]) == {"VP", "FN", "FP", "VN"}
```

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m05.py -v` → FAIL.
- [ ] **Step 3: Implementar** `m05_interpretacao.py`.
- [ ] **Step 4: Rodar e ver passar** – 4 passed; depois `python src/m05_interpretacao.py` sobre os resultados completos.
- [ ] **Step 5: Ler os resultados e anotar em `docs/a2_achados.md`**, com os valores reais, as respostas a: qual modelo é melhor e por quanto; a diferença é significativa pelo 5×2cv; quanto o SOPRO inflava o resultado; quanto os MOTIVOs sustentam o resultado; qual estratégia de desbalanceamento muda o recall e a que custo; que perfil de paciente Anormal o modelo deixa passar; se a avaliação agrupada muda a conclusão. Este arquivo é o roteiro da seção de Resultados.
- [ ] **Step 6: Commit** – `git commit -m "feat(a2): interpretação dos resultados"`.

---

### Task 7: Figuras, tabelas e números do artigo

**Files:**
- Create: `src/m06_figuras_tabelas.py`, `tests/test_m06.py`

**Interfaces:**
- Consumes: arquivos de `saida/a2/`; `saida/tabelas/tab_associacao_alvo.csv` (A1); estilo matplotlib e cores de `config.py` (`COR_NORMAL`, `COR_ANORMAL`).
- Produces: `executar(origem: Path = SAIDA_A2, destino: Path = ARTIGO) -> None`, que grava:

| Arquivo | Conteúdo |
|---|---|
| `figuras/fig1_leakage.pdf` | 2 painéis: (a) % de Anormal por categoria de SOPRO; (b) associação de cada atributo com o alvo (V de Cramér ou \|r\|), com SOPRO destacado |
| `figuras/fig2_curvas.pdf` | 2 painéis: curvas ROC e Precision–Recall (OOF) dos modelos do cenário principal; linha de referência do acaso |
| `figuras/fig3_erros_importancia.pdf` | 2 painéis: (a) matriz de confusão do melhor modelo, com contagem e % por linha; (b) 10 atributos mais importantes por permutação, com barra de erro |
| `tabelas/tab_dados.tex` | instâncias, atributos, % por classe, % de ausentes das variáveis principais |
| `tabelas/tab_modelos.tex` | modelos × métricas, média ± desvio-padrão, melhor valor de cada coluna em negrito |
| `tabelas/tab_ablacao.tex` | cenários (com SOPRO, principal, restrito) e estratégias de desbalanceamento para baseline e melhor modelo: AUC-ROC, recall, F1 |
| `numeros.tex` | um `\newcommand` por número citado no texto (ex.: `\aucMelhor`, `\recallMelhor`, `\tCincoDois`, `\pCincoDois`, `\nInstancias`) |

Figuras em largura de uma coluna IEEE (3,5 pol), fonte ≥ 7 pt, vetoriais, legíveis em preto e branco (marcadores ou hachuras além da cor). Decimais com vírgula.

- [ ] **Step 1: Escrever os testes que falham**

```python
def test_gera_todos_os_artefatos(saida_reduzida, tmp_path):
    executar(origem=saida_reduzida, destino=tmp_path)
    for rel in ["figuras/fig1_leakage.pdf", "figuras/fig2_curvas.pdf",
                "figuras/fig3_erros_importancia.pdf", "tabelas/tab_dados.tex",
                "tabelas/tab_modelos.tex", "tabelas/tab_ablacao.tex", "numeros.tex"]:
        assert (tmp_path / rel).stat().st_size > 0

def test_numeros_batem_com_o_resumo(saida_reduzida, tmp_path):
    executar(origem=saida_reduzida, destino=tmp_path)
    resumo = pd.read_csv(saida_reduzida / "resumo_metricas.csv")
    melhor = json.loads((saida_reduzida / "resumo.json").read_text())["melhor_complexo"]
    auc = resumo.query("experimento == 'principal' and modelo == @melhor")["auc_roc_media"].iloc[0]
    assert f"\\newcommand{{\\aucMelhor}}{{{auc:.3f}".replace(".", ",") in (tmp_path / "numeros.tex").read_text(encoding="utf-8")

def test_tabela_de_modelos_usa_virgula_e_tem_cinco_linhas(saida_reduzida, tmp_path):
    executar(origem=saida_reduzida, destino=tmp_path)
    tex = (tmp_path / "tabelas/tab_modelos.tex").read_text(encoding="utf-8")
    assert tex.count("\\\\") >= 6 and "0." not in tex
```

- [ ] **Step 2: Rodar e ver falhar** – `python -m pytest tests/test_m06.py -v` → FAIL.
- [ ] **Step 3: Implementar** `m06_figuras_tabelas.py`.
- [ ] **Step 4: Rodar e ver passar** – 3 passed; depois `python main_a2.py` de ponta a ponta e `python -m pytest -q` com a suíte toda verde.
- [ ] **Step 5: Abrir as três figuras** (converter para PNG e olhar) e conferir: rótulos legíveis, nada cortado, cores distinguíveis.
- [ ] **Step 6: Commit** – `git commit -m "feat(a2): figuras, tabelas e números do artigo"`.

---

### Task 8: Artigo no template IEEE

**Files:**
- Create: `artigo/main.tex`, `artigo/refs.bib`

**Interfaces:**
- Consumes: `artigo/numeros.tex`, `artigo/tabelas/*.tex`, `artigo/figuras/*.pdf`, `docs/a2_achados.md`.
- Produces: `artigo/main.pdf` (≤ 5 páginas).

Formato: `\documentclass[conference]{IEEEtran}`, `\usepackage[brazil]{babel}`, `\input{numeros}`; tabelas com `\input{tabelas/...}`; **nenhum número de resultado digitado à mão** – todos por macro. Link do repositório em `\thanks{}` preso ao título, para sair no rodapé da primeira página (URL definitiva entra na Task 9).

Conteúdo por seção:

| Seção | O que precisa estar escrito |
|---|---|
| Título, autores, Resumo (100–150 palavras) | Problema (triagem de patologia cardíaca pediátrica), dataset (UCMF, 11.470 registros após limpeza), algoritmos comparados, principal resultado com número e a ressalva do leakage |
| I. Introdução | Contexto clínico e por que triar; objetivo: classificação binária Normal × Anormal; relevância; contribuição em uma frase |
| II. Dados e Análise Exploratória | Origem (estudo de caso da disciplina, cardiologia pediátrica, 0–19 anos); 12.873 → 11.470 instâncias; atributos; alvo 57,3% / 42,7%; ausências relevantes (PPA 81,9%); **data leakage**: evidência do SOPRO (Fig. 1), decisão de excluir, e o papel dos MOTIVOs; Tab. I |
| III. Metodologia | Limpeza (resumo das 34 regras da A1, com a lógica de plausibilidade); transformações dentro do pipeline e por que só no treino; protocolo: validação aninhada 10×5 estratificada e justificativa pelo tamanho da base; métricas e por que recall importa; modelos e grades; estratégias de desbalanceamento; teste 5×2cv; verificação agrupada |
| IV. Resultados e Discussão | Tab. II e leitura crítica (ganho do modelo complexo sobre o baseline e se é significativo); Fig. 2; efeito do leakage e do cenário restrito (Tab. III); desbalanceamento e limiar em termos de falsos negativos por 1.000 pacientes; matriz de confusão e perfil dos erros (Fig. 3a); atributos mais importantes e sentido clínico (Fig. 3b); o que isso significa para uso em triagem |
| V. Conclusão | Resposta ao objetivo; limitações reais (dados de um único serviço e de 2003–2010; PPA quase toda ausente; possível repetição de pacientes; Convenio com sinônimos; B2 e MOTIVOs como informação próxima do diagnóstico); trabalhos futuros |
| Declaração de uso de IA | Qual ferramenta, onde, como e para quê; o grupo revisa e ajusta o texto para refletir o uso real |
| Referências | Dietterich (1998); Kohavi (1995); Chawla et al. (2002, SMOTE); Breiman (2001); Friedman (2001) ou Ke et al. (2017); Pedregosa et al. (2011, scikit-learn); Lemaître et al. (2017, imbalanced-learn); Flynn et al. (2017); OMS (2006/2007); Fleming et al. (2011) |

- [ ] **Step 1: Instalar o compilador** – `winget install TectonicProject.Tectonic` e conferir `tectonic --version`. Se não instalar, usar o Overleaf com o projeto "IEEE Conference Template" e enviar a pasta `artigo/`.
- [ ] **Step 2: Escrever `refs.bib` e o esqueleto de `main.tex`** com todas as seções vazias, as três figuras e as três tabelas posicionadas; compilar com `tectonic artigo/main.tex` → gera `main.pdf` sem erro.
- [ ] **Step 3: Escrever o texto** seção por seção a partir de `docs/a2_achados.md`, em linguagem científica objetiva, interpretando cada número no contexto clínico.
- [ ] **Step 4: Verificar os requisitos**, um comando ou conferência por item:
  - páginas: `python -c "from pypdf import PdfReader; print(len(PdfReader('artigo/main.pdf').pages))"` → ≤ 5;
  - resumo: contar as palavras do ambiente `abstract` → entre 100 e 150;
  - `grep -nE "\\\\begin\{(verbatim|lstlisting|minted)\}" artigo/main.tex` → nenhuma ocorrência;
  - `grep -nE "0[.,][0-9]{2,}" artigo/main.tex` → nenhuma métrica digitada à mão (só macros);
  - log da compilação sem "undefined reference" nem "Overfull \hbox" acima de 5 pt;
  - rodapé da primeira página com o link; declaração de IA presente; todas as referências citadas no texto.
- [ ] **Step 5: Ler o PDF página por página** (converter para imagem) e corrigir figura ilegível, tabela estourando a coluna ou seção fora do orçamento de páginas.
- [ ] **Step 6: Commit** – `git commit -m "docs(a2): artigo IEEE"`.

---

### Task 9: Repositório público e reprodutibilidade

**Files:**
- Create: `README.md`
- Modify: `artigo/main.tex` (URL no `\thanks`)

- [ ] **Step 1: PARAR e confirmar com o usuário** três coisas: conta e nome do repositório; se `UCMF_raw.csv` pode ser publicado; nomes dos integrantes. Publicar é visível a terceiros e não se desfaz bem.
- [ ] **Step 2: Escrever o `README.md`**: objetivo; estrutura de pastas; como reproduzir (`pip install -r requirements.txt`, depois `python main.py` para a A1 e `python main_a2.py` para a A2); tempo estimado; `RANDOM_STATE = 42`; versões; onde ficam os resultados; se os dados não forem publicados, onde colocar o `UCMF_raw.csv`.
- [ ] **Step 3: Testar em clone limpo** – `git clone` do repositório local para o diretório temporário, copiar o CSV se ele não estiver versionado, `pip install -r requirements.txt`, `python -m pytest -q` e `python main_a2.py`; comparar `saida/a2/metricas_cv.csv` com o original → idênticos.
- [ ] **Step 4: Publicar** – `gh repo create <nome> --public --source . --push` e abrir a URL em janela anônima para conferir que é pública.
- [ ] **Step 5: Colocar a URL no artigo**, recompilar, repetir a verificação de páginas e fazer `git commit -m "docs: link do repositório" && git push`.

---

### Task 10: Apresentação de 15 minutos

**Files:**
- Create: deck no mesmo modelo visual dos slides da A1 do grupo; `docs/Roteiro_apresentacao_A2.md`

Slides numerados, pouco texto, figuras e tabelas grandes; ênfase em metodologia e resultados.

| # | Slide | Tempo |
|---|---|---|
| 1 | Título, grupo, pergunta do trabalho | 0:30 |
| 2 | Problema e objetivo: classificar Normal × Anormal; por que o falso negativo pesa | 1:00 |
| 3 | Dados: 12.873 → 11.470, classes 57/43, principais ausências | 1:00 |
| 4 | Data leakage: evidência do SOPRO e decisão de excluir | 1:30 |
| 5 | Pré-processamento dentro do pipeline: o que é ajustado só no treino | 1:30 |
| 6 | Protocolo: validação aninhada 10×5, métricas | 1:30 |
| 7 | Modelos e hiperparâmetros: baseline × complexos | 1:00 |
| 8 | Resultado principal: tabela comparativa e curvas | 2:00 |
| 9 | A diferença é real? Teste 5×2cv; cenários com e sem SOPRO e MOTIVOs | 1:30 |
| 10 | Desbalanceamento e limiar: recall × falsos positivos | 1:00 |
| 11 | Erros e atributos mais importantes | 1:30 |
| 12 | Conclusão, limitações e trabalhos futuros | 1:00 |

- [ ] **Step 1: Montar o deck** com as figuras e os números de `saida/a2/`.
- [ ] **Step 2: Escrever o roteiro** com a fala de cada slide, a divisão entre os integrantes (todos apresentam) e 20 perguntas prováveis com resposta, cobrindo: por que SOPRO é leakage, por que validação aninhada, por que não hold-out, por que o pré-processamento fica no pipeline, o que o 5×2cv testa, por que SMOTE só no treino, o que significa cada métrica, o que o modelo erra.
- [ ] **Step 3: Conferir** os números do deck contra `resumo_metricas.csv` e somar os tempos → 15:00.

---

### Task 11: Conferência final e entrega

- [ ] **Step 1: Conferir cada critério do enunciado** contra o PDF final e marcar onde ele é atendido (seção e página): tarefa de mineração e relevância; instâncias, atributos e desbalanceamento; visualizações na EDA; leakage identificado e excluído; justificativa de limpeza, codificação e normalização; protocolo de validação; ausência de vazamento; baseline + complexo; métricas adequadas; tabela clara; ajuste de hiperparâmetros; matriz de confusão; variáveis mais relevantes; limitações; ≤ 5 páginas; link funcional; sem código nem screenshots; uso de IA informado.
- [ ] **Step 2: Reexecutar** `python -m pytest -q` e `python main_a2.py`; `git status` limpo e `git push` feito.
- [ ] **Step 3: Leitura do grupo** – cada integrante lê o artigo e o `docs/a2_achados.md`, porque qualquer um pode ser escolhido para responder.
- [ ] **Step 4: Envio no SIGAA pelo usuário até 17/11**, um dia antes do prazo de 18/11; guardar o comprovante.

---

## Self-Review

- **Cobertura do enunciado:** todas as seções exigidas do artigo estão na Task 8; reprodutibilidade na Task 9; apresentação na Task 10; cada critério de avaliação é conferido na Task 11.
- **Coerência de nomes:** `carregar_xy`, `montar_pipeline`, `validacao_aninhada`, `teste_5x2cv`, `executar` e os nomes dos arquivos em `saida/a2/` são os mesmos em todas as tasks que os usam.
- **Review Focus:** os cinco riscos têm teste nas Tasks 2, 3, 5 e 7.
- **Risco em aberto:** se o atributo de leakage apontado pelo professor não for SOPRO, a troca é uma linha em `CENARIOS`, mas a Fig. 1 e o texto das seções II e IV precisam ser refeitos; por isso vale confirmar antes da Task 8.
