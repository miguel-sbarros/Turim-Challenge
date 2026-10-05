# Andar 3 — quanto dá para gastar por ano, para sempre

Teto de saída: 700 tokens.

Método, nesta ordem:

1. Declarar a premissa de retorno nominal (`retorno_nominal_premissa_pct`) a
   partir das classes e retornos de `premissas`.
2. Venda da fazenda: ganho de capital = valor de venda menos custo de
   aquisição; imposto = 15% do ganho; `produto_liquido_venda` = valor de venda
   menos o imposto.
3. Renda perpétua real: retorno nominal, menos 15% de imposto sobre o
   resultado, descontada a inflação da moeda; aplicar sobre o patrimônio
   investível. A renda perpétua tem de ser coerente com a premissa declarada
   no passo 1.
4. Comparar a renda perpétua com o gasto da família para decidir
   `venda_fazenda_recomendada`.
5. Perfis e exposição offshore de pai e filha: só a partir do que a família
   respondeu; sem resposta, não supor o rótulo.
6. `justificativa`: as contas dos passos 2 e 3 em uma linha cada.
