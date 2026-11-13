# Entrega — Consolidador de reservas de hotel (Onfly)

**Autor:** Luís Felipe Henrique Campelo · **Repositório:** https://github.com/maroelo/onfly-challenge · **Uso de IA:** sim — ver [`uso-de-ia/declaracao.md`](uso-de-ia/declaracao.md)

## Resumo

Foram encontrados e corrigidos **5 defeitos** no CLI: status faturável, cálculo de noites, câmbio, ordenação do ranking e um limite de leitura de 200 linhas que nenhum teste fornecido cobria, mas que contradizia o README. No fim, `pytest -q` passa com os 5 testes fornecidos sem alteração e com 11 testes de regressão novos (16 no total). A amostra de validação bate integralmente com as tabelas do README, e o relatório do dataset completo confere com um recálculo independente feito direto do CSV.

## Defeitos corrigidos

| # | Defeito | Causa raiz | Testes | Commit |
|-|-|-|-|-|
| 1 | Reservas `NO_SHOW` eram inclusas em noites, valores, `by_month` e `top_hotels` | `is_billable` excluía só `CANCELLED` , era verificado apenas se status era diferente de `CANCELLED`, então `NO_SHOW` passava como faturável, embora o correto seria apenas `CONFIRMED`. | **Fornecido:** `tests/test_status_rules.py`<br>**Novo:** `tests/test_regression_no_show_not_billable.py` | `ac01e49` |
| 2 | Noites negativas na virada de mês (30/01 → 02/02 dava `-28`) | `calculate_room_nights` subtraía o dia do mês (`.day`) em vez de calcular a diferença entre as datas. | **Fornecido:** `tests/test_nights.py`<br>**Novo:** `tests/test_regression_room_nights.py` | `aaf2318` |
| 3 | Câmbio errado (100 USD virava `18.45` BRL; 0.75 USD virava `4.06` em vez de `4.07`) | `convert_to_brl` dividia o valor pela taxa em vez de multiplicar e fazia a conta em `float`, e não em `Decimal`. | **Fornecidos:** `tests/test_currency.py`, `tests/test_regression_report.py`<br>**Novo:** `tests/test_regression_currency_exactness.py` | `858ea88` |
| 4 | `top_hotels` mostrava os hotéis de menor valor primeiro | O ranking ordenava pelo valor em ordem crescente, quando o README pede ordem decrescente com desempate por `hotel_id` crescente. | **Fornecido:** `tests/test_top_hotels.py`<br>**Novo:** `tests/test_regression_top_hotels_order.py` | `4166039` |
| 5 | O dataset completo mostrava 200 reservas em vez de 300 | O leitor do CSV interrompia a leitura (`break`) ao chegar a 200 linhas, ignorando todas as reservas depois da 200ª. | **Fornecido:** nenhum<br>**Novo:** `tests/test_regression_reads_all_rows.py` | `f9d298a` |

### Testes por defeito

Os testes fornecidos não foram alterados. Cada defeito também ganhou testes novos, que cobrem casos que os fornecidos não pegavam. Todos rodam o CLI de ponta a ponta (`tests/helpers.py::run_cli`), e os valores esperados vêm das regras do README.

| # | Teste | Origem | O que verifica | Antes da correção |
|-|-|-|-|-|
| 1 | `test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show` | fornecido | Só `CONFIRMED` entra no total financeiro | falhava: `120.00` ≠ `100.00` |
| 1 | `test_regression_no_show_not_billable.py::test_no_show_alone_is_counted_but_not_billed` | novo | Um `NO_SHOW` sozinho conta no total, mas zera noites e valores e deixa `by_month` e `top_hotels` vazios | falhava |
| 1 | `test_regression_no_show_not_billable.py::test_no_show_does_not_leak_into_by_month_or_top_hotels` | novo | O `NO_SHOW` não vaza para `by_month` nem `top_hotels` | falhava |
| 2 | `test_nights.py::test_nights_across_month_boundary` | fornecido | Virada de mês: 30/01 → 02/02 = 3 noites | falhava: `-28` ≠ `3` |
| 2 | `test_regression_room_nights.py::test_room_nights_across_year_boundary_with_multiple_rooms` | novo | Virada de ano com 2 quartos: 30/12/2024 → 02/01/2025 = 6 noites | falhava: `-56` ≠ `6` |
| 2 | `test_regression_room_nights.py::test_room_nights_sum_across_months_by_checkin` | novo | Noites somadas no mês do check-in | falhava: `-49` ≠ `13` |
| 3 | `test_currency.py::test_currency_conversion_to_brl` | fornecido | Multiplica pela taxa: 100 BRL + 100 USD = 642.00 | falhava: `118.45` ≠ `642.00` |
| 3 | `test_regression_report.py::test_regression_report_on_sample` | fornecido | Resumo completo de uma amostra com BRL, USD e `CANCELLED` | falhava: `1018.45` ≠ `1542.00` |
| 3 | `test_regression_currency_exactness.py::test_conversion_multiplies_by_rate` | novo | 100 USD = 542.00 | falhava no código original (`e93affb`): `18.45` ≠ `542.00` |
| 3 | `test_regression_currency_exactness.py::test_conversion_is_exact_before_half_up` | novo | Conta exata em `Decimal`: 0.75 USD = 4.065 → `4.07`; pelo `float` dava `4.06` | falhava no código original (`0.14` ≠ `4.07`) e continuava falhando depois de trocar `/` por `*` (`4.06` ≠ `4.07`) |
| 4 | `test_top_hotels.py::test_top_hotels_are_ranked_descending` | fornecido | Maior valor primeiro: H01, H02, H03 | falhava: `H04, H03, H02` |
| 4 | `test_regression_top_hotels_order.py::test_highest_total_first_with_same_digit_count` | novo | 950 antes de 900, com o mesmo número de dígitos | falhava |
| 4 | `test_regression_top_hotels_order.py::test_numeric_not_string_order_and_top_n_cut` | novo | Ordem numérica, não por texto (1000 antes de 900), e corte em `--top` | falhava |
| 4 | `test_regression_top_hotels_order.py::test_tie_breaks_by_hotel_id_ascending` | novo | Empate de valor resolvido por `hotel_id` crescente | falhava |
| 5 | `test_regression_reads_all_rows.py::test_all_rows_are_read_beyond_200` | novo | 250 reservas são lidas inteiras | falhava: `200` ≠ `250` |
| 5 | `test_regression_reads_all_rows.py::test_last_row_of_the_file_is_counted` | novo | A 201ª linha é contada | falhava: `200` ≠ `201` |

### Detalhes por defeito

#### 1. NO_SHOW faturado
- **Onde:** `src/onfly_report/services/status_policy.py` (função `is_billable`)
- **Antes:** uma única reserva `NO_SHOW` de 100.00 BRL gerava `total_amount_brl = "100.00"`, 1 noite e entradas em `by_month` e `top_hotels`.
- **Depois:** `return status == "CONFIRMED"`. A reserva `NO_SHOW` conta em `total_reservations` e `no_show_reservations`, mas não em noites, valores, `by_month` nem `top_hotels` (README, seção Status).

#### 2. Noites na virada de mês e de ano
- **Onde:** `src/onfly_report/services/stay_calculator.py` (função `calculate_room_nights`)
- **Antes:** `(checkout.day - checkin.day) * rooms`, então 30/01 → 02/02 dava 2 − 30 = `-28`.
- **Depois:** `(checkout - checkin).days * rooms`, que é a fórmula do README. Ela também vale na virada de ano: 30/12/2024 → 02/01/2025 com 2 quartos dá 6.

#### 3. Câmbio
- **Onde:** `src/onfly_report/services/currency_converter.py` (função `convert_to_brl`)
- **Antes:** `Decimal(str(float(amount) / float(rate)))`.
- **Correção em duas etapas:**
  1. Trocar `/` por `*` corrigiu o sentido da conta, mas o `float` continuava errando: `0.75 * 5.42` dá `4.0649999999999995`, que arredonda para `4.06`.
  2. A versão final é `return amount * rate`, toda em `Decimal`. O resultado exato é `4.065`, que arredonda (half-up) para `4.07` (README, seções Câmbio e Exatidão).

#### 4. Ranking de hotéis
- **Onde:** `src/onfly_report/services/report_builder.py` (`ReportBuilder.build`)
- **Antes:** a chave de ordenação era `(amount, hotel_id)` em ordem crescente, e o código pegava os N primeiros, ou seja, os N de menor valor.
- **Depois:** a chave é `(-amount, hotel_id)`. Neguei só o valor porque `reverse=True` inverteria também o desempate, que precisa continuar por `hotel_id` crescente (README, seção Ordenação).

#### 5. Limite de 200 linhas
- **Onde:** `src/onfly_report/repositories/csv_reservation_repository.py` (`CsvReservationRepository.read`)
- **Antes:** um `if len(rows) == 200: break` descartava as linhas 201 a 300 do dataset real (RSV-0201 a RSV-0300).
- **Depois:** o leitor devolve todas as linhas do arquivo, porque `total_reservations` é o "número de reservas no arquivo" (README, seção Totais).

## Como foi investigado

### Ponto de partida

- O `README.md` foi tratado como a especificação. Os testes em `tests/` foram tratados como especificação executável e não foram alterados.
- `CONTEXT.md` com especificações para a IA: um defeito por vez uma causa raiz e um teste de regressão por defeito, um commit por defeito, e valores esperados tirados do README, nunca da lógica do código. nele também são listadas algumas invariantes verificáveis no dataset completo, que não tem saída esperada publicada.
- Antes de executar o agente eu rodava os testes pessoalmente para entender o problema, e algumas vezes resolvê-lo
- Linha de base: commit `e93affb` (código original) e `7208e23` (versão final do `CONTEXT.md`).
- A investigação seguiu a skill `diagnosing-bugs`: Teste pessoal → ciclo de feedback → reproduzir e minimizar → hipóteses → avaliar as hipóteses propostas → instrumentar → teste de regressão antes da correção → limpeza. 
- Os defeitos 2 e 3 eu corrigi pessoalmente, por isso não levantei hipóteses alternativas. No 3, deixei passar o erro de float: o agente o encontrou com testes de verificação que eu pedi depois da minha correção. Os defeitos 1, 4 e 5 seguiram o fluxo completo da skill. O defeito 5 foi encontrado pelo agente ao gerar o relatório do dataset real, depois que eu perguntei se ele já tinha sido feito.

### Ciclo de feedback

Usei um único comando de verificação, que roda em cerca de 1 segundo e dá sempre o mesmo resultado. Ele junta:

1. `pytest -q`.
2. O CLI na amostra (`data/exemplo-validacao.csv`), com cada campo comparado com as tabelas entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->` do README.
3. O CLI no dataset completo, checado contra as invariantes:
   - `confirmed + cancelled + no_show == total_reservations`;
   - `sum(by_month.reservations) == confirmed_reservations`;
   - `sum(by_month.room_nights) == total_room_nights`;
   - noites sempre positivas;
   - `by_month` em ordem crescente;
   - `top_hotels` em ordem numérica decrescente de `total_brl`, com desempate por `hotel_id`;
   - formato do dinheiro com 2 casas.
4. Uma invariante acrescentada depois do defeito 5: `total_reservations` igual ao número de linhas do CSV.

**Estado inicial:** 5 de 5 testes falhando e 11 falhas no ciclo de verificação. Na amostra, `total_room_nights` era `-33` (esperado 28) e `total_amount_brl` era `5962.41` (esperado 7566.00).

Antes de levantar hipóteses, foi reduzido cada sintoma ao menor CSV que ainda falhava, usando o mesmo `run_cli` dos testes:

| Repro mínimo | Obtido | Esperado |
|-|-|-|
| 1 reserva `NO_SHOW` | 1 noite, 100.00 | 0 noites, 0.00 |
| 1 reserva de 30/01 a 02/02 | -28 noites | 3 |
| 1 reserva de 100.00 USD | 18.45 | 542.00 |
| H01=1000 e H02=900, `--top 1` | H02 | H01 |
| 201 linhas idênticas | 200 lidas | 201 |

O defeito 5 não aparecia nos testes fornecidos nem na amostra, que têm menos de 200 linhas. Ele também não quebrava nenhuma invariante, porque o relatório continuava coerente consigo mesmo. Só apareceu ao comparar o relatório do dataset completo com um recálculo independente feito direto do CSV, sem usar o código do projeto: 300 reservas e 396170.00 BRL, contra 200 reservas e 249543.79 no CLI.

### Hipóteses

| Defeito | Hipótese | Como testei | Resultado |
|-|-|-|-|
| 1 | A regra de faturável exclui só `CANCELLED` | Observei `is_billable('NO_SHOW')` em memória: devolvia `True` | **confirmada** |
| 1 | A agregação lê uma lista sem filtro | Corrigi só o filtro em memória: o `NO_SHOW` sumiu de todos os agregados, então a agregação só lê a saída do filtro | descartada |
| 1 | A contagem e o filtro usam grafias diferentes de `NO_SHOW` | O filtro recebia exatamente `'NO_SHOW'`, a mesma string da contagem | descartada |
| 1 | O parser converte o status para um tipo com a flag errada | O status chegava ao filtro como string pura | descartada |
| 2 | A conta usa o dia do mês, não a diferença entre datas | Teste com e sem a correção: `-28`/`-56`/`-49` sem ela, `3`/`6`/`13` com ela | **confirmada** |
| 3 | Divisão em vez de multiplicação | 100 USD: `18.45` = 100 / 5.42 | **confirmada** |
| 3 | O `float` causa erro de arredondamento | Comparei com a conta exata em `Decimal`: 19 linhas do dataset ficavam inexatas, e 0.75 USD dava `4.06` em vez de `4.07` | **confirmada** |
| 4 | Ordenação numérica em ordem crescente | a lista ordenada foi observada antes do corte: crescente (100 → 200 → 300) | **confirmada** |
| 4 | Ordenação pelo texto serializado | 950 contra 900, com o mesmo número de dígitos, também saía errado | descartada |
| 4 | O corte pega a ponta errada da lista | A lista já saía crescente antes do corte, e o corte pegava o começo | descartada |
| 4 | O ranking usa outro campo (noites ou reservas) | Com noites iguais, daria H01, H02, H03, o que não aconteceu | descartada |
| 5 | Limite fixo de linhas no leitor | CSVs limpos com 201, 250 e 450 linhas resultavam sempre em 200 | **confirmada** |
| 5 | Uma linha específica interrompe a leitura | O corte também acontecia com linhas limpas e idênticas | descartada |
| 5 | Leitura em blocos que descarta o último | 450 linhas davam 200, e não 400 | descartada |
| 5 | Filtro por coluna que coincide com as linhas 201 a 300 | Com o dataset embaralhado, continuavam sendo lidas exatamente 200 linhas (corte por posição) | descartada |

Nos defeitos 1, 4 e 5, o teste de regressão foi escrito e visto falhar antes da correção. Nos defeitos 2 e 3, a minha correção veio primeiro:
- **Defeito 2:** confirmei que o teste pega o erro desfazendo a correção temporariamente e vendo o teste falhar.
- **Defeito 3:** o teste de exatidão foi escrito antes da troca para `Decimal` e falhou com a minha versão em `float` (`4.06`). Os dois testes de câmbio também foram rodados contra o código original (`e93affb`) e falharam (`18.45` e `0.14`).

### Limitações e decisões

- **Ponto de teste:** todos os testes de regressão rodam o CLI de ponta a ponta (`tests/helpers.py::run_cli`), o mesmo caminho dos testes fornecidos. Assim eles exercitam o defeito como ele aparece no relatório. Não houve defeito sem um ponto adequado para teste.
- **Status desconhecido:** um status fora de `CONFIRMED`, `CANCELLED` e `NO_SHOW` não é faturável, porque o README diz que "só `CONFIRMED` é faturável". O dataset só tem esses três status.
- **Arredondamento:** a soma dos `total_brl` de `by_month` já arredondados pode diferir do `total_amount_brl` em centavos. Isso é esperado, porque o arredondamento acontece só na serialização.
- **O que ficou de fora:** o script do ciclo de feedback e as sondas de investigação foram descartáveis e ficaram fora do repositório. Nenhum código de depuração ficou no projeto.

## Como validar

Requisitos: Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Testes:

```bash
pytest -q
```

Relatório do dataset completo:

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

Resumo impresso no stdout:

```
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

Resumo do `output/report.json`:

| Campo | Valor |
|-|-|
| `total_reservations` | 300 |
| `confirmed_reservations` | 235 |
| `cancelled_reservations` | 31 |
| `no_show_reservations` | 34 |
| `total_room_nights` | 1347 |
| `total_amount_brl` | 396170.00 |
| `average_nightly_rate_brl` | 294.11 |

Amostra de validação (comparar com as tabelas do README):

```bash
PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json
```

| Campo | Esperado (README) | Antes das correções | Depois das correções |
|-|-|-|-|
| `total_reservations` | 12 | 12 | 12 |
| `confirmed_reservations` | 9 | 9 | 9 |
| `cancelled_reservations` | 2 | 2 | 2 |
| `no_show_reservations` | 1 | 1 | 1 |
| `total_room_nights` | 28 | -33 | 28 |
| `total_amount_brl` | 7566.00 | 5962.41 | 7566.00 |
| `average_nightly_rate_brl` | 270.21 | 0.00 | 270.21 |
| `by_month` 2025-01 | 8 / 25 / 6684.00 | 9 / -36 / 5936.90 | 8 / 25 / 6684.00 |
| `by_month` 2025-02 | 1 / 3 / 882.00 | 1 / 3 / 25.51 | 1 / 3 / 882.00 |
| `top_hotels` | H01, H02, H12, H10, H09 | H09, H02, H05, H08, H07 | H01, H02, H12, H10, H09 |

## Resultado do pytest

Antes das correções:

```
FAILED tests/test_currency.py::test_currency_conversion_to_brl - AssertionErr...
FAILED tests/test_nights.py::test_nights_across_month_boundary - assert -28 == 3
FAILED tests/test_regression_report.py::test_regression_report_on_sample - As...
FAILED tests/test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show
FAILED tests/test_top_hotels.py::test_top_hotels_are_ranked_descending - Asse...
5 failed in 0.73s
```

Depois das correções:

```
................                                                         [100%]
16 passed in 2.15s
```

## Uso de IA

Usei o Claude Code e chat do app desktop com o modelo Claude Opus 5.5 com a skill [`diagnosing-bugs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs). O detalhe está em [`uso-de-ia/declaracao.md`](uso-de-ia/declaracao.md), e as sessões exportadas estão em [`uso-de-ia/`](uso-de-ia/).
