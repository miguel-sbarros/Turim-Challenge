# Simulador local

Regra da dupla: nenhuma submissão na Arena sem passar aqui antes.

## Andar 1

```
.venv/bin/python porteiro.py ../05_submissoes/zips/agente_vN.zip
```

Confere o zip contra `schemas/contrato.schema.json`, transcrito do README do kit (o schema oficial não vem no kit), e contra as regras escritas: arquivo na raiz, sem BOM, prompts existentes, sem `ESCREVA AQUI`, Claude.md citando os cinco andares. Os checks sem regra escrita (`pasta_tools`, `sem_executaveis`, `nomes_no_padrao`, `estrutura_md`) saem como AVISO.

## Andares 2 a 6

```
export ANTHROPIC_API_KEY=...
.venv/bin/python simular.py --agente ../05_submissoes/zips/agente_vN.zip --andares 2,3,4
.venv/bin/python simular.py --agente ... --andares 2,3,4,5 --contestacao ../04_testes/contestacao1.txt
.venv/bin/python simular.py --agente ... --respostas exemplos/certo --nao-registrar   # offline, sem API
```

Teste sempre o **zip** que vai ser submetido, não a pasta. Cada rodada grava `rodadas/<data-hora>/` com a chamada exata (`andarN_chamada.json`), a resposta crua e o `relatorio.md`, e acrescenta uma linha em `05_submissoes/diario.md`. A torre para no primeiro andar reprovado.

Checks:

| tipo | o que reprova |
|---|---|
| FORMA | resposta cortada no teto (`stop_reason = max_tokens`), JSON que não fecha, obrigatório ausente, obrigatórios fora das primeiras posições (essa última é regra local: o kit só recomenda) |
| OBRIGATORIO | números contra `02_gabarito/gabarito.json`; soma 100%; drawdown contra a planilha (±0,5 p.p.); 4 carteiras; 15 slides de conteúdo, capa, sumário, cinco seções, sem placeholder |
| DIFERENCIAL | só informa: vocabulário fechado, iscas e lacunas reais de `informacoes_ausentes`, `segmentacao` |

AVISO = não dá para decidir com o que está escrito; conferir a mão.

`exemplos/` traz respostas escritas à mão para autotestar os checks (`certo` passa; `errado`, `cortado` e `extra_primeiro` reprovam).

## O que o simulador supõe e o kit não escreve

1. **Modelo:** o kit não diz qual modelo o Juiz usa. O padrão é `claude-sonnet-4-6`, porque aceita `temperature=0`; os modelos 5.5 recusam esse parâmetro. Troque com `--modelo`.
2. **Montagem:** system = Claude.md + prompt do andar + schema + teto, nessa ordem. O kit confirma só que o Juiz combina o prompt do andar com o Claude.md e manda o schema junto.
3. **Dossiê e andares anteriores:** vão na mensagem do usuário. O kit diz que cada andar consome a resposta do anterior, mas não diz como.
4. **Perguntas do agente:** a chamada tem uma rodada só; ninguém responde perguntas. O mecanismo não está escrito.
5. **Tools:** não são executadas. Não está escrito que o Juiz as executa.
6. **Schemas:** só os `required`, o vocabulário fechado e o `segmentacao` vêm do kit. Tipos e formato de `carteiras` e `slides` são palpite (`$comment` em cada arquivo).
7. **Unidade:** reais ou R$ milhões são aceitos, com AVISO.
8. **Drawdown:** a coluna IBOV da planilha parece estar em US$ (`03_backtest/observacoes.md`). O check aceita tanto a leitura crua quanto a convertida, e o offshore em US$ ou em R$.
9. **Andar 5:** sem arquivo de contestação, o andar é pulado (`04_testes/contestacoes.md` está vazio).
