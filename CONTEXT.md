# CONTEXT — Onfly · Consolidador de reservas de hotel

Este arquivo dá a um agente o modelo mental mínimo para trabalhar neste repositório.

## Fonte

O `README.md` da raiz é a especificação do projeto. Em caso de conflito entre o README, o código e este arquivo, vale o README.

- O código atual tem defeitos conhecidos; ele não é referência de comportamento correto.
- Os dados (`data/*.csv`) estão corretos. Qualquer defeito encontrado, como citado no README, estará no CLI.
- Os testes em `tests/` são a especificação executável e não podem ser alterados.

## Invariantes verificáveis

Úteis para montar ciclos de feedback e testes, inclusive no dataset completo, que não tem saída esperada publicada:

- `confirmed + cancelled + no_show == total_reservations` (se só existirem esses três status).
- `sum(by_month[].reservations) == confirmed_reservations`.
- `sum(by_month[].room_nights) == total_room_nights`.
- A soma exata (antes de arredondar) dos `total_brl` de `by_month` é igual ao `total_amount_brl` exato. Os valores já arredondados podem diferir em centavos, e isso é esperado.
- `len(top_hotels) == min(--top, número de hotéis com reserva faturável)`.
- `top_hotels` é ordenado pelo valor numérico de `total_brl`, nunca pela string serializada.

## Regras de trabalho para o agente

- Feedback loop base: `pytest -q` + CLI na amostra comparado com as tabelas do README + CLI em `data/reservas_hoteis.csv` checado contra as invariantes acima.
- Há vários defeitos: tratar um por vez, do diagnóstico à correção, com um commit por defeito.
- Cada defeito corrigido deve ter uma causa raiz identificada e um teste de regressão próprio. A causa raiz deve ser retornada no chat com uma frase apenas. 
- Mesmo quando o `diagnosing-bugs` indicar ausência de seam correto, escreva o teste no seam mais próximo e registre a limitação neste chat de forma explicita.
- Valores esperados dos testes novos vêm do README ou de contas derivadas das regras do README, nunca da lógica do código.
- Os sintomas a diagnosticar são os descritos no README: testes fornecidos falhando e saída divergente da amostra de validação.
- Apresente a lista de hipóteses e aguarde a resposta do usuário antes de testar qualquer uma.
- Após cada commit, mostre o resultado do ciclo de feedback e aguarde o usuário liberar o próximo defeito.

## Restrições

- Não renomeie nem remova funções, classes ou módulos que os testes importam. Reorganizar o código interno é permitido, desde que esses pontos de importação continuem existindo.

## Recomendações

- Evite alterar o README, em especial o bloco entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->`. O README não proíbe isso explicitamente, mas os marcadores sugerem que esse bloco pode ser lido de forma automática na avaliação.
