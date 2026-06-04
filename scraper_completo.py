"""
Scraper completo do Lattes - extrai TODAS as secoes do CV.
- Detecta automaticamente todos os anchors da pagina
- Salva cada secao separada (artigos, patentes, orientacoes, etc.)
- Resume de onde parou
- Voce resolve o CAPTCHA manualmente quando aparecer
"""

import json
import time
import re
from pathlib import Path
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

PESQUISADORES = [
    ("Joao Marcos Travassos Romano",               "6161888127051479"),
    ("Alexandre Gori Maia",                        "8284067987442342"),
    ("Claudia Regina Castellanos Pfeiffer",        "5874189610971770"),
    ("Henrique Nogueira de Sa Earp",               "4040588840128192"),
    ("Jorge Moreira de Souza",                     "2012600504138316"),
    ("Jurandir Zullo Junior",                      "8258858460621065"),
    ("Konradin Metze",                             "7890165105970581"),
    ("Leonardo Tomazeli Duarte",                   "7255819542670612"),
    ("Niro Higuchi",                               "5725047439189958"),
    ("Peter Sussner",                              "8436386349098166"),
    ("Renato Machado",                             "2684900317624442"),
    ("Ricardo Suyama",                             "6146944142372232"),
    ("Romis Ribeiro de Faissol Attux",             "3057001219316165"),
    ("Rosangela Ballini",                          "1766558858445284"),
    ("Sueli Irene Rodrigues Costa",                "8726052383378563"),
    ("Alvaro de Oliveira D'Antona",                "1771971577733548"),
    ("Alberto Paradisi",                           "2505262935763403"),
    ("Aline de Oliveira Neves Panazio",            "9616961770334574"),
    ("Ana Estela Antunes da Silva",                "9070607576528017"),
    ("Ana Paula Romani",                           "7270919095464054"),
    ("Andre Kazuo Takahata",                       "5335439141754127"),
    ("Angel Pontin Garcia",                        "0561187004562980"),
    ("Angela Christina Lucas",                     "6492835060009859"),
    ("Barbara Janet Teruel Mederos",               "1175445863697842"),
    ("Bartolomeu Ferreira Uchoa-Filho",            "7752341440632617"),
    ("Benilton de Sa Carvalho",                    "0897291971174045"),
    ("Betania Silva Carneiro Campello",            "9668497061923439"),
    ("Breno Bernard Nicolau de Franca",            "1827990606590127"),
    ("Bruno Sanches Masiero",                      "4796810967060744"),
    ("Carlos Alberto Oliveira de Freitas",         "5295896684679547"),
    ("Celsa da Silva Moura Souza",                 "6057816333800619"),
    ("Cesar Cabello dos Santos",                   "7928081514043772"),
    ("Claudia Teixeira Alves Affonso",             "4249379649620395"),
    ("Claudio Jose Bordin Junior",                 "7369731268354886"),
    ("Cristiano Torezzan",                         "1314550908170192"),
    ("Daniel Albiero",                             "4121566773721400"),
    ("Denis Gustavo Fantinato",                    "6743074399752192"),
    ("Diego Vicentin",                             "4245451146205160"),
    ("Dimas Irion Alves",                          "2169963993021819"),
    ("Edson Amaro Junior",                         "5927371795409877"),
    ("Eduardo Alves do Valle Junior",              "6301401714714951"),
    ("Erich Vinicius de Paula",                    "0983518713985469"),
    ("Estevao Esmi Laureano",                      "7842866667708331"),
    ("Eulanda Miranda dos Santos",                 "3054990742969890"),
    ("Everton Emanuel Campos de Lima",             "0866511972839867"),
    ("Felix Dieter Antreich",                      "3992941500638443"),
    ("Filipe de Oliveira Costa",                   "9296763269153204"),
    ("Filipe Ieda Fazanaro",                       "2019455573415782"),
    ("Fabio Maia Bertato",                         "5489913728031899"),
    ("Giovanni Moura de Holanda",                  "5163843859981532"),
    ("Gleyce Kelly Dantas Araujo Figueiredo",      "9188905862774352"),
    ("Guilherme Dean Pelegrina",                   "9984556081239908"),
    ("Guilherme Palermo Coelho",                   "0597865875425201"),
    ("Harki Tanaka",                               "0582529929808928"),
    ("Hugo Enrique Hernandez Figueroa",            "4870907540258696"),
    ("Igor Gadelha Pereira",                       "7917967295254962"),
    ("Ivette Raymunda Luna Huamani",               "2854855744345507"),
    ("Joao Batista Florindo",                      "4462635233301972"),
    ("Joao Marcos Bastos Cavalcanti",              "3537707069694606"),
    ("Jose Guilherme Cecatti",                     "9719769943147183"),
    ("Jose Luiz de Souza Pio",                     "1014904168887285"),
    ("Joao Eloir Strapasson",                      "7566633201771792"),
    ("Joao Frederico da Costa Azevedo Meyer",      "9611168473482242"),
    ("Joao Paulo Dias de Souza",                   "9159348039113345"),
    ("Juan Gabriel Colonna",                       "9535853909210803"),
    ("Julio Cesar Teixeira",                       "2416276722663460"),
    ("Kelson Mota Teixeira de Oliveira",           "8167226394049801"),
    ("Kenji Nose Filho",                           "7933130617235231"),
    ("Leandro Russovski Tessler",                  "8439710263887822"),
    ("Leonardo Abdala Elias",                      "5429275286295501"),
    ("Leonardo Henrique de Melo Leite",            "0627453518078015"),
    ("Leticia Rittner",                            "6540619386101635"),
    ("Levy Boccato",                               "8193307869847230"),
    ("Lucas Carvalho Cordeiro",                    "5005832876603012"),
    ("Luiz Henrique Antunes Rodrigues",            "8555352444875883"),
    ("Luis Otavio Zanatta Sarian",                 "5231556293542572"),
    ("Manish Sharma",                              "8584508324043770"),
    ("Marcelo da Silva Pinho",                     "0513060705572423"),
    ("Marcelo Gomes da Silva Bruno",               "5244203898950618"),
    ("Marcelo Pereira da Cunha",                   "3684400139138167"),
    ("Marcos Augusto Bastos Dias",                 "8031974589549952"),
    ("Marcos Medeiros Raimundo",                   "1605909137233786"),
    ("Marcos Nakamura Pereira",                    "9449960742334833"),
    ("Marcos Ricardo Omena de Albuquerque Maximo", "1610878342077626"),
    ("Marcos Vanine Portilho de Nader",            "7888547143130373"),
    ("Marcus Henrique Victor Junior",              "4656075728153452"),
    ("Maria Gorete Valus",                         "6672577061255784"),
    ("Maria Leticia Cintra",                       "5803743950533597"),
    ("Marta Rettelbusch de Bastos",                "7105264376958447"),
    ("Murilo Bellezoni Loiola",                    "3775617409810154"),
    ("Monica Mitiko Soares Matsumoto",             "3017844454590417"),
    ("Paula Dornhofer Paro Costa",                 "4518009815956207"),
    ("Priscila Cristina Berbert Rampazzo",         "7297488900077729"),
    ("Priscila Pereira Coltri",                    "7282763701085219"),
    ("Priscyla Waleska Targino de Azevedo Simoes", "6676936483436465"),
    ("Rafael Ferrari",                             "9053038415971900"),
    ("Raimundo da Silva Barreto",                  "1132672107627968"),
    ("Renata Pelissari Infante",                   "4642836982364582"),
    ("Renata Ribeiro do Valle Goncalves",          "2345317755369905"),
    ("Renato Passini Junior",                      "0079874765476253"),
    ("Rodolfo de Carvalho Pacagnella",             "5647674022681204"),
    ("Rodrigo Lanna Franco da Silveira",           "7916021882928474"),
    ("Rosa Maria Soares Madeira Domingues",        "4458330446178508"),
    ("Rosiane de Freitas Rodrigues",               "8358219976594707"),
    ("Sandra Eliza Fontes de Avila",               "8343699060914150"),
    ("Sergio San Juan Dertkigil",                  "1672860991156449"),
    ("Simone Pallone de Figueiredo",               "0233896493818934"),
    ("Sophie Francoise Mauricette Derchain",       "2585985788279780"),
    ("Thais Queiroz Zorzeto Cesar",                "7517079067482818"),
    ("Tiago Fernandes Tavares",                    "0738838630843591"),
    ("Vandermi Joao da Silva",                     "1231884642541177"),
    ("Victor Mendonca de Azevedo",                 "3378276571162549"),
    ("Washington Alves de Oliveira",               "8789150442726795"),
    ("Weiler Alves Finamore",                      "8689372749422458"),
]

OUTPUT_FILE  = Path("scraped_completo.json")
HTML_DIR     = Path("html_cvs")          # HTMLs completos salvos aqui
DELAY        = 12                         # segundos entre paginas

# Mapa de anchor -> nome legivel da secao
SECOES_CONHECIDAS = {
    "ProducaoBibliografica":         "producao_bibliografica",
    "ArtigosCompletos":              "artigos_periodicos",
    "LivrosCapitulos":               "livros_capitulos",
    "TrabalhosCongresso":            "trabalhos_congresso",
    "ApresentacoesTrabalho":         "apresentacoes",
    "ProducaoTecnica":               "producao_tecnica",
    "PatentesRegistros":             "patentes_registros",
    "ProgramaComputador":            "software_registros",
    "ProducaoArtistica":             "producao_artistica",
    "Orientacoes":                   "orientacoes",
    "OrientacoesConcluidas":         "orientacoes_concluidas",
    "OrientacoesEmAndamento":        "orientacoes_andamento",
    "PremiosTitulos":                "premios_titulos",
    "Eventos":                       "eventos",
    "Bancas":                        "bancas",
    "OutrasInformacoes":             "outras_informacoes",
    "InformacoesCandidato":          "informacoes_candidato",
}


def salvar_html(id_lattes, html):
    """Salva o HTML bruto do CV para reprocessamento futuro."""
    HTML_DIR.mkdir(exist_ok=True)
    path = HTML_DIR / f"{id_lattes}.html"
    path.write_text(html, encoding="utf-8")


def extrair_metadados(soup):
    """Extrai dados gerais: nome completo, ultima atualizacao, areas de atuacao, formacao."""
    meta = {}

    # Nome completo
    for sel in ["h2.nome", "h1", "div#nome", "span.nome"]:
        el = soup.select_one(sel)
        if el:
            txt = el.get_text(strip=True)
            if txt and len(txt) > 3:
                meta["nome_completo"] = txt
                break

    # Ultima atualizacao
    for el in soup.find_all(string=re.compile(r"[Uu]ltima.*[Aa]tualiz")):
        parent = el.parent
        if parent:
            txt = parent.get_text(strip=True)
            meta["ultima_atualizacao"] = txt
            break

    # Areas de atuacao
    areas = []
    anchor_areas = soup.find("a", attrs={"name": re.compile(r"[Aa]reas|[Aa]rea")})
    if anchor_areas:
        parent = anchor_areas.find_parent("div")
        if parent:
            for div in parent.find_all("div", class_=re.compile(r"layout-cell")):
                txt = div.get_text(separator=" ", strip=True)
                txt = re.sub(r"\s+", " ", txt).strip()
                if txt and len(txt) > 5 and txt not in areas:
                    areas.append(txt)
    if areas:
        meta["areas_atuacao"] = areas

    # Resumo / texto da bio
    resumo_el = soup.find("div", id="resumo")
    if resumo_el:
        meta["resumo"] = re.sub(r"\s+", " ", resumo_el.get_text(strip=True))

    return meta


def carregar_progresso():
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            dados = json.load(f)
        return {p["id"]: p for p in dados}
    return {}


def salvar_progresso(dados_dict):
    lista = list(dados_dict.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


def extrair_todas_secoes(soup):
    """
    Extrai todas as secoes do CV automaticamente.
    Retorna dict: {nome_secao: [lista de itens texto]}
    """
    resultado = {}

    # Encontra todos os anchors com atributo 'name'
    anchors = soup.find_all("a", attrs={"name": True})

    for anchor in anchors:
        nome = anchor.get("name", "").strip()
        if not nome:
            continue

        # Pega o nome legivel ou usa o proprio anchor name
        nome_campo = SECOES_CONHECIDAS.get(nome, nome.lower())

        # Sobe ate o div pai que contem os itens
        parent = anchor.find_parent("div")
        if not parent:
            continue

        items = []
        for div in parent.find_all("div", class_="layout-cell-11"):
            txt = div.get_text(separator=" ", strip=True)
            txt = re.sub(r"\s+", " ", txt).strip()
            if txt and len(txt) > 10:
                items.append(txt)

        if items:
            # Se ja existe o campo, concatena (pode ter subsecoes)
            if nome_campo in resultado:
                resultado[nome_campo].extend(items)
            else:
                resultado[nome_campo] = items

    return resultado


def cv_carregado(driver):
    try:
        html = driver.page_source
        url = driver.current_url
        tem_cv = "metodo=apresentar" in url or "metodo=apresentar" in html
        sem_captcha = "divCaptcha" not in html and "grecaptcha.render" not in html
        return tem_cv and sem_captcha
    except Exception:
        return False


def aguardar_cv(driver, timeout=300):
    for i in range(timeout):
        time.sleep(1)
        if cv_carregado(driver):
            return True
        if i > 0 and i % 20 == 0:
            print(f"    aguardando... ({i}s) - resolva o CAPTCHA se aparecer")
    return False


def scrape_cv(driver, nome, id_lattes):
    driver.get(f"https://lattes.cnpq.br/{id_lattes}")
    time.sleep(3)

    if not cv_carregado(driver):
        print("  CAPTCHA detectado - aguardando...")
        ok = aguardar_cv(driver)
        if not ok:
            return {"id": id_lattes, "nome": nome, "secoes": {}, "erro": "timeout"}

    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Salva HTML completo para reprocessamento futuro
    salvar_html(id_lattes, html)

    secoes  = extrair_todas_secoes(soup)
    metadados = extrair_metadados(soup)
    total   = sum(len(v) for v in secoes.values())

    return {
        "id":          id_lattes,
        "nome":        nome,
        "metadados":   metadados,
        "secoes":      secoes,
        "total_itens": total,
    }


def main():
    progresso = carregar_progresso()
    ja_feitos = set(progresso.keys())

    # Filtra pesquisadores com erro para re-tentar
    com_erro = {id_ for id_, p in progresso.items() if p.get("erro")}
    if com_erro:
        print(f"Re-tentando {len(com_erro)} com erro anterior...")
        ja_feitos -= com_erro

    pendentes = [(n, i) for n, i in PESQUISADORES if i not in ja_feitos]

    print(f"Total: {len(PESQUISADORES)} | Feitos: {len(ja_feitos)} | Pendentes: {len(pendentes)}")
    if not pendentes:
        print("Todos ja foram coletados!")
        # Mostra resumo das secoes encontradas
        resumo = {}
        for p in progresso.values():
            for sec, items in p.get("secoes", {}).items():
                resumo[sec] = resumo.get(sec, 0) + len(items)
        print("\nSecoes encontradas:")
        for sec, total in sorted(resumo.items(), key=lambda x: -x[1]):
            print(f"  {sec}: {total} itens")
        return

    print("\nAbrindo Chrome...")
    print("Resolva o CAPTCHA quando aparecer - o script continua sozinho.\n")

    driver = uc.Chrome(version_main=148)

    try:
        for idx, (nome, id_lattes) in enumerate(pendentes, 1):
            print(f"[{idx}/{len(pendentes)}] {nome}")
            try:
                dados = scrape_cv(driver, nome, id_lattes)
                progresso[id_lattes] = dados
                salvar_progresso(progresso)
                secoes = dados.get("secoes", {})
                resumo = ", ".join(f"{k}:{len(v)}" for k, v in secoes.items() if v)
                print(f"  OK: {dados.get('total_itens', 0)} itens | {resumo[:120]}")
                time.sleep(DELAY)
            except Exception as e:
                print(f"  ERRO: {e}")
                progresso[id_lattes] = {"id": id_lattes, "nome": nome, "secoes": {}, "erro": str(e)}
                salvar_progresso(progresso)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    total_pesq = len([p for p in progresso.values() if not p.get("erro")])
    print(f"\nFinalizado! {total_pesq} pesquisadores OK.")
    print(f"Dados em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
