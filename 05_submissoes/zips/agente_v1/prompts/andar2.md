# Andar 2 — quem é o cliente, em números

Teto de saída: 700 tokens.

Método:

1. Ler `patrimonio` e `familia` inteiros antes de escrever qualquer número.
2. `patrimonio_total`: soma dos ativos listados em `patrimonio`.
3. `parcela_imobilizada_pct`: valor dos ativos não financeiros dividido por
   `patrimonio_total`, em porcentagem.
4. `renda_fazenda_anual` e `gasto_familia_anual`: os valores anuais escritos
   no material, sem ajuste.
5. `informacoes_ausentes`: só itens do vocabulário fechado do schema, e só os
   que o material de fato não traz. Antes de incluir um item, conferir se ele
   aparece em algum documento; se aparece, ele fica de fora.
6. `justificativa`: uma ou duas frases com a conta da parcela imobilizada e a
   comparação entre renda e gasto.
