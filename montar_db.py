"""
Converte scraped_completo.json + curriculos (1).json -> db.json
Mapeia cada secao do Lattes para o campo correto do site.
"""

import json
from pathlib import Path


MAPA_SECOES = {
    "artigos_periodicos":       "artigosCompletos",
    "producao_bibliografica":   "artigosCompletos",   # fallback
    "livros_capitulos":         "livrosCapitulos",
    "trabalhos_congresso":      "trabalhosCongresso",
    "apresentacoes":            "apresentacoes",
    "patentes_registros":       "patentesRegistros",
    "software_registros":       "softwareRegistros",
    "producao_tecnica":         "producaoTecnica",
    "orientacoes_concluidas":   "orientacoesConcluidas",
    "orientacoes":              "orientacoesConcluidas",  # fallback
    "orientacoes_andamento":    "orientacoesAndamento",
    "premios_titulos":          "premiosTitulos",
    "eventos":                  "eventos",
    "bancas":                   "bancas",
    "outras_informacoes":       "outrasInformacoes",
}


def limpar(txt):
    import re
    if not isinstance(txt, str):
        return ""
    return re.sub(r"\s+", " ", txt).replace("\t", " ").replace("\n", " ").strip()


def dedup(lista):
    seen, out = set(), []
    for item in lista:
        k = item.strip().lower()[:120]
        if k and k not in seen:
            seen.add(k)
            out.append(item)
    return out


def main():
    # Base: curriculos com projetos
    with open("curriculos (1).json", encoding="utf-8") as f:
        curriculos = json.load(f)

    base = {}
    for p in curriculos:
        base[p["id"]] = {
            "id":               p["id"],
            "nome":             p["nome"],
            "ultima_atualizacao": p.get("ultima_atualizacao", ""),
            "projetos":         p.get("projetos", []),
            # campos de producao (todos vazios por padrao)
            "artigosCompletos":       [],
            "livrosCapitulos":        [],
            "trabalhosCongresso":     [],
            "apresentacoes":          [],
            "patentesRegistros":      [],
            "softwareRegistros":      [],
            "producaoTecnica":        [],
            "orientacoesConcluidas":  [],
            "orientacoesAndamento":   [],
            "premiosTitulos":         [],
            "eventos":                [],
            "bancas":                 [],
            "outrasInformacoes":      [],
        }

    # Overlay com dados do scraper completo
    if Path("scraped_completo.json").exists():
        with open("scraped_completo.json", encoding="utf-8") as f:
            scraped = json.load(f)

        for p in scraped:
            id_ = p.get("id")
            if not id_ or id_ not in base or p.get("erro"):
                continue
            secoes = p.get("secoes", {})
            for secao_key, campo_db in MAPA_SECOES.items():
                items = secoes.get(secao_key, [])
                if items:
                    items_limpos = [limpar(i) for i in items if limpar(i)]
                    base[id_][campo_db] = dedup(base[id_][campo_db] + items_limpos)

    resultado = list(base.values())

    # Estatisticas
    campos = ["artigosCompletos","livrosCapitulos","trabalhosCongresso","patentesRegistros",
              "softwareRegistros","orientacoesConcluidas","premiosTitulos","eventos"]
    print(f"Pesquisadores: {len(resultado)}")
    for c in campos:
        total = sum(len(p.get(c, [])) for p in resultado)
        com_dados = sum(1 for p in resultado if p.get(c))
        if total > 0:
            print(f"  {c}: {total} itens em {com_dados} pesquisadores")

    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, separators=(",", ":"))
    print(f"\ndb.json salvo ({Path('db.json').stat().st_size/1024/1024:.1f} MB)")


if __name__ == "__main__":
    main()
