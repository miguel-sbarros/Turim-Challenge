# Diário de submissões

Regra da dupla desde 2026-10-03: nenhuma submissão na Arena sem passar antes no teste local
(`simulador/porteiro.py` para o Andar 1, `simulador/simular.py` para os Andares 2–6). Cada derrota
tira 3 pontos do teto de confiança para sempre, inclusive refazendo andar já vencido (README).

## Versões

| versão | data | o que mudou | sha256 do zip |
|---|---|---|---|
| v1 | 2026-10-03 | esqueleto: contrato com descrição própria, Claude.md do case, prompts 2–6 sem `ESCREVA AQUI`, tools do kit sem alteração. Zip: `05_submissoes/zips/agente_v1.zip` | `90b5ca068c1a…` |

## Rodadas locais

Linhas dos Andares 2–6 são acrescentadas automaticamente pelo `simulador/simular.py`.

| data | agente | modelo / teste | resultado | pasta |
|---|---|---|---|---|
| 2026-10-03 | v1 (sha256 `90b5ca068c1a`) | `porteiro.py` (Andar 1, regras escritas) | PASSA; avisos: `pasta_tools`, `sem_executaveis`, `nomes_no_padrao`, `estrutura_md` sem regra escrita | — |
<!-- rodadas-locais -->

## Submissões na Arena

Preencher a cada envio, com o log completo do Juiz. Os checks que aparecerem vão para `01_regras/checks.md`.

| data | versão | andar | resultado | derrotas acumuladas | teto de confiança | o que o Juiz disse |
|---|---|---|---|---|---|---|
