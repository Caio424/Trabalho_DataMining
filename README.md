# Triagem de patologia cardíaca pediátrica (UCMF)

**Grupo 10 – UFG:** Caio Moreira Bovo, Pedro Henrique Santana, Rafael Alencar Delfino, Yuri Resende Camargo.

Trabalho da disciplina de Mineração de Dados. Classificação binária **Normal × Anormal** (presença de patologia cardíaca) a partir dos dados de encaminhamento de 11.470 crianças e adolescentes (0–19 anos) a um serviço de cardiologia pediátrica.

- **A1:** pré-processamento (limpeza e transformação) → `main.py`, `src/p01`–`p05`
- **A2:** modelagem e artigo IEEE → `main_a2.py`, `src/m01`–`m06`, `artigo/`

## Resultado principal

| Modelo (sem o atributo Sopro) | AUC-ROC | Recall | F1 |
|---|---|---|---|
| Regressão Logística (baseline) | 0,787 | 0,587 | 0,656 |
| Random Forest | **0,802** | 0,590 | 0,665 |

Validação cruzada aninhada estratificada 10 × 5. Teste t 5×2cv entre os dois modelos: t = 3,44, p = 0,018. O atributo **Sopro** foi excluído por vazamento de dados: com ele, a AUC chegaria a 0,953. Detalhes em [`docs/a2_achados.md`](docs/a2_achados.md) e no artigo [`artigo/main.pdf`](artigo/main.pdf).

## Como reproduzir

Requisitos: Python 3.13 e as versões fixadas em `requirements.txt`.

```bash
pip install -r requirements.txt
# os dados NÃO são distribuídos neste repositório: coloque o UCMF_raw.csv
# (fornecido na disciplina) na raiz do projeto antes de rodar
python main_a2.py     # A2: limpeza (se faltar o CSV limpo), experimentos, figuras e tabelas (~50 min)
python main.py        # opcional, A1 completa: também gera o relatório .docx (usa o Word via COM)
python -m pytest      # testes (~15 min; incluem uma execução reduzida dos experimentos)
```

Toda a aleatoriedade usa `random_state = 42` (`src/config.py`). Rodar `main_a2.py` de novo reproduz exatamente os arquivos de `saida/a2/`.

Para compilar o artigo: `tectonic artigo/main.tex` (ou envie a pasta `artigo/` ao Overleaf). Todos os números do texto vêm de `artigo/numeros.tex`, gerado por `src/m06_figuras_tabelas.py`.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/config.py` | Caminhos, faixas de plausibilidade, mapeamentos, `RANDOM_STATE`, cenários de atributos |
| `src/p01`–`p05` | A1: perfil, limpeza (34 regras), análise bivariada, transformação, relatório |
| `src/m01_atributos.py` | Do arquivo limpo para `X`, `y` e grupos (nada ajustado aos dados) |
| `src/m02_modelos.py` | Pipeline: log, imputação, padronização, one-hot, reamostragem e modelo |
| `src/m03_validacao.py` | Métricas, validação cruzada aninhada, partição agrupada, teste 5×2cv |
| `src/m04_experimentos.py` | Experimentos: comparação, cenários de atributos, desbalanceamento, partição agrupada, 5×2cv |
| `src/m05_interpretacao.py` | Matriz de confusão, limiar, importância por permutação, razão de chances, perfil dos erros |
| `src/m06_figuras_tabelas.py` | Figuras, tabelas e macros numéricas do artigo |
| `saida/a2/` | Resultados brutos e resumidos dos experimentos |
| `artigo/` | Artigo no template IEEE (`main.tex`, `main.pdf`, figuras e tabelas geradas) |
| `tests/` | Testes automatizados (pytest) |
| `docs/` | Documentação da limpeza, achados e roteiros de apresentação |

## Uso de IA generativa

O assistente Claude (Anthropic), via Claude Code, apoiou a implementação do código, a organização do protocolo experimental e a redação inicial do artigo. O grupo revisou o código e conferiu os resultados.
