# Declaração de uso de IA

## Ferramentas e modelos

| Sessão | Ferramenta | Modelo | Uso |
|-|-|-|-|
| `sessao-01.md` | Claude (app) | Claude Opus 5.5 | Entendimento do enunciado, escolha de skills relevantes, `CONTEXT.md` |
| `sessao_02.jsonl` | Claude Code | Claude Opus 5.5 | Ambiente para correção dos bugs |
| `sessao_03.md` | Claude(app) | Claude Opus 5.5 | correção simples de erros de grafia na versão final de declaracao.md e README-ENTREGA.md |

Skills usadas: `diagnosing-bugs` ([plugin skills for real engineers](https://github.com/mattpocock/skills)).

## O que a IA fez

- Deu feedback sobre as skills que eu já utilizo em projetos pessoais e sugeriu utilizar `code-review` e `tdd`, que descartei por serem muito focadas em desenvolvimento de aplicações, e não em correção de bugs.
- Deu feedback sobre a ideia de adicionar os arquivos `.claude` e `.idea` ao `.gitignore`.
- Escreveu a primeira versão (`CONTEXT_v1.md`). A partir das minhas críticas, apontou problemas concretos no próprio texto, que levei em consideração durante a reescrita.
- A IA da `sessao-01.md` montou o log consolidado de sua sessão a partir do histórico da conversa, já que o `/export` não estava disponível. A IA da `sessao_02.jsonl` exportou a sessão pela ferramenta do app e omitiu o meu e-mail.
- Montou o ambiente e o loop de verificação orientado.
- Investigou cada defeito seguindo o loop proposto tanto no `CONTEXT.md` quanto na skill `diagnosing-bugs`.
- Montou testes de regressão para cada bug encontrado.
- Reverificou, com testes de regressão, todos os bugs que eu corrigi, a fim de confirmar que foram corrigidos corretamente, e encontrou uma falha na minha correção da conversão.
- Corrigiu um erro que ela mesma gerou, quando criou uma pasta indevida no ambiente.
- Encontrou o bug 5 ao gerar o relatório do dataset real: comparou o resultado do CLI com um recálculo feito direto do CSV e viu que só 200 das 300 reservas eram lidas.
- Corrigiu pessoalmente, por completo, os bugs 1, 4 e 5 e, parcialmente, o bug 3.
- Fez alguns commits, que ele é citado como co autor. 

## O que eu fiz

- Defini o escopo das sessões a fim de separar o contexto de planejamento do contexto de uso do Claude Code e, assim, aplicar a ferramenta de forma efetiva.
- Escolhi, a partir de minhas experiências passadas, a skill `diagnosing-bugs` para a resolução deste trabalho.
- Estudei a skill citada acima para utilizá-la de forma efetiva.
- Revisei criticamente todas as versões do `CONTEXT.md` para evitar redundância, tanto com o que foi citado no README quanto com o que foi implementado na skill, e diretivas imprecisas que poderiam afetar a qualidade do projeto. Assim, acabei reescrevendo parte do `CONTEXT.md`.
- Revisei o loop de feedback que o Claude Code utilizaria para a correção do repositório disponibilizado.
- Decidi a investigação:
  - Para cada bug, a IA me retornava hipóteses do que poderia estar causando o problema, e eu as revisava. Por exemplo, em uma situação, pedi à IA que testasse uma hipótese antes das outras, porque ela propunha um teste que não auxiliava na detecção daquela hipótese.
  - Um loop era iniciado apenas quando eu verificava pessoalmente que o bug havia sido solucionado.
- Organizei a entrega.
- Perguntei se o relatório do dataset real já tinha sido gerado, o que levou a IA a encontrar o bug 5.
- Corrigi pessoalmente o bug 2 por completo e, parcialmente, o bug 3.
- Revisei e fiz o commit da correção do bug 5 (`f9d298a`), feita pela IA.
- Fiz alguns commits que não citam o claude como co autor. 

## Artefatos e autoria

- `CONTEXT.md`: v1 gerada pela IA (`uso-de-ia/CONTEXT_v1.md`); na versão final, , eu removi redundâncias e adequei para funcionar com o README e com a skill, a versão final se encontra na raiz deste repositorio.  