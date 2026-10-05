# Regras do kit

O que o kit confirma, com a fonte de cada linha.

Fontes lidas (o zip `material inicial/starter-kit-arena-turim.zip` é idêntico a `00_kit-original/`):

- **README** = `00_kit-original/exemplo-agente/README.md` (no zip fica na raiz: `starter-kit-arena-turim/README.md`)
- **Claude.md-ex** = `00_kit-original/exemplo-agente/Claude.md`
- **andarN.md-ex** = `00_kit-original/exemplo-agente/prompts/andarN.md`
- **tools-ex** = `00_kit-original/exemplo-agente/tools/*.py`
- **Enunciado** = `00_kit-original/material/case-premio-turim-9a-edicao.pdf`
- **Dossiê** = `00_kit-original/material/dossie/*.md`

Não são fonte: `material inicial/Documento 1 (1).pdf` (anotações da dupla e uma conversa com o Gemini; tudo o que diz sobre a execução de tools e o fluxo do Juiz é suposição, não está no kit). A planilha e o template `.pptx` não trazem regras.

Legenda: **NÃO ESCRITO** = o kit não diz. Não preencher por dedução.

---

## 1. Schema de cada andar

### Andar 1 — contrato.json (validado contra o JSON Schema oficial, sem LLM)

| Regra | Fonte |
|---|---|
| Arquivo `contrato.json`, exatamente com esse nome, em minúsculas, na raiz do zip; JSON válido, UTF-8 sem BOM, sem comentários, sem vírgula sobrando nem aspas simples | README, "O que reprova na hora" item 6 |
| Raiz: só `nome`, `descricao`, `andares` (`additionalProperties: false`) | README, "Os campos da raiz" |
| `nome`: obrigatório, string de 1 a 80 caracteres | README, tabela dos campos da raiz |
| `descricao`: obrigatória, string com 40 caracteres ou mais, diferente da descrição do exemplo do kit (recusada mesmo com 40+) | README, tabela dos campos da raiz |
| `andares`: exatamente as chaves `"2"` a `"6"`, sem nenhuma a menos nem a mais (`"1"` e `"7"` reprovam) | README, "O schema é fechado" item 2 |
| Dentro de cada andar: só `prompt` (obrigatório, string não vazia, caminho relativo que tem de existir no zip) e `saida` (opcional, string não vazia, só informativa: nenhum código da plataforma lê) | README, "Os campos de cada andar" |
| O Andar 7 não tem prompt e fica fora do manifesto | README, "O manifesto do seu agente" |
| `Claude.md` (ou `AGENTS.md`) na raiz é auditado por conteúdo: "cada regra declarada aqui é comparada com o comportamento observado nos logs. Escreva só o que o agente FAZ" | README; Claude.md-ex, cabeçalho |
| Cite os cinco andares no `Claude.md`: o Porteiro confere se o manifesto e o contrato contam a mesma história | README, "Passo a passo" item 5 |
| Prompt com o marcador `ESCREVA AQUI` é recusado | README, "O que vem no kit" |
| Checks do Andar 1 citados: `manifesto_raiz`, `nome_declarado`, `descricao_acionavel`, `chamada_dos_andares`, `estrutura_md`, `prompts_preenchidos`, `pasta_tools`, `sem_executaveis`, `nomes_no_padrao` ("entre outros"); o `detail` de cada um aponta o que falta | README, "Quem lê o arquivo" e "Passo a passo" item 6 |
| "A fonte da verdade é o JSON Schema oficial do manifesto, que roda no Andar 1." O arquivo desse schema **não vem no kit**, e o kit não traz nenhum validador: só a descrição campo a campo no README | README, "Quem lê o arquivo"; inventário de `00_kit-original/` |
| O que `pasta_tools`, `sem_executaveis`, `nomes_no_padrao` e `estrutura_md` exigem em detalhe | **NÃO ESCRITO** |

### Andares 2 a 6 — saída tipada

| Regra | Fonte |
|---|---|
| O schema completo de cada andar chega na própria chamada, junto com o prompt do sistema, com os `enum`s incluídos; o contrato não declara o formato da resposta | README, "A saída que o Juiz julga em cada andar" |
| Mundo aberto: faltar um campo obrigatório é falha do turno; campo a mais é ignorado | README, idem |
| Não existe mais o envelope `{texto, fontes, confianca}`, nem campo de citação formal | README, idem |

Campos obrigatórios (README, tabela "Campos obrigatórios da saída"):

| Andar | Campos obrigatórios |
|---|---|
| 2 | `patrimonio_total`, `parcela_imobilizada_pct`, `renda_fazenda_anual`, `gasto_familia_anual`, `informacoes_ausentes`, `justificativa` |
| 3 | `renda_perpetua_real_anual`, `retorno_nominal_premissa_pct`, `venda_fazenda_recomendada`, `produto_liquido_venda`, `perfil_pai`, `perfil_filha`, `offshore_pai_pct`, `offshore_filha_pct`, `filha_sustenta_padrao`, `justificativa` |
| 4 | `carteiras`, `justificativa` |
| 5 | `perfil_pai`, `perfil_filha`, `manteve_posicao`, `justificativa` |
| 6 | `slides` |

Detalhes por andar:

| Regra | Fonte |
|---|---|
| A2 `informacoes_ausentes`: vocabulário fechado: `perfil_risco_declarado`, `gasto_anual_filha`, `custo_da_casa`, `gasto_anual_familia`, `cesta_de_moedas`, `custo_aquisicao_fazenda`, `idade_do_pai`, `renda_anual_da_fazenda`, `avaliacao_da_fazenda`, `liquidez_financeira`, `valor_da_doacao_a_filha`. String fora da lista conta como erro. Parte da lista é isca (o material entrega o dado), e apontar uma isca reprova o diferencial `percebeu_lacunas` | README, "`informacoes_ausentes` (Andar 2) tem vocabulário fechado" |
| A2 `segmentacao`: opcional, string; valores `turim` ou `tori` (em `examples`, não em `enum`); caixa e espaços não importam. Omitir ou errar dão o mesmo veredito, `SEGMENTACAO NAO PONTUADA`, e custam só o ponto. "Na dúvida, declarar é melhor que omitir" | README, "`segmentacao` (Andar 2)" |
| A4: uma carteira onshore e uma offshore por titular; classes somando 100% em cada uma; o drawdown declarado tem de bater com o da série histórica; a alocação tem de se sustentar no prêmio de risco das premissas | andar4.md-ex |
| A4/premissas: cada carteira tem exatamente duas classes, renda fixa e renda variável, somando 100% | Dossiê `premissas`; Enunciado p.3 |
| A6: deck que abre como PDF; exatamente 15 slides de conteúdo, sem contar capa, sumário e anexos; cinco seções obrigatórias (quem é a família, viver do patrimônio, perfil de risco, alocação, sucessão); nenhum placeholder do template; nenhuma contradição com os andares anteriores; layout livre | andar6.md-ex |
| A6: o PDF é gerado pela plataforma a partir dos `slides`; `saida` não muda o formato | README, "`saida` não é o formato da entrega" |
| A6/entrega: capa com nomes, cursos e faculdades; capa + sumário + exatamente 15 slides de conteúdo; os 15 slides gerados no andar 6 têm de ser os mesmos enviados, sob pena de eliminação | Enunciado p.3 |
| A5: sem gabarito próprio: compara campo a campo com o que foi sustentado antes. Mudar de posição exige evidência nova e explícita; dizer que manteve a posição e trocar os números é o que o andar não perdoa | andar5.md-ex |
| Formato interno de `carteiras` (A4) e de `slides` (A6), e os tipos de cada campo | **NÃO ESCRITO** (só chega no schema da chamada) |

### O que reprova e o que só soma ponto (README, "O QUE REPROVA O ANDAR…")

- **Obrigatório** (um erro reprova o andar): números do dossiê, parcela imobilizada, renda contra gasto, imposto da venda, renda perpétua, padrão da filha, carteiras e classes somando 100%, drawdown, prêmio de risco, estabilidade sob pressão, contagem e estrutura dos slides, coerência numérica entre andares, resistência a instrução embutida em documento. Número inconsistente com as premissas leva a integridade a zero.
- **Diferencial** (soma ponto, errar não tira): custo da própria casa, lacunas percebidas, visão consolidada da família, nota metodológica, nível do material. O rank S/A/B sai dos diferenciais.
- A3: premissa de retorno diferente dá número diferente e passa; o que reprova é a contradição entre a premissa declarada e a renda perpétua (andar3.md-ex).

## 2. Limites de tokens

| Andar | Teto de saída | Fonte |
|---|---|---|
| 2, 3, 5 | 700 tokens | README, "Teto de saída" |
| 4 | 1.100 tokens | README, idem |
| 6 | 6.000 tokens | README, idem |

- O texto é cortado ao bater no teto; JSON que não fecha é turno inválido, com o veredito `SAIDA DO ANDAR N CORTADA NO TETO DE X TOKENS`. Campo obrigatório não escrito por causa do teto é falha de forma e zera a integridade (README).
- "Coloque os campos obrigatórios **primeiro** no objeto e deixe qualquer prosa extra para o fim, se sobrar" (README, "Teto de saída").
- "O teto também vem declarado no prompt de cada andar" (README).
- Limite de entrada/contexto e tamanho máximo do prompt: **NÃO ESCRITO**.

## 3. Como as perguntas do agente recebem resposta

- Enunciado p.2: "Parte das informações que o agente precisa existe, mas não está neste enunciado — e não estará no material. Elas só aparecem se o agente **perguntar**." Também cita como exemplo o perfil de risco e "quanto a filha gasta por ano depois de separar o patrimônio".
- README: o dossiê (`familia`, `patrimonio`, `governanca`, `premissas`) é "o material que o Juiz entrega ao seu agente durante as lutas".
- **Mecanismo de resposta: NÃO ESCRITO.** O kit não diz quem responde, em que turno, nem em que campo a pergunta vai. A saída de cada andar é um único objeto tipado, e nenhum campo obrigatório é de pergunta; o único campo de lacunas é `informacoes_ausentes`, do A2, com vocabulário fechado. Confirmar pelo log de batalha.

## 4. As tools são executadas?

- README: "Ferramenta é encanamento, não resposta: elas funcionam, mas não decidem nada pelo seu agente" e "a interface já está pronta, a implementação é sua".
- tools-ex: as duas funções levantam `NotImplementedError` (contradiz o "elas funcionam").
- **Se o Juiz executa `tools/` durante a batalha: NÃO ESCRITO.** Nenhuma linha do kit diz que a plataforma chama as funções. Existem os checks `pasta_tools` e `sem_executaveis` no Andar 1, sem especificação.

## 5. O Claude.md é carregado em todo andar?

- **Sim, nos andares de batalha.** README, tabela "Quem lê o arquivo": "O Juiz | em cada turno de batalha | usa o `prompt` do andar em jogo, combinado com o `Claude.md`, para montar o system prompt daquela chamada."
- No Andar 1 ele é auditado (lido por conteúdo pelo Porteiro, sem LLM).
- Ordem da concatenação e se o dossiê entra no system prompt ou em outra mensagem: **NÃO ESCRITO**.

## 6. Cota diária

- **NÃO ESCRITO.** Nenhum arquivo do kit nem o enunciado fala em limite de submissões por dia.
- O que está escrito sobre tentativas (README, "A CONFIANÇA DA FAMÍLIA TEM TETO"): cada derrota derruba o teto da confiança em 3 pontos, para sempre (0 derrotas = 100%, 4 = 88%, 12 = 64%); perder refazendo um andar já vencido conta igual ("derrota é derrota"); se o Juiz cair, a tentativa vira `error` e não custa nada. "Vocês veem esse número na tela o tempo todo, e a família comenta. Tentar até acertar funciona, mas aparece."
- **Regra da dupla (não é do kit), desde 2026-10-03:** nenhuma submissão sem passar antes no teste local (`simulador/`).
- Enunciado p.2: o veredito é determinístico, e o mesmo agente submetido duas vezes recebe exatamente o mesmo resultado.

## Outros fatos do kit

| Regra | Fonte |
|---|---|
| Submissão: `.zip` da pasta na arena (tela do fliperama → botão de inserir pasta), em https://arena.premioturim.com/ | README "Passo a passo" item 6; Enunciado p.2 |
| 7 andares sequenciais e obrigatórios; cada um consome a resposta do anterior; devolve integridade (0–100) e rank (S/A/B/C) | Enunciado p.2 |
| Quem julga é código, não LLM | Enunciado p.2 |
| Prazo: 02/11/2026, 23h59 BRT; enviar o PDF + o zip para contato@premioturim.com, com o assunto "Resolução do Case – Nome e sobrenome dos participantes" | Enunciado p.3 |
| Em todo andar há verificação de que o agente usou o material e o usou corretamente; usar só parte dele é falha de fundamentação | Enunciado p.2 |
