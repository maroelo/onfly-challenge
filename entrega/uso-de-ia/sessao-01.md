# Sessão de IA — Onfly · Consolidador de reservas de hotel

| Campo | Valor |
|-|-|
| Ferramenta | Claude (app desktop/web da Anthropic, sessão agêntica baseada no Claude Code) |
| Modelo | Claude Opus 5.5 (`claude-opus-5-5`) |
| Período | 2026-11-11 18:59 → 2026-11-12 17:24 (horário de Brasília) |
| Formato | Log consolidado de prompts e respostas (opção prevista no README) |

## Por que este formato

O comando `/export` não estava disponível nesta interface e o ambiente não guardou um log nativo
(`.jsonl`) da sessão. Este arquivo foi gerado pela própria IA, ao final da sessão, a partir do
histórico da conversa:

- **Prompts do usuário:** transcritos literalmente, sem correções.
- **Respostas da IA:** transcritas literalmente.
- **Ações de ferramenta** (leitura de arquivos, criação de arquivos): resumidas entre colchetes, no
  ponto em que ocorreram. Metadados internos da plataforma (lembretes de sistema, dados da conta)
  foram omitidos.
- **Arquivos gerados pela IA:** conteúdo completo no Apêndice.

Nesta sessão **nenhum código do projeto foi lido, executado ou alterado**. Ela cobriu a
compreensão do enunciado, a escolha das skills e a escrita do `CONTEXT.md`.

---

## Turno 1

**Usuário** _(anexou o `README.md` do desafio)_

> Nesta conversa esta anexado um README, nele é descrito um projeto para uma seleção, não se preocupe em montar nem nada, quero um entendimento mais profundo de oque esta sendo pedido de mim.

**IA**

[Leu o `README.md` anexado.]

### O que a Onfly está pedindo de você

#### Em uma frase

Não é um desafio de construir algo do zero. É um **desafio de depuração com contrato fechado**: o código já existe, a saída está especificada nos mínimos detalhes e há bugs plantados de propósito. Eles querem ver se você encontra os defeitos, entende por que eles acontecem, corrige sem quebrar o contrato e explica o que fez.

#### O cenário

Uma empresa cliente exportou as reservas de hotel em CSV. O CLI em Python lê esse CSV junto com uma tabela de câmbio e gera um relatório JSON com:

- **totais**: quantidade de reservas por status, noites, valor em BRL e diária média;
- **quebra por mês** do check-in;
- **ranking dos hotéis** que mais faturaram.

O README diz duas coisas que limitam onde procurar:

1. **"Os dados estão consistentes, os defeitos estão no CLI."** O problema não está no CSV, então não "conserte" os dados. Os arquivos `reservas_hoteis.csv` e `taxas_cambio.csv` são intocáveis.
2. **"Não altere os testes."** Os testes funcionam como a especificação executável. Se um teste falha, o erro está no código.

#### As regras de negócio são pistas dos bugs

Esse é o ponto mais importante. Quase toda regra que o README faz questão de explicar existe porque o código atual provavelmente a viola. Lendo assim:

| Regra no README | Bug provável no código |
|---|---|
| Ordem `ler → converter → contar status → filtrar CONFIRMED → agregar` | O código filtra antes de contar, e aí `cancelled`/`no_show` saem zerados ou `total_reservations` só conta as confirmadas |
| Diferença de datas "não inclusiva" (10/01 → 13/01 = 3) | Um `+1` sobrando, ou `rooms` não multiplicado |
| "Vale também na virada de mês/ano" | O código subtrai o dia do mês (`checkout.day - checkin.day`) em vez de subtrair as datas, e isso dá negativo ou errado em 30/01 → 02/02 |
| "Converta com `amount * rate`" | O código divide pela taxa, ou inverte a direção do câmbio |
| "Todas as moedas têm taxa" | O código usa taxa `1` como padrão quando não acha a moeda (falha silenciosa), ou procura com chave errada (maiúscula/minúscula, espaço) |
| "`Decimal`, nunca `float`" | O código usa `float` |
| "Arredonde só na serialização, half-up" | O código arredonda cada linha antes de somar, ou usa o `round()` do Python, que é *half-even* (banker's rounding): `round(2.675, 2)` não dá o que você espera |
| "`average = total / noites`" | O código calcula a média das diárias individuais, que dá outro número, ou divide por zero quando não há noites |
| "Datas civis" e "offset fixo -03:00" | O código interpreta a data como datetime UTC e converte o fuso, o que desloca o dia. Uma reserva em 01/02 pode cair em 31/01 e mudar de mês no `by_month` |
| "`by_month` usa o mês do check-in" | O código usa o check-out |
| "`top_hotels`: `total_brl` decrescente, empate por `hotel_id`" | O código ordena pela **string** `"900.00"`, que em ordem alfabética fica acima de `"1200.00"`. Ou ordena crescente, ou não desempata |
| "`--top` itens (inteiro ≥ 1)" | Off-by-one no slice, corte feito antes de ordenar, ou `--top 0` aceito sem validação |
| Códigos de saída `0` / `2` / `1` | Erro de entrada saindo com `1`, ou exceção engolida |

Um detalhe que passa despercebido: a amostra tem hotéis chamados **"Hotel Madrid, Gran Vía"** e **"Hotel Lisboa, Centro"**. Esses nomes têm **vírgula** e **acento** de propósito. Se o código lê o CSV com `line.split(",")` em vez do módulo `csv`, ou abre o arquivo sem `encoding="utf-8"`, essas linhas quebram. É quase certamente um dos bugs.

#### As três camadas de avaliação

O mínimo é **fazer os testes passarem**. Isso não basta, porque o README avisa que **"a amostra cobre apenas parte dos cenários"**.

A segunda camada é o **relatório do dataset real** (`reservas_hoteis.csv`). Muito provavelmente eles têm o JSON esperado guardado e vão comparar campo a campo, ignorando só o `generated_at`. Por isso o formato precisa ser exato: dinheiro como string com 2 casas, sem separador de milhar, nomes de campo idênticos, ordem correta. Os testes podem não cobrir tudo o que essa comparação cobre.

A terceira camada é o **raciocínio**. O `README-ENTREGA.md` pede, para cada defeito, a **causa raiz em uma frase**. Eles querem ver que você entendeu por que o bug existe, e não só que mexeu até o teste ficar verde. "Testes adicionais são considerados" também conta ponto: escrever um teste para cada bug que você achou, como a virada de ano, o empate no ranking, o half-up em `x.xx5` e o nome com vírgula, mostra método.

#### A parte sobre IA, que pesa mais do que parece

Eles **permitem** IA, mas pedem transparência total: exportar a sessão no formato nativo e uma declaração dizendo o que a IA fez e o que **você** fez.

Duas observações práticas:

- **Esta conversa já conta como uso de IA.** Se você seguir pelo caminho com IA, vale incluí-la, ou ao menos mencioná-la na declaração.
- O que eles avaliam aqui provavelmente é **como você conduz a ferramenta**: se você questiona o que ela propõe, valida os números contra a amostra e entende cada correção. Uma sessão em que você só pede "conserta tudo" e aceita a resposta passa uma impressão bem diferente de uma em que você investiga, levanta hipóteses e confere. A declaração precisa ser honesta, porque a sessão exportada vai mostrar o que realmente aconteceu.

#### Armadilhas fáceis de cair

- **Mudar o schema "para melhorar"**, por exemplo trocar dinheiro de string para número. Isso é proibido explicitamente.
- **Reorganizar demais o código.** É permitido, mas se os testes importam funções com nomes e assinaturas específicos, renomear quebra os testes.
- **Mexer no bloco entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->`.** Esses marcadores sugerem que algum script lê essa tabela automaticamente.
- **Esquecer a pasta `entrega/`** ou deixar o repositório privado.
- **Corrigir o sintoma em vez da causa.** Um exemplo é fazer um ajuste específico para a amostra bater: passa na amostra e falha no dataset real.

#### Resumo

O pedido é que você trabalhe como um engenheiro que recebe um relatório financeiro com números errados em produção: leia a especificação como um contrato, use cada regra como hipótese de bug, prove cada correção com teste, não toque no que é proibido e documente o raciocínio de forma que outra pessoa consiga auditar. Os bugs em si (datas, arredondamento, câmbio, ordenação, parsing de CSV) são clássicos de sistemas financeiros, e o domínio da Onfly é exatamente esse: viagens corporativas, várias moedas, faturamento.

---

## Turno 2

**Usuário**

> no caso de utilização de IA, eu tenho algumas skills instaladas aqui, algumas que eu fiz e outras que costumo utilizar dentro de projetos, como o plugin skills for real engineers. Eu quero que você verifique a utilidade do do fluxo ja proposto, dado que algumas coisas eu ja entendo que não serão uteis, como a skill grill me que é mais utilizada para levantar algo do zero, no entanto skills como diagnosing bugs seja extremamente util.

**IA**

[Localizou no disco os arquivos `SKILL.md` do plugin instalado e listou todas as skills. Leu na íntegra `diagnosing-bugs` e `tdd`, e o início de `code-review`, `setup-matt-pocock-skills`, `retro`, `handoff` e `domain-modeling`.]

Li os arquivos das skills do *skills for real engineers* instalados aqui para avaliar cada uma pelo que ela faz de fato, e não só pela descrição. No geral, concordo com você: o `diagnosing-bugs` é a peça central, mas ele sozinho não cobre o desafio. Abaixo está o que vale a pena usar, o que ajuda de forma pontual e o que é melhor deixar de fora.

#### Essenciais

##### `diagnosing-bugs`: a espinha dorsal

Encaixa quase perfeitamente, e a estrutura dele corresponde item por item ao que a Onfly pede no `README-ENTREGA.md`:

| Fase da skill | O que vira no desafio |
|---|---|
| **1. Ciclo de feedback** que fica vermelho no bug | O `pytest -q` mais um script pequeno que roda o CLI na amostra e compara com a tabela do README. A skill chama isso de *"CLI invocation with a fixture input, diffing against a known-good snapshot"*, que é exatamente o seu caso. |
| **3. De 3 a 5 hipóteses refutáveis, ranqueadas e mostradas ao usuário** | A seção "como investigou/abordou o problema". As regras de negócio que discutimos antes já funcionam como lista de hipóteses. |
| **5. Teste de regressão antes da correção** | Os "testes adicionais", que contam ponto. |
| **6. Hipótese correta registrada no commit** | A "causa raiz em uma frase por defeito". |

Há também um ganho que é específico desta seleção. A skill manda **mostrar as hipóteses para você antes de testar**. Na sessão exportada, isso deixa registrado que você conduziu a investigação e decidiu o que testar, e foi justamente isso que eu disse que eles avaliam.

O ponto a ajustar é que a skill foi pensada para **um bug difícil**, e aqui há vários bugs, provavelmente fáceis. Fazer a cerimônia completa dez vezes é exagero. O que funciona melhor:
- montar a Fase 1 **uma única vez**, já que o ciclo serve para todos os bugs;
- fazer as Fases 3 a 5 **por bug**, de forma enxuta;
- pular quase toda a etapa de "minimizar", porque a amostra já tem só 12 linhas.

##### `tdd`: complemento do diagnosing-bugs na Fase 5

Ela não serve como fluxo principal, porque você não está construindo funcionalidade nova. Serve para que os testes adicionais sejam bons. Três regras dela importam aqui:

- **Confirmar os seams antes de escrever testes.** Neste projeto há dois: as funções que os testes fornecidos já importam e o CLI de ponta a ponta. Escrever testes em funções internas que você talvez renomeie é desperdício.
- **Evitar teste tautológico.** Essa é a armadilha mais perigosa quando a IA escreve os testes: ela calcula o valor esperado do mesmo jeito que o código calcula, e o teste passa por construção. Os valores esperados precisam vir do README (tabela da amostra, exemplo do 10/01 → 13/01) ou de uma conta feita por você à mão.
- **Fatias verticais**, ou seja, um teste, uma correção e repete. Isso combina com a ideia de tratar um bug por vez.

#### Úteis em um momento específico

##### `code-review`: no final, revisando contra a especificação

O eixo **Spec** é muito útil aqui, porque o README é uma especificação fechada e a revisão confere se o diff respeita o contrato, o schema e as proibições. O eixo **Standards** vai sair fraco, porque o repositório não tem guia de estilo.

Ela tem duas dependências:
- Precisa de um **ponto fixo no git**. Por isso, **antes de tocar em qualquer coisa, faça `git init` e um commit do código original**. Isso ajuda a revisão e também o avaliador, que vai conseguir ver o diff exato das suas correções.
- Ela procura `docs/agents/issue-tracker.md` e sugere rodar o `setup-matt-pocock-skills`. Não vale a pena: basta passar o caminho do README como especificação. Ela também roda **subagentes**, e as conversas deles podem não aparecer no `/export`. Mencione isso na declaração.

##### `handoff`: só se precisar

Use só se a sessão ficar longa e você precisar abrir outra. Lembre que o README aceita várias sessões (`sessao-01.md`, `sessao-02.md`), mas **todas** precisam ser exportadas.

#### Não usar, ou não compensam

- **`grill-me`, `grilling`, `grill-with-docs`**: concordo, são para desenhar algo do zero, e aqui tudo já está especificado.
- **`codebase-design`, `improve-codebase-architecture`**: são **arriscadas**, não só inúteis. Elas incentivam a reorganizar módulos, e se os testes fornecidos importam funções por nome, você quebra os testes que não pode alterar. Corrija no lugar.
- **`domain-modeling`**: o domínio é pequeno e já tem glossário (o próprio README). Criar `CONTEXT.md` e ADRs seria cerimônia que o avaliador não pediu.
- **`to-spec`, `to-tickets`, `triage`, `wayfinder`, `implement`, `implement-spec`**: são para trabalho grande, com issue tracker. Aqui não se aplicam.
- **`setup-pre-commit`**: usa Husky e lint-staged, do ecossistema JS, e o projeto é Python.
- **`prototype`, `wizard`, `research`, `pr`, `scaffold-exercises`, `migrate-to-shoehorn`**: estão fora do escopo.
- **`retro`**: melhora o ambiente do agente para sessões futuras e não acrescenta nada à entrega.
- **`writing-*`**: podem ajudar a estruturar o `README-ENTREGA.md`, mas eu recomendaria que **você** escrevesse esse arquivo. A declaração de IA fica mais forte quando diz que a investigação e o texto final são seus.

#### Fluxo que eu sugiro

1. **Linha de base**: `git init` e commit do código original.
2. **`diagnosing-bugs`, Fase 1**: rodar o `pytest` e o script que compara a amostra com o README, e registrar o que falha.
3. **`diagnosing-bugs`, Fase 3**: lista de hipóteses. **Você** ranqueia e corrige o que achar necessário.
4. **Para cada bug**: teste de regressão que falha (regras do `tdd`), correção, teste passa, commit com a causa raiz na mensagem.
5. **Dataset real**: rodar no `reservas_hoteis.csv` e conferir invariantes. Por exemplo, a soma do `by_month` precisa bater com o total, e as contagens por status precisam somar `total_reservations`. É aqui que aparecem os bugs que a amostra não cobre.
6. **`code-review`** contra o README como especificação.
7. **Entrega**: `README-ENTREGA.md` escrito por você, exportação das sessões e uma declaração que cite as skills usadas.

Esse último item merece atenção. Dizer na declaração que você usou um fluxo de diagnóstico estruturado com hipóteses refutáveis e testes de regressão mostra maturidade no uso de IA, e o avaliador consegue conferir isso na sessão exportada.

---

## Turno 3

**Usuário**

> Sobre pastas .idea e .claude, você acha que pertinente enviar estes no github ou você acha que é necessario adicionar eles no gitignore

**IA**

Coloque as duas no `.gitignore`. A `.claude` tem uma exceção, que explico abaixo.

**`.idea`: ignore sempre.** É a configuração pessoal do seu PyCharm/IntelliJ: layout das janelas, interpretador local, caminhos absolutos da sua máquina. Não serve para mais ninguém e, num repositório de seleção, passa a impressão de descuido.

**`.claude`: ignore também, neste caso.** Normalmente ela guarda:
- `settings.local.json`, com as suas permissões locais e eventuais caminhos da sua máquina. Esse arquivo nunca deve subir.
- `settings.json`, comandos e agentes do projeto. Em projetos de equipe às vezes vale versionar, para todos usarem a mesma configuração.

Neste desafio, a prova do uso de IA tem um lugar definido: `entrega/uso-de-ia/`, com a sessão exportada e a `declaracao.md`. Subir a `.claude` não acrescenta transparência e pode expor configurações locais.

**A exceção:** se você criar um `CLAUDE.md` com instruções para o agente (algo como "não altere os testes" ou "use Decimal"), vale versionar esse arquivo. Ele fica na raiz do projeto, não dentro da `.claude`. Ele mostra como você orientou a ferramenta, e isso reforça a declaração. Se fizer isso, cite o arquivo na `declaracao.md`.

Sugestão de `.gitignore`:

```gitignore
# IDE
.idea/
.vscode/

# Claude Code (configuração local)
.claude/

# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

**Sobre o `output/`:** o README não diz se o relatório gerado deve ir para o repositório. Eu deixaria o `output/report.json` versionado, porque o avaliador vê o resultado sem precisar rodar nada. Se preferir não versionar, explique no `README-ENTREGA.md` como gerar.

Por fim, se alguma dessas pastas já tiver entrado num commit, o `.gitignore` sozinho não a remove do repositório. Rode:

```bash
git rm -r --cached .idea .claude
git commit -m "Remove configs locais do versionamento"
```

---

## Turno 4

**Usuário**

> na skill que citei, ele diz que ele já lê imediatamente uma um context.md. Gere um context.md que possa ser utilizado na primeira fase da skill, explicando a importancia do readme e etc. e outra coisa, esse context.md, é bom adicionar no gitignore né, e depois citar ele no meu relatorio final.

**IA**

[Criou o arquivo `CONTEXT.md` (versão 1, conteúdo no Apêndice A) e enviou ao usuário.]

Criei o `CONTEXT.md`. Coloque-o na **raiz** do projeto, porque é lá que a skill procura.

O arquivo tem três escolhas de propósito:

- **Ele aponta para o README, não o copia.** O README fica declarado como a fonte da verdade, e o CONTEXT só resume os termos e as restrições. Assim você não fica com duas especificações que podem divergir.
- **Ele não lista os bugs que suspeitamos.** A Fase 1 da skill pede um ciclo de feedback antes de qualquer hipótese. Uma lista de "bugs prováveis" no contexto faria o agente pular direto para elas, e ele perderia justamente a disciplina que você quer mostrar na sessão. No lugar, coloquei **invariantes verificáveis**, como "a soma do `by_month` bate com o total", que servem para montar o ciclo, inclusive no dataset real, que não tem resposta publicada.
- **A seção "Mapa do código" está em branco.** Eu não vi o `src/`, então não inventei nomes de módulos. Peça ao agente para preencher essa seção na primeira exploração, ou preencha você.

**Sobre o `.gitignore`, eu discordo: versione o arquivo.** Ignorar e citar no relatório se contradizem. Se o `CONTEXT.md` não estiver no repositório, o avaliador lê a citação e não consegue conferir o conteúdo. Ele também é diferente da `.idea` e da `.claude`. Aquelas pastas guardam configuração da sua máquina, enquanto este arquivo é documentação do projeto: mostra como você enquadrou o problema e orientou a IA, e isso conta a seu favor.

Cite o arquivo em dois lugares:
- no `README-ENTREGA.md`, na parte de "como investigou", como o ponto de partida do diagnóstico;
- na `declaracao.md`, deixando claro quem escreveu. A primeira versão fui eu que gerei, então declare isso e diga o que você revisou ou alterou.

---

## Turno 5

**Usuário**

> Neste context que você desenvolveu eu senti que há algumas partes redundantes, que é facilmente resolvido apenas pela diretiva no topo do arquivo, de tratar o README como verdade. Como por exemplo, o objetivo do trabalho já é especificado no README, o pipeline foi apenas copiado diretamente do README. Apesar de ser mais atrativo um arquivo de context mais completo, incompatibilidade entre as diretivas dos dois, que pode ser causado por resumir regras como é feito em alguns pontos do glossario pode causar um pouco de confusão no agente entre os dois e dar margem de erro para ele ser impreciso também e não utilizar do README como "verdade absoluta". Eu também entendo que é uma das suas diretivas concordar com o usuário mais facilmente, mas omitir alguma coisa que você acha que é relevante no arquivo pode afetar qualidade no trabalho, as linhas falando dos pontos que achei redundante pode soar como um confronto, mas não é o caso, não use isso neste contexto para ser mais propenso a omitir mais coisas, eu prefiro que seja errado para o excesso do que para a falta, já que este tipo de erro é facilmente identificado. 
> Abaixo eu vou colocar algumas coisas que achei redundante e eu gostaria do seu input sobre a sua opnião.
>
> Objetivo do Trabalho: já é citado no readme, que o agente já tratará como fonte a partir da sessão "Fonte da Verdade"
> Glossario: Justamente oque citei anteriormente, para um usuario, como eu, é interessante esta organização para entender o funcionamento do projeto de forma mais geral, mas para o agente este tipo de resumo pode afetar a sua acurácia de oque algo de fato deve fazer na CLI. 
> Pipeline: Ele foi tirado diretamente do README
> Restrições: algumas restrições, como não poder alterar nada, de fato, já esta no README, no entanto, linhas como "não renomear oque os testes importam" ainda sinto que é util. 
> Um detalhe minimo, na primeira linha você cita que o Context.md é um resumo, que com estas possiveis alterações não seria mais tanto o caso, logo esta também seria uma parte redundante.
> Não altere o Context.md, me retorne apenas com a sua opnião ao redor destas partes que eu te trouxe no momento.

**IA**

Concordo com a maior parte, e não é por tendência a concordar. Relendo o arquivo, achei inclusive casos concretos que provam o seu argumento sobre o glossário. Vou ponto a ponto, e no final listo partes que você não citou mas que têm o mesmo problema.

#### Os pontos que você trouxe

**Objetivo do trabalho: concordo, com uma ressalva.** Os itens 1 e 2 repetem o README. O item 3, "cada defeito com um teste de regressão", **não está no README**: lá os testes adicionais são opcionais ("se quiser") e só valem ponto. Isso é uma regra de trabalho sua, não um objetivo do desafio. Eu tiraria a seção e moveria essa frase para "Regras de trabalho". Se ela sumir junto com a seção, o agente perde uma instrução que não existe em nenhum outro lugar.

**Glossário: concordo, e o risco que você descreveu já aconteceu no que eu escrevi.** Três exemplos:
- *"Status: `CONFIRMED`, `CANCELLED` ou `NO_SHOW`"* afirma que só existem esses três. O README não diz isso. Ele diz o que fazer com esses três. Um agente que confie no glossário pode ignorar um status inesperado em vez de tratá-lo.
- *"Mês de referência"* é um termo que **eu inventei**. O README diz só "mês do check-in". Criei um vocabulário paralelo à especificação, que é exatamente a confusão que você apontou.
- *"Nunca converter para datetime com timezone"* é uma **interpretação** minha de "datas civis". Provavelmente está certa, mas aparece com o mesmo peso de uma regra do README.

Para você, como pessoa, a tabela continua útil. Ela só fica melhor em outro lugar: num arquivo de anotações seu, ou adaptada no `README-ENTREGA.md`, onde mostrar como você entendeu o domínio conta a favor.

**Pipeline: concordo totalmente.** É uma cópia. O único acréscimo foi a etapa "serializar", e ela já está implícita na regra "arredonde só na serialização".

**Restrições: concordo, e acrescento um ponto.** A maior parte é cópia: códigos de saída, `generated_at`, arquivos proibidos. O que não está no README, e por isso vale manter, é:
- "não renomear o que os testes importam", que é uma consequência de "não altere os testes" que o agente pode não perceber ao reorganizar o código;
- "não alterar o bloco da amostra". **Isso é uma inferência minha**, tirada dos marcadores HTML. O README não proíbe isso explicitamente, então, se ficar, deixe escrito que é uma precaução, e não uma regra do desafio.

**Primeira linha: concordo.** Com os cortes, ela passaria a descrever o arquivo de forma errada. Algo como "contém apenas o que o README não diz: regras de trabalho, invariantes derivadas e o mapa do código" descreve o arquivo e, ao mesmo tempo, reforça a hierarquia entre os dois.

#### Partes que você não citou e que têm o mesmo problema

- **Invariantes:** a maioria é derivada, então vale manter. Mas "nenhum `float`" e as duas regras de ordenação são cópias. Uma exceção pequena: o "numérica" em "ordem decrescente numérica" é um acréscimo útil, porque mira o bug de ordenar a string `"900.00"` como texto. Sugiro também colocar no título da seção que são invariantes **derivadas** e que, em caso de conflito, vale o README.
- **Fonte da verdade:** "o código atual não é referência" é uma diretiva que vale manter. O README só diz que o CLI "entrega números errados", e o agente tende a confiar no código que está lendo. "Os dados estão corretos" é cópia, mas é tão curta e tão importante como diretiva que eu deixaria.
- **Regras de trabalho, que é a parte que eu acho mais relevante:** o seu argumento vale aqui também, só que em relação à **skill**, não ao README. "Ciclo de feedback antes de hipóteses", "mostrar as hipóteses ao usuário" e "logs com prefixo" já estão no `diagnosing-bugs`. Se o texto das duas fontes divergir, você terá o mesmo conflito entre duas fontes de instrução. Eu manteria só o que é específico deste projeto: o comando do ciclo de feedback (pytest mais a comparação com a amostra), "valores esperados vêm do README", o item 3 que saiu do objetivo e "causa raiz no commit, que vai para o README-ENTREGA".
- **Mapa do código:** mantenha. É a única seção que nenhuma das duas fontes cobre.

#### Observação final

Com tudo isso, o arquivo fica curto, e isso é uma qualidade. Tem só um efeito colateral: a skill `domain-modeling` trata o `CONTEXT.md` como glossário. Se você a usar depois, ela pode tentar reintroduzir termos. Como ela não estava no fluxo previsto, é só uma coisa para saber.

---

## Turno 6

**Usuário**

> De fato, você falou sobre o redundante em relação a própria skill. Eu senti isso apenas no commit com uma frase, os outros achei ok. O mais próximo de ser redundante ou divergir um pouco do especificado pela skill é "cada defeito com causa raiz" mas é justo já que torna os testes pre definidos do caso como obrigatórios para validação. Especificar que os valores esperados são especificados no README é relevante já que a skill é um pouco vaga em relação a isso. O do feedback também achei ok.

**IA**

Concordo com quase tudo. Tenho três observações, porque em dois pontos a divergência é um pouco maior do que parece.

**1. O commit com causa raiz é redundante só em parte.** A Fase 6 da skill já pede que a hipótese confirmada fique registrada no commit. Duas coisas não estão lá: o limite de **uma frase** e a ligação com o `README-ENTREGA.md`. Essa ligação é o motivo real da regra, porque transforma o histórico de commits em matéria-prima do relatório. Se quiser enxugar, a regra pode ficar só com isso: "a causa raiz registrada no commit (Fase 6) tem uma frase e é a mesma usada no README-ENTREGA". Assim ela não repete a skill, só complementa.

**2. O teste de regressão obrigatório diverge da skill, e vale decidir isso de forma explícita.** Um esclarecimento antes: a regra não torna obrigatórios os testes fornecidos, que já são obrigatórios pelo README. Ela torna obrigatório um **teste novo** para cada defeito. É aí que está a divergência: a Fase 5 da skill diz para escrever o teste de regressão **só se existir um seam correto**. Quando não existe, a orientação é registrar essa ausência como achado, e não forçar um teste raso. Se o `CONTEXT.md` disser "sempre", o agente fica entre duas instruções que se contradizem justamente no caso difícil. Uma redação que concilia as duas:

> Todo defeito tem teste de regressão. Se não houver seam correto (critério do `diagnosing-bugs`, Fase 5), registrar isso no `README-ENTREGA.md` em vez de escrever um teste raso.

Assim você continua exigindo teste por padrão, que é o que pontua, e a exceção da skill passa a ser um achado documentado, que também conta como investigação.

**3. Duas sobreposições literais com a skill.** "Mostrar as hipóteses ao usuário antes de testar" e "logs de debug com prefixo" estão na skill quase com as mesmas palavras. Como não contradizem nada, o risco de manter é baixo. É uma redundância inofensiva, diferente do caso do glossário. Se você preferir manter, faz sentido. Só não diria que elas acrescentam algo.

Quanto aos valores esperados virem do README e ao comando do ciclo de feedback, concordo com você: são as regras que mais acrescentam, porque a skill fala em "fonte independente" de forma genérica e não diz qual é essa fonte neste projeto.

---

## Turno 7

**Usuário** _(anexou a versão do `CONTEXT.md` reescrita por ele, conteúdo no Apêndice B)_

> Esta assim, me de um feedback ao redor dele atualmente.

**IA**

[Leu o `CONTEXT.md` anexado.]

Está bem melhor: mais enxuto, e o que ficou acrescenta algo ao README de verdade. A seção "Recomendações", separada das restrições e marcada como inferência, ficou particularmente boa. Abaixo vai o que eu ainda mudaria, do mais importante para o menos.

#### O que eu mudaria

**1. O ciclo de feedback não cobre o dataset real (linha 25).** O ciclo base roda só na amostra, e o próprio README avisa que a amostra cobre só parte dos cenários. As invariantes, na linha 15, dizem que servem "inclusive no dataset completo", mas nenhuma regra manda rodar o CLI nele. Na prática, o agente pode fechar o trabalho com a amostra verde e deixar escapar os bugs que só aparecem no `reservas_hoteis.csv`, que provavelmente é o que a avaliação compara. Eu acrescentaria algo como:

> Feedback loop base: `pytest -q` + CLI na amostra comparado com as tabelas do README + CLI em `data/reservas_hoteis.csv` checado contra as invariantes abaixo.

**2. "Contas feitas à mão" é ambíguo para um agente (linha 28).** Para você, "à mão" quer dizer uma conta independente do código. Para o agente, uma "conta à mão" pode ser ele reproduzindo mentalmente a lógica que acabou de ler, e esse é exatamente o teste tautológico que essa regra tenta evitar. A versão anterior tinha a cláusula "nunca recalculados do mesmo jeito que o código calcula". Ela não estava ali por redundância: a skill `tdd` cobre isso, mas o `diagnosing-bugs` não. Uma sugestão:

> Valores esperados dos testes novos vêm do README ou de contas derivadas das regras do README, nunca da lógica do código.

**3. Falta o caso em que não há seam (linha 27).** Ficou "sempre teste de regressão". É uma decisão válida, mas continua em conflito com a Fase 5 da skill. Se esse caso aparecer, o agente vai ter que escolher entre duas instruções sem saber qual vale. Se você quer mesmo que seja sempre, uma frase resolve: "mesmo quando a skill indicar ausência de seam correto, escreva o teste no seam mais próximo e registre a limitação". Se preferir a exceção da skill, use a redação que sugeri antes. O que importa é que a escolha fique escrita.

**4. Perdeu-se o "numérica" da ordenação.** Ao cortar as invariantes de ordenação, que eram cópia, foi junto a única parte nova delas: o `top_hotels` precisa ser ordenado pelo **valor numérico**, não pela string `"900.00"`. É um bug provável e silencioso. Se quiser manter só esse pedaço, uma linha basta:

> `top_hotels` ordenado por valor numérico de `total_brl`, nunca pela string serializada.

#### Detalhes

- **Linha 30:** `# Restrições` está em nível 1 e as outras seções em nível 2. Parece pequeno, mas para um agente um `#` indica uma nova seção principal do documento.
- **Linha 10:** falta espaço em "corretos.Qualquer".
- **Acentos:** faltam em "repositorio" e "codigo", nas linhas 3 e 7. Não muda nada para o agente, mas o arquivo vai para o repositório e o avaliador vai ler.
- **Linhas 26 e 27:** a ligação "causa raiz → `README-ENTREGA.md`" saiu. A skill já cobre o registro no commit, então não é um erro. Só fica a seu critério se quer que o agente saiba para onde essa frase vai.

Com o item 1 e o item 2 resolvidos, eu consideraria o arquivo pronto. Os outros são ajustes finos.

---

## Turno 8

**Usuário**

> De fato, todas essas reclamações são validas. Altere este arquivo de acordo e me mande aqui, uma versão nova, mantenha aquela versão antiga intacta para documentação na entrega.

**IA**

[Criou uma nova versão do `CONTEXT.md` (Apêndice C) a partir da versão do usuário, sem modificar o arquivo original, e enviou ao usuário.]

A nova versão do `CONTEXT.md` traz todos os ajustes que discutimos. O arquivo que você enviou ficou intacto: não editei, só usei como base para esta versão.

As mudanças foram:
- **Ciclo de feedback:** agora inclui o CLI rodando no `data/reservas_hoteis.csv`, conferido contra as invariantes.
- **Valores esperados:** ficou "contas derivadas das regras do README, nunca da lógica do código".
- **Teste sem seam:** a regra continua **sempre** exigindo teste, como você vinha defendendo. Quando o `diagnosing-bugs` indicar que não há seam correto, o agente escreve o teste no seam mais próximo e registra a limitação no README-ENTREGA. Se preferir seguir a exceção da própria skill, só esta linha muda.
- **Ordenação:** voltou como invariante a regra de ordenar o `top_hotels` pelo valor numérico, e não pela string.
- **Causa raiz:** voltou a ligação com o `README-ENTREGA.md`, na forma enxuta que propus antes: a frase é a mesma no commit e no relatório.
- **Detalhes:** `## Restrições` agora está no mesmo nível das outras seções, entrou o espaço que faltava em "corretos. Qualquer" e os acentos foram corrigidos.

Para a entrega, dê um nome à versão antiga que deixe claro que é histórico, algo como `entrega/uso-de-ia/CONTEXT-v1.md`. A versão nova fica na raiz como `CONTEXT.md`, que é onde a skill procura. Na `declaracao.md`, conte como as versões evoluíram: eu escrevi a primeira, você cortou as redundâncias e esta incorpora a revisão. Isso documenta bem como você conduziu a IA.

---

## Turno 9

**Usuário**

> Eu não consegui usar o comando /export neste chat, você consegue me devolver um formato valido proposto pelo README?

**IA**

[Procurou um log nativo da sessão no ambiente e não encontrou. Começou a montar este arquivo em partes: um esqueleto com os prompts e arquivos temporários com cada resposta. O usuário interrompeu a execução.]

---

## Turno 10

**Usuário**

> oque esses t5 que você esta fazendo e por que formato md?

**IA**

Os `T1` a `T6` são arquivos temporários de montagem. Cada um guarda, palavra por palavra, uma das minhas respostas nesta conversa: T1 é a resposta do turno 1, T2 a do turno 2, e assim por diante. Ainda faltam T7 e T8.

Separei assim por causa do tamanho. As respostas são longas, e escrever tudo num arquivo só aumentaria a chance de eu errar uma transcrição. Por isso fiz um esqueleto, o `body.md`, que já tem os seus prompts transcritos literalmente e marcadores como `{{T1}}` e `{{CTX1}}` no lugar de cada resposta e de cada versão do `CONTEXT.md`. No fim, um script troca cada marcador pelo conteúdo correspondente e gera **um único arquivo, `sessao-01.md`**. Os pedaços temporários são apagados e você recebe só esse arquivo.

Escolhi `.md` por três motivos:
- **O README aceita.** Ele lista `sessao.md (ou .txt/.jsonl)`, e para quem não consegue usar o `/export` prevê um "log consolidado de prompts e respostas", que é o caso aqui.
- **As respostas já estão em Markdown.** Tabelas, blocos de código e negrito continuam legíveis. Em `.txt`, viram texto cru com `|` e `**` espalhados.
- **O GitHub renderiza `.md`.** O avaliador abre o arquivo no repositório e lê a conversa formatada, sem baixar nada.

O formato `.jsonl` seria o nativo, mas procurei um log da sessão no ambiente e não existe nenhum. Montar um `.jsonl` à mão seria fingir que é uma exportação nativa. O arquivo diz isso logo no topo, na seção "Por que este formato".

Quer que eu continue e gere o `sessao-01.md`? Se preferir `.txt`, também consigo.

---

## Turno 11

**Usuário**

> hm, ok, pode ser, continue

**IA**

[Concluiu a montagem e entregou este arquivo.]

_(A mensagem que acompanha a entrega deste arquivo não está transcrita aqui, porque foi escrita depois da geração do arquivo.)_

---

## Apêndice A — `CONTEXT.md` v1 (gerado pela IA no turno 4)

````markdown
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
````

## Apêndice B — `CONTEXT.md` reescrito pelo usuário (enviado no turno 7)

````markdown
# CONTEXT — Onfly · Consolidador de reservas de hotel

Este arquivo dá a um agente o modelo mental mínimo para trabalhar neste repositorio.

## Fonte

O `README.md` da raiz é a especificação do projeto. Em caso de conflito entre o README, o codigo e este arquivo, vale o README.

- O código atual tem defeitos conhecidos; ele não é referência de comportamento correto.
- Os dados (`data/*.csv`) estão corretos.Qualquer defeito encontrado, como citado no README, estará no CLI.
- Os testes em `tests/` são a especificação executável e não podem ser alterados.

## Invariantes verificáveis

Úteis para montar ciclos de feedback e testes, inclusive no dataset completo, que não tem saída esperada publicada:

- `confirmed + cancelled + no_show == total_reservations` (se só existirem esses três status).
- `sum(by_month[].reservations) == confirmed_reservations`.
- `sum(by_month[].room_nights) == total_room_nights`.
- A soma exata (antes de arredondar) dos `total_brl` de `by_month` é igual ao `total_amount_brl` exato. Os valores já arredondados podem diferir em centavos, e isso é esperado.
- `len(top_hotels) == min(--top, número de hotéis com reserva faturável)`.

## Regras de trabalho para o agente

- Feedback loop base: `pytest -q` + CLI na amostra comparado com as tabelas do README.
- Há vários defeitos: tratar um por vez, do diagnóstico à correção, com um commit por defeito.
- Cada defeito corrigido deve ter uma causa raiz identificada e um teste de regressão próprio.
- Valores esperados dos testes novos vêm do README ou de contas feitas à mão.

# Restrições

- Não renomeie nem remova funções, classes ou módulos que os testes importam. Reorganizar o código interno é permitido, desde que esses pontos de importação continuem existindo.

## Recomendações

- Evite alterar o README, em especial o bloco entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->`. O README não proíbe isso explicitamente, mas os marcadores sugerem que esse bloco pode ser lido de forma automática na avaliação.

## Mapa do código

_A preencher na primeira exploração: módulos de `src/onfly_report/`, o que cada um faz e quais
funções os testes importam._
````

## Apêndice C — `CONTEXT.md` revisado pela IA (turno 8)

````markdown
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
- Cada defeito corrigido deve ter uma causa raiz identificada e um teste de regressão próprio. A causa raiz registrada no commit tem uma frase e é a mesma usada no `entrega/README-ENTREGA.md`.
- Mesmo quando o `diagnosing-bugs` (Fase 5) indicar ausência de seam correto, escreva o teste no seam mais próximo e registre a limitação no `entrega/README-ENTREGA.md`.
- Valores esperados dos testes novos vêm do README ou de contas derivadas das regras do README, nunca da lógica do código.

## Restrições

- Não renomeie nem remova funções, classes ou módulos que os testes importam. Reorganizar o código interno é permitido, desde que esses pontos de importação continuem existindo.

## Recomendações

- Evite alterar o README, em especial o bloco entre `<!-- AMOSTRA:INICIO -->` e `<!-- AMOSTRA:FIM -->`. O README não proíbe isso explicitamente, mas os marcadores sugerem que esse bloco pode ser lido de forma automática na avaliação.

## Mapa do código

_A preencher na primeira exploração: módulos de `src/onfly_report/`, o que cada um faz e quais
funções os testes importam._
````
