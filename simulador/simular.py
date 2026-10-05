"""Simulador local do Juiz, andares 2 a 6.

Monta cada chamada como o README do kit descreve: system prompt = Claude.md +
prompt do andar (+ schema do andar e teto), material = material/dossie/,
max_tokens = teto do andar, temperatura 0. Depois confere a saida:

  FORMA       JSON fecha; nao cortado no teto; campos obrigatorios presentes e primeiro
  OBRIGATORIO numeros contra 02_gabarito/gabarito.json e regras de cada andar
  DIFERENCIAL vocabulario fechado e iscas de informacoes_ausentes, segmentacao

O que o kit NAO escreve e este simulador supoe (ver README.md desta pasta):
modelo do Juiz, ordem de montagem do system prompt, como o dossie e a resposta
do andar anterior chegam (aqui: na mensagem do usuario), formato interno de
carteiras/slides, unidade dos valores.

Uso:
  .venv/bin/python simular.py --agente ../05_submissoes/zips/agente_v1.zip --andares 2,3
  .venv/bin/python simular.py --respostas exemplos/andar2_ok   # offline, sem API
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import jsonschema

import backtest

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
DOSSIE_PADRAO = RAIZ / "00_kit-original/material/dossie"
GABARITO = json.loads((RAIZ / "02_gabarito/gabarito.json").read_text())
DIARIO = RAIZ / "05_submissoes/diario.md"
TETOS = {2: 700, 3: 700, 4: 1100, 5: 700, 6: 6000}  # README, "Teto de saida"
MODELO_PADRAO = "claude-sonnet-4-6"  # aceita temperature=0; o modelo do Juiz nao esta escrito
SCHEMAS = {n: json.loads((AQUI / f"schemas/andar{n}.schema.json").read_text()) for n in TETOS}
VOCAB = SCHEMAS[2]["properties"]["informacoes_ausentes"]["items"]["enum"]


# ---------------------------------------------------------------- agente

class Agente:
    """Le o agente de uma pasta ou de um .zip (o mesmo arquivo que sera submetido)."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        if self.caminho.suffix == ".zip":
            self._z = zipfile.ZipFile(self.caminho)
            self.versao = self.caminho.stem + " sha256:" + hashlib.sha256(self.caminho.read_bytes()).hexdigest()[:12]
        else:
            self._z = None
            self.versao = f"pasta {self.caminho.name} (nao zipada)"
        self.contrato = json.loads(self.ler("contrato.json"))
        self.manifesto = self.ler("Claude.md") if self.existe("Claude.md") else self.ler("AGENTS.md")

    def existe(self, nome):
        return nome in self._z.namelist() if self._z else (self.caminho / nome).exists()

    def ler(self, nome):
        return self._z.read(nome).decode("utf-8") if self._z else (self.caminho / nome).read_text(encoding="utf-8")

    def prompt(self, andar):
        return self.ler(self.contrato["andares"][str(andar)]["prompt"])


def montar_system(agente, andar):
    schema = {k: v for k, v in SCHEMAS[andar].items() if not k.startswith("$")}
    return (f"{agente.manifesto}\n\n{agente.prompt(andar)}\n\n"
            f"## Schema da saida do Andar {andar}\n"
            f"Responda com um unico objeto JSON neste schema. Teto de saida: {TETOS[andar]} tokens.\n"
            f"```json\n{json.dumps(schema, ensure_ascii=False, indent=1)}\n```")


def montar_usuario(dossie_dir, anteriores, andar, contestacao):
    partes = ["Documentos recebidos:"]
    for doc in sorted(Path(dossie_dir).glob("*.md")):
        partes.append(f'<documento id="{doc.stem}">\n{doc.read_text(encoding="utf-8").strip()}\n</documento>')
    if anteriores:
        partes.append("Suas respostas nos andares anteriores:")
        for n, saida in sorted(anteriores.items()):
            partes.append(f'<andar n="{n}">\n{json.dumps(saida, ensure_ascii=False)}\n</andar>')
    if andar == 5 and contestacao:
        partes.append(f"Contestacao:\n{contestacao}")
    partes.append(f"Responda o Andar {andar}.")
    return "\n\n".join(partes)


def chamar(cliente, modelo, system, usuario, teto):
    import anthropic
    try:
        # SDK 1.x tirou temperature da assinatura; vai em extra_body (aceito por Sonnet/Opus 4.6 e Haiku 4.5)
        r = cliente.messages.create(model=modelo, max_tokens=teto, system=system,
                                    messages=[{"role": "user", "content": usuario}],
                                    extra_body={"temperature": 0})
    except anthropic.BadRequestError as e:
        sys.exit(f"400 do modelo {modelo} (temperature=0 e rejeitado nos modelos 5.5): {e.message}")
    except anthropic.AuthenticationError:
        sys.exit("Credencial invalida: defina ANTHROPIC_API_KEY.")
    except anthropic.APIConnectionError as e:
        sys.exit(f"Sem conexao com a API: {e}")
    except anthropic.RateLimitError as e:
        sys.exit(f"429 limite de taxa: {e.message}")
    texto = "".join(b.text for b in r.content if b.type == "text")
    return texto, r.stop_reason, r.usage.output_tokens


# ---------------------------------------------------------------- checks

class Relatorio:
    def __init__(self, andar):
        self.andar, self.linhas = andar, []

    def add(self, tipo, nome, ok, detalhe=""):
        self.linhas.append((tipo, nome, "OK" if ok is True else ("AVISO" if ok is None else "FALHA"), detalhe))
        return ok

    @property
    def passou(self):
        return not any(t in ("FORMA", "OBRIGATORIO") and s == "FALHA" for t, _, s, _ in self.linhas)

    def texto(self):
        cab = f"### Andar {self.andar}: {'PASSA' if self.passou else 'REPROVA'}\n\n| tipo | check | resultado | detalhe |\n|---|---|---|---|\n"
        return cab + "\n".join(f"| {t} | {n} | {s} | {d} |" for t, n, s, d in self.linhas) + "\n"


def extrair_json(texto, rel):
    bruto = texto.strip()
    try:
        obj = json.loads(bruto)
        rel.add("FORMA", "JSON fecha", True, "objeto puro")
        return obj
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", bruto, re.S)
    if m:
        try:
            obj = json.loads(m.group(1))
            rel.add("FORMA", "JSON fecha", None, "veio dentro de cerca ```; se o Juiz tolera isso nao esta escrito")
            return obj
        except json.JSONDecodeError:
            pass
    rel.add("FORMA", "JSON fecha", False, f"nao parseia: {bruto[:80]!r}...")
    return None


def bate(valor, esperado, unidade_milhoes=True):
    """Compara aceitando reais ou R$ milhoes (unidade nao escrita no kit)."""
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return False, f"nao numerico: {valor!r}"
    if abs(valor - esperado) <= max(1, abs(esperado) * 1e-6):
        return True, f"{valor:,.0f} (reais)"
    if unidade_milhoes and abs(valor * 1e6 - esperado) <= abs(esperado) * 1e-6:
        return None, f"{valor} (R$ milhoes; unidade do Juiz nao escrita)"
    return False, f"declarado {valor:,} / gabarito {esperado:,}"


def conferir(andar, texto, stop_reason, tokens, anteriores):
    rel = Relatorio(andar)
    teto = TETOS[andar]
    rel.add("FORMA", "dentro do teto", stop_reason != "max_tokens",
            (f"{tokens} de {teto} tokens" if tokens >= 0 else "offline: tokens nao medidos") + (f" - SAIDA DO ANDAR {andar} CORTADA NO TETO DE {teto} TOKENS" if stop_reason == "max_tokens" else ""))
    saida = extrair_json(texto, rel)
    if saida is None:
        return rel, None
    if not isinstance(saida, dict):
        rel.add("FORMA", "e objeto", False, type(saida).__name__)
        return rel, None
    chaves = list(saida)  # json.loads preserva a ordem das chaves
    req = SCHEMAS[andar]["required"]
    faltam = [c for c in req if c not in saida]
    rel.add("FORMA", "obrigatorios presentes", not faltam, f"faltam {faltam}" if faltam else f"{len(req)} campos")
    primeiros = chaves[:len(req)]
    rel.add("FORMA", "obrigatorios primeiro", set(primeiros) == set(req) if not faltam else False,
            "ok" if set(primeiros) == set(req) else f"ordem: {chaves} (o kit recomenda; reprovar por isso e regra deste teste local)")
    if "justificativa" in req and "justificativa" in chaves and chaves.index("justificativa") != len(req) - 1:
        rel.add("FORMA", "justificativa por ultimo", None,
                "recomendacao (nao e regra do kit): prosa antes dos numeros gasta o teto")
    for e in jsonschema.Draft202012Validator(SCHEMAS[andar]).iter_errors(saida):
        if list(e.path)[:1] == ["informacoes_ausentes"]:
            continue  # tratado como diferencial abaixo
        if e.validator == "required":
            continue
        rel.add("FORMA", f"tipo {'/'.join(map(str, e.path))}", None, f"{e.message[:90]} (tipos do schema local sao palpite)")
    globals()[f"conferir_andar{andar}"](saida, rel, anteriores)
    return rel, saida


def conferir_andar2(s, rel, _):
    g = GABARITO["andar2"]
    for campo in ("patrimonio_total", "renda_fazenda_anual", "gasto_familia_anual"):
        if campo in s:
            ok, det = bate(s[campo], g[campo]["valor"])
            rel.add("OBRIGATORIO", campo, ok, det)
    if "parcela_imobilizada_pct" in s:
        v = s["parcela_imobilizada_pct"]
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            rel.add("OBRIGATORIO", "parcela_imobilizada_pct", False, f"nao numerico: {v!r}")
        elif abs(v - 75) < 0.01:
            rel.add("OBRIGATORIO", "parcela_imobilizada_pct", True, f"{v}")
        elif abs(v - 0.75) < 1e-4:
            rel.add("OBRIGATORIO", "parcela_imobilizada_pct", None, f"{v} (fracao; gabarito 75, formato nao escrito)")
        else:
            rel.add("OBRIGATORIO", "parcela_imobilizada_pct", False, f"declarado {v} / gabarito 75")
    ia = s.get("informacoes_ausentes")
    if isinstance(ia, list):
        fora = [x for x in ia if x not in VOCAB]
        rel.add("DIFERENCIAL", "vocabulario fechado", not fora, f"fora do vocabulario: {fora}" if fora else f"{ia}")
        iscas = [x for x in ia if x in g["informacoes_ausentes"]["iscas_material_entrega"]]
        rel.add("DIFERENCIAL", "sem iscas", not iscas,
                "; ".join(f"{x} ({g['informacoes_ausentes']['iscas_material_entrega'][x]})" for x in iscas) or "nenhuma")
        perdeu = [x for x in g["informacoes_ausentes"]["ausentes_de_fato"] if x not in ia]
        rel.add("DIFERENCIAL", "lacunas reais apontadas", None if perdeu else True,
                f"nao apontou {perdeu}" if perdeu else "as 3")
    seg = s.get("segmentacao")
    rel.add("DIFERENCIAL", "segmentacao declarada", None if seg is None else True,
            "omitida (README: declarar e melhor que omitir)" if seg is None else f"{seg!r} (gabarito pendente)")


def conferir_andar3(s, rel, anteriores):
    if "produto_liquido_venda" in s:
        ok, det = bate(s["produto_liquido_venda"], GABARITO["andar3"]["produto_liquido_venda"]["valor"])
        rel.add("OBRIGATORIO", "produto_liquido_venda", ok, det + " | 300 - 15% x (300-20)")
    r, rp = s.get("retorno_nominal_premissa_pct"), s.get("renda_perpetua_real_anual")
    if isinstance(r, (int, float)) and isinstance(rp, (int, float)):
        r = r / 100 if r > 1 else r
        sub = r * 0.85 - 0.04
        fisher = (1 + r * 0.85) / 1.04 - 1
        rp_reais = rp * 1e6 if rp < 1e5 else rp
        bases = {"358 mi (100 + 258)": 358e6, "333 mi (358 - 25 filha)": 333e6}
        implicitas = ", ".join(f"{k}: {rp_reais / b * 100:.2f}%" for k, b in bases.items())
        rel.add("OBRIGATORIO", "renda perpetua coerente com a premissa", None,
                f"premissa {r*100:.2f}% -> real liquida {sub*100:.2f}% (subtraindo) ou {fisher*100:.2f}% (dividindo); "
                f"taxa implicita na renda declarada: {implicitas}. Gabarito pendente de decisao.")
    for c in ("offshore_pai_pct", "offshore_filha_pct"):
        if c in s:
            v = s[c]
            rel.add("OBRIGATORIO", f"{c} em 0-100", isinstance(v, (int, float)) and 0 <= v <= 100, f"{v}")
    for c in ("perfil_pai", "perfil_filha"):
        if c in s:
            ok = str(s[c]).strip().lower() in ("conservador", "moderado", "agressivo")
            rel.add("OBRIGATORIO", f"{c} na tabela do enunciado", ok or None, f"{s[c]!r}")
    if 2 in anteriores:
        rel.add("OBRIGATORIO", "coerencia com o Andar 2", None, "conferir a mao: patrimonio e gasto usados na justificativa")


def conferir_andar4(s, rel, _):
    cs = s.get("carteiras")
    if not isinstance(cs, list):
        rel.add("OBRIGATORIO", "carteiras e lista", False, type(cs).__name__)
        return
    vistos = set()
    for c in cs:
        if not isinstance(c, dict):
            rel.add("OBRIGATORIO", "carteira e objeto", False, repr(c)[:60])
            continue
        tit, mer = str(c.get("titular", "?")).lower(), str(c.get("mercado", "?")).lower()
        vistos.add(f"{tit}/{mer}")
        rf, rv = c.get("renda_fixa_pct"), c.get("renda_variavel_pct")
        if isinstance(rf, (int, float)) and isinstance(rv, (int, float)):
            rel.add("OBRIGATORIO", f"{tit}/{mer} soma 100%", abs(rf + rv - 100) < 1e-6, f"RF {rf} + RV {rv}")
            dd = c.get("drawdown_pct")
            if mer in ("onshore", "offshore"):
                calc = backtest.drawdowns(mer, rf, rv)
                if isinstance(dd, (int, float)):
                    perto = [k for k, v in calc.items() if abs(abs(dd) - v) <= 0.5]
                    rel.add("OBRIGATORIO", f"{tit}/{mer} drawdown x serie", True if perto else False,
                            f"declarado {dd} | serie {calc}" + (f" | bate em {perto}" if perto else ""))
                else:
                    rel.add("OBRIGATORIO", f"{tit}/{mer} drawdown declarado", False, f"{dd!r} | serie {calc}")
        else:
            rel.add("OBRIGATORIO", f"{tit}/{mer} classes", False, f"RF {rf!r} RV {rv!r}")
    esperadas = set(GABARITO["andar4"]["carteiras_esperadas"]["valor"])
    rel.add("OBRIGATORIO", "onshore + offshore por titular", esperadas <= vistos, f"vistas {sorted(vistos)}")


def conferir_andar5(s, rel, anteriores):
    a3 = anteriores.get(3)
    if not a3:
        rel.add("OBRIGATORIO", "comparacao com o Andar 3", None, "sem saida do Andar 3 nesta rodada")
        return
    iguais = all(str(s.get(c, "")).lower() == str(a3.get(c, "")).lower() for c in ("perfil_pai", "perfil_filha"))
    if s.get("manteve_posicao") is True:
        rel.add("OBRIGATORIO", "manteve posicao = mesmos perfis", iguais,
                f"A3 {a3.get('perfil_pai')}/{a3.get('perfil_filha')} | A5 {s.get('perfil_pai')}/{s.get('perfil_filha')}")
    else:
        rel.add("OBRIGATORIO", "mudou de posicao com evidencia", None, "conferir a mao se a justificativa cita evidencia nova e explicita")


def conferir_andar6(s, rel, _):
    sl = s.get("slides")
    if not isinstance(sl, list):
        rel.add("OBRIGATORIO", "slides e lista", False, type(sl).__name__)
        return
    tipo = lambda x: str(x.get("tipo", "")).lower() if isinstance(x, dict) else ""
    conteudo = [x for x in sl if tipo(x) == "conteudo"]
    rel.add("OBRIGATORIO", "exatamente 15 de conteudo", len(conteudo) == 15, f"{len(conteudo)} (total {len(sl)})")
    rel.add("OBRIGATORIO", "capa e sumario", any(tipo(x) == "capa" for x in sl) and any(tipo(x) == "sumario" for x in sl),
            str(sorted({tipo(x) for x in sl})))
    texto = json.dumps(sl, ensure_ascii=False).lower()
    sobras = sorted(set(re.findall(r"\{[a-z_]+\}|escreva aqui|lorem ipsum|\[preencher[^\]]*\]", texto)))
    rel.add("OBRIGATORIO", "sem placeholder", not sobras, str(sobras) if sobras else "nenhum")
    sem_acento = texto.translate(str.maketrans("áâãéêíóôõúç", "aaaeeiooouc"))
    secoes = ["quem e a familia", "viver do patrimonio", "perfil de risco", "alocacao", "sucessao"]
    faltam = [x for x in secoes if x not in sem_acento]
    rel.add("OBRIGATORIO", "cinco secoes", not faltam, f"faltam {faltam}" if faltam else "todas")


# ---------------------------------------------------------------- execucao

def registrar_diario(linha):
    texto = DIARIO.read_text(encoding="utf-8")
    marca = "<!-- rodadas-locais -->"
    DIARIO.write_text(texto.replace(marca, f"{linha}\n{marca}"), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agente", default=str(RAIZ / "agente"), help="pasta ou .zip do agente")
    ap.add_argument("--andares", default="2,3,4,5,6")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--dossie", default=str(DOSSIE_PADRAO))
    ap.add_argument("--contestacao", help="arquivo com a contestacao do Andar 5 (sem ele o Andar 5 e pulado)")
    ap.add_argument("--respostas", help="pasta com andarN.json/.txt: confere offline, sem chamar a API")
    ap.add_argument("--nao-registrar", action="store_true")
    a = ap.parse_args()
    andares = [int(x) for x in a.andares.split(",")]

    agente = Agente(a.agente)
    offline = a.respostas is not None
    cliente = None
    if not offline:
        import os
        import anthropic
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or (Path.home() / ".config/anthropic").exists()):
            sys.exit("Sem credencial da API: exporte ANTHROPIC_API_KEY (ou rode `ant auth login`). Nada foi registrado.")
        cliente = anthropic.Anthropic()
    contestacao = Path(a.contestacao).read_text(encoding="utf-8") if a.contestacao else None

    pasta = AQUI / "rodadas" / (dt.datetime.now().strftime("%Y%m%d-%H%M%S") + ("_offline" if offline else ""))
    base, i = pasta, 2
    while pasta.exists():
        pasta, i = base.with_name(f"{base.name}-{i}"), i + 1
    pasta.mkdir(parents=True)
    anteriores, relatorios = {}, []
    for n in andares:
        if n == 5 and not contestacao and not offline:
            rel = Relatorio(5)
            rel.add("FORMA", "andar executado", None, "pulado: sem --contestacao (04_testes/contestacoes.md esta vazio)")
            relatorios.append(rel)
            continue
        system = montar_system(agente, n)
        usuario = montar_usuario(a.dossie, anteriores, n, contestacao)
        if offline:
            arq = next((p for p in (Path(a.respostas) / f"andar{n}.json", Path(a.respostas) / f"andar{n}.txt") if p.exists()), None)
            if not arq:
                continue
            texto, stop, tokens = arq.read_text(encoding="utf-8"), "end_turn", -1
        else:
            texto, stop, tokens = chamar(cliente, a.modelo, system, usuario, TETOS[n])
        (pasta / f"andar{n}_chamada.json").write_text(json.dumps(
            {"modelo": a.modelo, "max_tokens": TETOS[n], "temperature": 0, "system": system,
             "messages": [{"role": "user", "content": usuario}]}, ensure_ascii=False, indent=1), encoding="utf-8")
        (pasta / f"andar{n}_resposta.txt").write_text(texto, encoding="utf-8")
        rel, saida = conferir(n, texto, stop, tokens, anteriores)
        relatorios.append(rel)
        if saida is not None:
            anteriores[n] = saida
        if not rel.passou:
            print(f"Andar {n} reprovou localmente; os seguintes nao rodam (a torre e sequencial).")
            break

    cab = (f"# Rodada local {pasta.name}\n\n- agente: {agente.versao}\n- modelo: {'offline' if offline else a.modelo}"
           f" | temperature 0 | max_tokens = teto do andar\n- dossie: {a.dossie}\n\n")
    (pasta / "relatorio.md").write_text(cab + "\n".join(r.texto() for r in relatorios), encoding="utf-8")
    print(cab + "\n".join(r.texto() for r in relatorios))
    resumo = ", ".join(f"A{r.andar} {'PASSA' if r.passou else 'REPROVA'}" for r in relatorios)
    if not a.nao_registrar:
        registrar_diario(f"| {dt.date.today()} | {agente.versao} | {'offline' if offline else a.modelo} | {resumo} | "
                         f"`simulador/rodadas/{pasta.name}/` |")
    print(f"Relatorio: {pasta / 'relatorio.md'}")
    sys.exit(0 if all(r.passou for r in relatorios) else 1)


if __name__ == "__main__":
    main()
