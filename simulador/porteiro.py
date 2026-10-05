"""Andar 1 local: confere um .zip de submissao contra as regras escritas no README do kit.

So cobre o que o kit descreve. Os checks sem especificacao escrita (pasta_tools,
sem_executaveis, nomes_no_padrao, estrutura_md) aparecem como AVISO, nao como OK.

Uso: .venv/bin/python porteiro.py ../05_submissoes/zips/agente_v1.zip
"""
import json
import sys
import zipfile
from pathlib import Path

import jsonschema

AQUI = Path(__file__).parent
MARCADOR = "ESCREVA AQUI"


def conferir(caminho_zip):
    falhas, avisos, oks = [], [], []
    z = zipfile.ZipFile(caminho_zip)
    nomes = [n for n in z.namelist() if not n.endswith("/")]

    def ok(check, cond, detalhe):
        (oks if cond else falhas).append(f"{check}: {detalhe}")
        return cond

    if not ok("manifesto_raiz", "contrato.json" in nomes,
              "contrato.json na raiz do zip, em minusculas"):
        return falhas, avisos, oks
    bruto = z.read("contrato.json")
    ok("manifesto_raiz", not bruto.startswith(b"\xef\xbb\xbf"), "UTF-8 sem BOM")
    try:
        contrato = json.loads(bruto.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        ok("manifesto_raiz", False, f"JSON invalido: {e}")
        return falhas, avisos, oks
    ok("manifesto_raiz", True, "JSON valido")

    schema = json.loads((AQUI / "schemas/contrato.schema.json").read_text())
    erros = sorted(jsonschema.Draft202012Validator(schema).iter_errors(contrato), key=str)
    ok("schema do contrato (transcrito do README)", not erros,
       "; ".join(f"{list(e.path)}: {e.message[:120]}" for e in erros) or "sem erros")

    for andar, decl in sorted(contrato.get("andares", {}).items()):
        prompt = decl.get("prompt", "") if isinstance(decl, dict) else ""
        if ok("chamada_dos_andares", prompt in nomes, f"andar {andar} -> {prompt} existe no zip"):
            texto = z.read(prompt).decode("utf-8")
            ok("prompts_preenchidos", MARCADOR not in texto, f"andar {andar} sem '{MARCADOR}'")

    manifestos = [n for n in nomes if n in ("Claude.md", "AGENTS.md")]
    if ok("Claude.md/AGENTS.md na raiz", bool(manifestos), ", ".join(manifestos) or "ausente"):
        texto = z.read(manifestos[0]).decode("utf-8")
        faltam = [p["prompt"] for p in contrato["andares"].values() if p["prompt"] not in texto]
        ok("manifesto cita os cinco andares", not faltam, f"faltam {faltam}" if faltam else "todos citados")
        if MARCADOR in texto:
            avisos.append(f"{manifestos[0]} contem '{MARCADOR}'")

    lixo = [n for n in nomes if ".DS_Store" in n or "__MACOSX" in n or "__pycache__" in n]
    if lixo:
        avisos.append(f"arquivos de sistema no zip: {lixo}")
    tools = [n for n in nomes if n.startswith("tools/")]
    avisos.append(f"pasta_tools (regra nao escrita): {len(tools)} arquivo(s) em tools/ {tools}")
    exe = [n for n in nomes if not n.endswith((".md", ".json", ".py", ".txt", ".pptx", ".xlsx"))]
    py = [n for n in nomes if n.endswith(".py")]
    avisos.append(f"sem_executaveis (regra nao escrita): extensoes fora de md/json/py/txt: {exe or 'nenhuma'}; "
                  f".py presentes {py} (o kit inclui .py em exemplo-agente/tools/)")
    estranhos = [n for n in nomes if not n.isascii() or " " in n or n != n.strip()]
    avisos.append(f"nomes_no_padrao (regra nao escrita): nomes com espaco/acento: {estranhos or 'nenhum'}")
    avisos.append("estrutura_md (regra nao escrita): nao simulado alem da presenca do Claude.md")
    return falhas, avisos, oks


if __name__ == "__main__":
    falhas, avisos, oks = conferir(sys.argv[1])
    for linha in oks:
        print("OK     ", linha)
    for linha in avisos:
        print("AVISO  ", linha)
    for linha in falhas:
        print("FALHA  ", linha)
    print("\nRESULTADO:", "REPROVA" if falhas else "PASSA nas regras escritas")
    sys.exit(1 if falhas else 0)
