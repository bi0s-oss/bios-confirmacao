"""
Reprocessa os HTMLs salvos em html_cvs/ sem precisar acessar o Lattes.
Use este script se quiser extrair novos campos depois, sem refazer os CAPTCHAs.

Uso:
    python reprocessar_htmls.py
"""

import json, re
from pathlib import Path
from bs4 import BeautifulSoup

HTML_DIR    = Path("html_cvs")
OUTPUT_FILE = Path("scraped_completo.json")

PESQUISADORES = {
    "6161888127051479": "Joao Marcos Travassos Romano",
    "8284067987442342": "Alexandre Gori Maia",
    "5874189610971770": "Claudia Regina Castellanos Pfeiffer",
    "4040588840128192": "Henrique Nogueira de Sa Earp",
    "2012600504138316": "Jorge Moreira de Souza",
    "8258858460621065": "Jurandir Zullo Junior",
    "7890165105970581": "Konradin Metze",
    "7255819542670612": "Leonardo Tomazeli Duarte",
    "5725047439189958": "Niro Higuchi",
    "8436386349098166": "Peter Sussner",
    "2684900317624442": "Renato Machado",
    "6146944142372232": "Ricardo Suyama",
    "3057001219316165": "Romis Ribeiro de Faissol Attux",
    "1766558858445284": "Rosangela Ballini",
    "8726052383378563": "Sueli Irene Rodrigues Costa",
    "1771971577733548": "Alvaro de Oliveira D'Antona",
    "2505262935763403": "Alberto Paradisi",
    "9616961770334574": "Aline de Oliveira Neves Panazio",
    "9070607576528017": "Ana Estela Antunes da Silva",
    "7270919095464054": "Ana Paula Romani",
    "5335439141754127": "Andre Kazuo Takahata",
    "0561187004562980": "Angel Pontin Garcia",
    "6492835060009859": "Angela Christina Lucas",
    "1175445863697842": "Barbara Janet Teruel Mederos",
    "7752341440632617": "Bartolomeu Ferreira Uchoa-Filho",
    "0897291971174045": "Benilton de Sa Carvalho",
    "9668497061923439": "Betania Silva Carneiro Campello",
    "1827990606590127": "Breno Bernard Nicolau de Franca",
    "4796810967060744": "Bruno Sanches Masiero",
    "5295896684679547": "Carlos Alberto Oliveira de Freitas",
    "6057816333800619": "Celsa da Silva Moura Souza",
    "7928081514043772": "Cesar Cabello dos Santos",
    "4249379649620395": "Claudia Teixeira Alves Affonso",
    "7369731268354886": "Claudio Jose Bordin Junior",
    "1314550908170192": "Cristiano Torezzan",
    "4121566773721400": "Daniel Albiero",
    "6743074399752192": "Denis Gustavo Fantinato",
    "4245451146205160": "Diego Vicentin",
    "2169963993021819": "Dimas Irion Alves",
    "5927371795409877": "Edson Amaro Junior",
    "6301401714714951": "Eduardo Alves do Valle Junior",
    "0983518713985469": "Erich Vinicius de Paula",
    "7842866667708331": "Estevao Esmi Laureano",
    "3054990742969890": "Eulanda Miranda dos Santos",
    "0866511972839867": "Everton Emanuel Campos de Lima",
    "3992941500638443": "Felix Dieter Antreich",
    "9296763269153204": "Filipe de Oliveira Costa",
    "2019455573415782": "Filipe Ieda Fazanaro",
    "5489913728031899": "Fabio Maia Bertato",
    "5163843859981532": "Giovanni Moura de Holanda",
    "9188905862774352": "Gleyce Kelly Dantas Araujo Figueiredo",
    "9984556081239908": "Guilherme Dean Pelegrina",
    "0597865875425201": "Guilherme Palermo Coelho",
    "0582529929808928": "Harki Tanaka",
    "4870907540258696": "Hugo Enrique Hernandez Figueroa",
    "7917967295254962": "Igor Gadelha Pereira",
    "2854855744345507": "Ivette Raymunda Luna Huamani",
    "4462635233301972": "Joao Batista Florindo",
    "3537707069694606": "Joao Marcos Bastos Cavalcanti",
    "9719769943147183": "Jose Guilherme Cecatti",
    "1014904168887285": "Jose Luiz de Souza Pio",
    "7566633201771792": "Joao Eloir Strapasson",
    "9611168473482242": "Joao Frederico da Costa Azevedo Meyer",
    "9159348039113345": "Joao Paulo Dias de Souza",
    "9535853909210803": "Juan Gabriel Colonna",
    "2416276722663460": "Julio Cesar Teixeira",
    "8167226394049801": "Kelson Mota Teixeira de Oliveira",
    "7933130617235231": "Kenji Nose Filho",
    "8439710263887822": "Leandro Russovski Tessler",
    "5429275286295501": "Leonardo Abdala Elias",
    "0627453518078015": "Leonardo Henrique de Melo Leite",
    "6540619386101635": "Leticia Rittner",
    "8193307869847230": "Levy Boccato",
    "5005832876603012": "Lucas Carvalho Cordeiro",
    "8555352444875883": "Luiz Henrique Antunes Rodrigues",
    "5231556293542572": "Luis Otavio Zanatta Sarian",
    "8584508324043770": "Manish Sharma",
    "0513060705572423": "Marcelo da Silva Pinho",
    "5244203898950618": "Marcelo Gomes da Silva Bruno",
    "3684400139138167": "Marcelo Pereira da Cunha",
    "8031974589549952": "Marcos Augusto Bastos Dias",
    "1605909137233786": "Marcos Medeiros Raimundo",
    "9449960742334833": "Marcos Nakamura Pereira",
    "1610878342077626": "Marcos Ricardo Omena de Albuquerque Maximo",
    "7888547143130373": "Marcos Vanine Portilho de Nader",
    "4656075728153452": "Marcus Henrique Victor Junior",
    "6672577061255784": "Maria Gorete Valus",
    "5803743950533597": "Maria Leticia Cintra",
    "7105264376958447": "Marta Rettelbusch de Bastos",
    "3775617409810154": "Murilo Bellezoni Loiola",
    "3017844454590417": "Monica Mitiko Soares Matsumoto",
    "4518009815956207": "Paula Dornhofer Paro Costa",
    "7297488900077729": "Priscila Cristina Berbert Rampazzo",
    "7282763701085219": "Priscila Pereira Coltri",
    "6676936483436465": "Priscyla Waleska Targino de Azevedo Simoes",
    "9053038415971900": "Rafael Ferrari",
    "1132672107627968": "Raimundo da Silva Barreto",
    "4642836982364582": "Renata Pelissari Infante",
    "2345317755369905": "Renata Ribeiro do Valle Goncalves",
    "0079874765476253": "Renato Passini Junior",
    "5647674022681204": "Rodolfo de Carvalho Pacagnella",
    "7916021882928474": "Rodrigo Lanna Franco da Silveira",
    "4458330446178508": "Rosa Maria Soares Madeira Domingues",
    "8358219976594707": "Rosiane de Freitas Rodrigues",
    "8343699060914150": "Sandra Eliza Fontes de Avila",
    "1672860991156449": "Sergio San Juan Dertkigil",
    "0233896493818934": "Simone Pallone de Figueiredo",
    "2585985788279780": "Sophie Francoise Mauricette Derchain",
    "7517079067482818": "Thais Queiroz Zorzeto Cesar",
    "0738838630843591": "Tiago Fernandes Tavares",
    "1231884642541177": "Vandermi Joao da Silva",
    "3378276571162549": "Victor Mendonca de Azevedo",
    "8789150442726795": "Washington Alves de Oliveira",
    "8689372749422458": "Weiler Alves Finamore",
}

# Importa as funcoes do scraper
import sys
sys.path.insert(0, str(Path(__file__).parent))
from scraper_completo import extrair_todas_secoes, extrair_metadados, SECOES_CONHECIDAS


def reprocessar():
    htmls = sorted(HTML_DIR.glob("*.html"))
    if not htmls:
        print(f"Nenhum HTML encontrado em {HTML_DIR}/")
        print("Rode primeiro: python scraper_completo.py")
        return

    print(f"Encontrados {len(htmls)} HTMLs para reprocessar...")

    resultado = {}
    for html_path in htmls:
        id_lattes = html_path.stem
        nome = PESQUISADORES.get(id_lattes, f"ID_{id_lattes}")
        print(f"  Reprocessando: {nome}")

        html = html_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        secoes   = extrair_todas_secoes(soup)
        metadados = extrair_metadados(soup)
        total    = sum(len(v) for v in secoes.values())

        resultado[id_lattes] = {
            "id":          id_lattes,
            "nome":        nome,
            "metadados":   metadados,
            "secoes":      secoes,
            "total_itens": total,
        }

    lista = list(resultado.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

    print(f"\nReprocessados: {len(lista)} pesquisadores")
    print(f"Salvo em: {OUTPUT_FILE}")

    # Resumo das secoes encontradas
    resumo = {}
    for p in lista:
        for sec in p.get("secoes", {}):
            resumo[sec] = resumo.get(sec, 0) + 1
    print("\nSecoes encontradas (pesquisadores com dados):")
    for sec, count in sorted(resumo.items(), key=lambda x: -x[1]):
        print(f"  {sec}: {count} pesquisadores")


if __name__ == "__main__":
    reprocessar()
