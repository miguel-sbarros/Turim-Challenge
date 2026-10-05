# Observações sobre a planilha de retornos

Dedução a partir dos dados, **não escrita no kit**. Confirmar antes de usar no prompt.

- Colunas reais (linha 7): Data, SPX – Retorno Total, IBOV – Retorno Total, USDBRL, SOFR Proxy, CDI. São 260 meses, de 2005-01 a 2026-08 (a linha 2004-12 está vazia).
- **A coluna IBOV parece estar em US$.** Convertida por (1+IBOV)×(1+USDBRL)−1, set/2008 dá −11,7% e out/2008 dá −24,0%, que batem com o Ibovespa em reais. Sem conversão, dão −24,3% e −33,0%. Na série toda: coluna crua 5,91% a.a. e drawdown de 77,4% (mai/2008 → jan/2016); convertida, 9,23% a.a. e drawdown de 49,8%.
- Anualizados: CDI 10,72%, SOFR 1,78%, SPX 10,98% (US$), USDBRL 3,14%.
- O drawdown "da série histórica" que o Andar 4 cobra depende dessa convenção, e de a carteira offshore ser medida em US$ ou em R$. O kit não diz qual é. O simulador reporta todas as leituras.
