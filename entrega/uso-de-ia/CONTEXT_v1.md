# CONTEXT — Onfly · Consolidador de reservas de hotel

Este arquivo dá a um agente (ou a uma pessoa nova no projeto) o modelo mental mínimo para trabalhar
aqui. Ele **não substitui** o `README.md`: resume termos e restrições e aponta para lá.

## Fonte da verdade

O `README.md` da raiz é a **especificação** do projeto. Em caso de conflito entre o README, o
código e este arquivo, vale o README.

- O código atual tem defeitos conhecidos; ele **não** é referência de comportamento correto.
- Os dados (`data/*.csv`) estão corretos. Defeito encontrado = defeito no CLI, nunca nos dados.
- Os testes em `tests/` são a especificação executável e **não podem ser alterados**.

## Objetivo do trabalho

Encontrar e corrigir os defeitos do CLI `onfly_report` para que:

1. `pytest -q` passe sem alterar os testes fornecidos;
2. o relatório gerado a partir de `data/reservas_hoteis.csv` siga exatamente o contrato do README;
3. cada defeito tenha uma causa raiz identificada e um teste de regressão.

## Glossário

| Termo | Significado |
|-|-|
| **Reserva** | Uma linha do CSV de entrada. |
| **Status** | `CONFIRMED`, `CANCELLED` ou `NO_SHOW`. |
| **Faturável** | Somente `CONFIRMED`. Só reservas faturáveis entram em noites, valores, `by_month` e `top_hotels`. |
| **Contagem** | Todas as reservas, de qualquer status, entram em `total_reservations` e nas contagens por status. |
| **Room night (noite)** | `(checkout_date - checkin_date).days * rooms`. Diferença não inclusiva, entre datas civis. |
| **Data civil** | Data `YYYY-MM-DD` sem hora e sem fuso. Nunca converter para datetime com timezone. |
| **Moeda / taxa** | `amount` está em `currency`; valor em BRL = `amount * rate_to_brl` (`data/taxas_cambio.csv`). |
| **Mês de referência** | Mês do **check-in** (`YYYY-MM`), usado em `by_month`. |
| **Diária média** | `total_amount_brl / total_room_nights`; `"0.00"` quando não há noites. |
| **Dinheiro serializado** | String com exatamente 2 casas, sem separador de milhar, arredondada half-up **só na serialização**. |
| **Amostra de validação** | `data/exemplo-validacao.csv` + tabelas entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->` no README. |

## Pipeline (ordem obrigatória)

```
ler → converter tipos → contar status → filtrar CONFIRMED → agregar → serializar
```

Contar status **antes** de filtrar. Arredondar **só** em serializar.

## Invariantes verificáveis

Úteis para montar ciclos de feedback e testes, inclusive no dataset completo, que não tem saída
esperada publicada:

- `confirmed + cancelled + no_show == total_reservations` (se só existirem esses três status).
- `sum(by_month[].reservations) == confirmed_reservations`.
- `sum(by_month[].room_nights) == total_room_nights`.
- A soma exata (antes de arredondar) dos `total_brl` de `by_month` é igual ao `total_amount_brl`
  exato. Os valores já arredondados podem diferir em centavos, e isso é esperado.
- `by_month` em ordem crescente de `month`; `top_hotels` em ordem decrescente **numérica** de
  `total_brl`, com empate por `hotel_id` crescente.
- `len(top_hotels) == min(--top, número de hotéis com reserva faturável)`.
- Nenhum `float` em caminho de dinheiro.

## Restrições (não negociáveis)

- Não alterar: comando e argumentos do CLI, schema e semântica do JSON, `data/reservas_hoteis.csv`,
  `data/taxas_cambio.csv`, testes em `tests/`, bloco da amostra no README.
- Códigos de saída: `0` sucesso, `2` entrada/argumento inválido, `1` erro inesperado.
- `generated_at` com offset fixo `-03:00`; ignorado em comparações.
- Reorganizar código interno é permitido, mas **não** renomear/remover o que os testes importam.

## Regras de trabalho para o agente

- Seguir o fluxo do `diagnosing-bugs`: primeiro um ciclo de feedback que fica vermelho, depois
  hipóteses. Não corrigir por leitura de código sem um comando que demonstre o defeito.
- Feedback loop base: `pytest -q` + CLI na amostra comparado com as tabelas do README.
- Apresentar as hipóteses ao usuário antes de testá-las; o usuário decide a ordem.
- Um defeito por vez: teste de regressão vermelho → correção mínima → verde → commit.
- Valores esperados dos testes novos vêm do README ou de contas feitas à mão, **nunca** recalculados
  do mesmo jeito que o código calcula (teste tautológico).
- Mensagem de commit cita a causa raiz em uma frase (vai para o `entrega/README-ENTREGA.md`).
- Logs de debug com prefixo `[DEBUG-onfly]`, removidos antes do fim (`grep` pelo prefixo).

## Mapa do código

_A preencher na primeira exploração: módulos de `src/onfly_report/`, o que cada um faz e quais
funções os testes importam._
