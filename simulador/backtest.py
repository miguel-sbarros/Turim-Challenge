"""Drawdown maximo de uma carteira de duas classes com rebalanceamento mensal,
sobre a planilha do kit (material/retornos-mensais-2005-2026.xlsx).

Colunas da planilha: Data, SPX, IBOV, USDBRL, SOFR Proxy, CDI (retornos mensais).
A convencao que o Juiz usa nao esta escrita no kit: aqui sao reportadas as duas
leituras plausiveis para offshore (em US$ e convertida para R$).
"""
from functools import lru_cache
from pathlib import Path

import openpyxl

PLANILHA = Path(__file__).parent.parent / "00_kit-original/material/retornos-mensais-2005-2026.xlsx"


@lru_cache(maxsize=1)
def serie():
    ws = openpyxl.load_workbook(PLANILHA, data_only=True, read_only=True).active
    linhas = []
    for r in ws.iter_rows(values_only=True):
        if hasattr(r[0], "year") and all(v is not None for v in r[1:6]):
            linhas.append(dict(data=r[0], spx=r[1], ibov=r[2], usdbrl=r[3], sofr=r[4], cdi=r[5]))
    return linhas


def drawdown_max_pct(retornos):
    valor, pico, pior = 1.0, 1.0, 0.0
    for r in retornos:
        valor *= 1 + r
        pico = max(pico, valor)
        pior = min(pior, valor / pico - 1)
    return round(-pior * 100, 2) + 0.0


def drawdowns(mercado, renda_fixa_pct, renda_variavel_pct):
    """Devolve {leitura: drawdown_%} para os pesos dados."""
    wf, wv = renda_fixa_pct / 100, renda_variavel_pct / 100
    s = serie()
    if mercado == "onshore":
        # A coluna IBOV se comporta como IBOV em US$ (ver 03_backtest/observacoes.md):
        # reporta a coluna crua e a convertida para R$ pelo USDBRL.
        ibov_brl = [(1 + m["ibov"]) * (1 + m["usdbrl"]) - 1 for m in s]
        return {"CDI+IBOV coluna crua": drawdown_max_pct([wf * m["cdi"] + wv * m["ibov"] for m in s]),
                "CDI+IBOV convertido p/ R$": drawdown_max_pct([wf * m["cdi"] + wv * i for m, i in zip(s, ibov_brl)])}
    usd = [wf * m["sofr"] + wv * m["spx"] for m in s]
    brl = [(1 + r) * (1 + m["usdbrl"]) - 1 for r, m in zip(usd, s)]
    return {"US$ (SOFR+SPX)": drawdown_max_pct(usd), "R$ (SOFR+SPX convertido)": drawdown_max_pct(brl)}


if __name__ == "__main__":
    s = serie()
    print(f"{len(s)} meses: {s[0]['data']:%Y-%m} a {s[-1]['data']:%Y-%m}")
    for mercado in ("onshore", "offshore"):
        for rv in (0, 10, 20, 30, 50, 100):
            print(mercado, f"RV {rv:3d}%", drawdowns(mercado, 100 - rv, rv))
