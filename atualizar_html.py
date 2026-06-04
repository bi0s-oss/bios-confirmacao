"""
Le dados_completos.json, remove duplicados e atualiza o index.html com:
- const DB atualizado com todos os tipos de producao
- Novas secoes de producao no site (acordeoes collapsibles)
- Commit e push para o GitHub
"""

import json
import re
import subprocess
import shutil
import sys
from pathlib import Path

JSON_PATH   = Path("dados_completos.json")
HTML_PATH   = Path("index.html")
GIT_EXE     = r"C:\Program Files\Git\bin\git.exe"


# ── Limpeza de dados ────────────────────────────────────────────

def dedup(lista):
    seen, out = set(), []
    for item in lista:
        if isinstance(item, dict):
            key = str(item).lower()[:120]
            if key not in seen:
                seen.add(key)
                out.append(item)
        else:
            key = str(item).strip().lower()[:120]
            if key and key not in seen:
                seen.add(key)
                out.append(str(item).strip())
    return out


def limpar_dados(dados):
    removidos = 0
    for p in dados:
        for campo in ("projetos", "artigosCompletos", "livrosPublicados",
                      "orientacoesconcluidas", "participacaoEventos",
                      "premiosTitulos", "demaisProducaoTecnica",
                      "textosJornaisRevistas", "entrevistasEPCTA"):
            antes = len(p.get(campo, []))
            if isinstance(p.get(campo), list):
                p[campo] = dedup(p[campo])
            removidos += antes - len(p.get(campo, []))
    return dados, removidos


# ── CSS das novas secoes ────────────────────────────────────────

NOVO_CSS = """
  /* Secoes de producao */
  .producao-section { margin-top: 28px; }
  .producao-header {
    display: flex; align-items: center; justify-content: space-between;
    cursor: pointer; padding: 14px 18px;
    background: var(--surface); border: 1.5px solid var(--border);
    border-radius: var(--radius); user-select: none;
    transition: border-color 0.15s;
  }
  .producao-header:hover { border-color: #aac9bb; }
  .producao-header.open { border-color: var(--accent); border-bottom-left-radius: 0; border-bottom-right-radius: 0; }
  .producao-header-left { display: flex; align-items: center; gap: 10px; }
  .producao-icon { font-size: 18px; }
  .producao-titulo { font-size: 14px; font-weight: 600; color: var(--text); }
  .producao-count {
    font-size: 12px; font-weight: 600; color: var(--tag);
    background: #d4ede0; padding: 2px 8px; border-radius: 20px;
  }
  .producao-chevron { color: var(--sub); transition: transform 0.2s; font-size: 12px; }
  .producao-header.open .producao-chevron { transform: rotate(180deg); }
  .producao-body {
    display: none; border: 1.5px solid var(--accent);
    border-top: none; border-bottom-left-radius: var(--radius);
    border-bottom-right-radius: var(--radius);
    background: var(--surface); max-height: 400px; overflow-y: auto;
  }
  .producao-body.open { display: block; }
  .producao-item {
    padding: 10px 18px; font-size: 13px; color: var(--text);
    border-bottom: 1px solid var(--border); line-height: 1.5;
  }
  .producao-item:last-child { border-bottom: none; }
  .producao-item-num { color: var(--sub); font-size: 11px; margin-right: 6px; }
  .producao-empty { padding: 16px 18px; font-size: 13px; color: var(--sub); font-style: italic; }
"""

# ── HTML das secoes de producao ─────────────────────────────────

SECOES_CONFIG = [
    ("artigosCompletos",      "📄", "Artigos completos em periódicos"),
    ("livrosPublicados",      "📚", "Livros publicados/organizados"),
    ("orientacoesconcluidas", "🎓", "Orientações concluídas"),
    ("participacaoEventos",   "🏛️", "Participação em eventos"),
    ("premiosTitulos",        "🏆", "Prêmios e títulos"),
    ("demaisProducaoTecnica", "🔧", "Demais produções técnicas"),
    ("textosJornaisRevistas", "📰", "Textos em jornais/revistas"),
    ("entrevistasEPCTA",      "🎙️", "Entrevistas e mídia"),
]

PRODUCAO_HTML = """
    <div class="producao-section" id="producaoSection" style="display:none">
      <h3 style="font-family:'DM Serif Display',serif;font-size:18px;margin:32px 0 12px;color:var(--accent)">Produção Científica</h3>
      <div id="producaoLista"></div>
    </div>
"""

# ── JS para renderizar secoes ───────────────────────────────────

PRODUCAO_JS = """
function renderProducao(person) {
  const secoes = [
    {campo:'artigosCompletos',      icone:'📄', titulo:'Artigos completos em periódicos'},
    {campo:'livrosPublicados',      icone:'📚', titulo:'Livros publicados/organizados'},
    {campo:'orientacoesconcluidas', icone:'🎓', titulo:'Orientações concluídas'},
    {campo:'participacaoEventos',   icone:'🏛️', titulo:'Participação em eventos'},
    {campo:'premiosTitulos',        icone:'🏆', titulo:'Prêmios e títulos'},
    {campo:'demaisProducaoTecnica', icone:'🔧', titulo:'Demais produções técnicas'},
    {campo:'textosJornaisRevistas', icone:'📰', titulo:'Textos em jornais/revistas'},
    {campo:'entrevistasEPCTA',      icone:'🎙️', titulo:'Entrevistas e mídia'},
  ];

  const lista = document.getElementById('producaoLista');
  lista.innerHTML = '';
  let temAlgo = false;

  secoes.forEach(({campo, icone, titulo}) => {
    const items = person[campo] || [];
    if (items.length === 0) return;
    temAlgo = true;
    const id = 'sec_' + campo;
    const div = document.createElement('div');
    div.innerHTML = `
      <div class="producao-header" onclick="toggleSecao('${id}')">
        <div class="producao-header-left">
          <span class="producao-icon">${icone}</span>
          <span class="producao-titulo">${titulo}</span>
          <span class="producao-count">${items.length}</span>
        </div>
        <span class="producao-chevron">▼</span>
      </div>
      <div class="producao-body" id="${id}">
        ${items.map((item,i) => `<div class="producao-item"><span class="producao-item-num">${i+1}.</span>${item}</div>`).join('')}
      </div>`;
    lista.appendChild(div);
  });

  document.getElementById('producaoSection').style.display = temAlgo ? 'block' : 'none';
}

function toggleSecao(id) {
  const body = document.getElementById(id);
  const header = body.previousElementSibling;
  const isOpen = body.classList.contains('open');
  body.classList.toggle('open', !isOpen);
  header.classList.toggle('open', !isOpen);
}
"""


# ── Atualiza HTML ───────────────────────────────────────────────

def atualizar_html(html_path, novo_db_js):
    content = html_path.read_text(encoding="utf-8")

    # 1. Substitui const DB (linha inteira que começa com "const DB = [")
    lines = content.split("\n")
    found = False
    for i, line in enumerate(lines):
        if line.startswith("const DB = ["):
            lines[i] = novo_db_js
            found = True
            break
    if not found:
        print("ERRO: const DB nao encontrado")
        sys.exit(1)
    content = "\n".join(lines)

    # 2. Adiciona CSS (antes de </style>)
    if NOVO_CSS.strip() not in content:
        content = content.replace("</style>", NOVO_CSS + "\n</style>", 1)

    # 3. Adiciona secao de producao no HTML (antes de </div>\n\n<div class="sticky-bottom")
    if 'id="producaoSection"' not in content:
        content = content.replace(
            '</div>\n</div>\n\n<div class="sticky-bottom"',
            PRODUCAO_HTML + '\n</div>\n</div>\n\n<div class="sticky-bottom"',
            1
        )

    # 4. Adiciona JS de producao (antes do render() final)
    if "function renderProducao" not in content:
        content = content.replace(
            "\nrender();",
            "\n" + PRODUCAO_JS + "\nrender();"
        )

    # 5. Chama renderProducao no final da funcao render()
    if "renderProducao(person)" not in content:
        content = content.replace(
            "document.getElementById('stickyBar').style.display = 'flex';",
            "document.getElementById('stickyBar').style.display = 'flex';\n  renderProducao(person);"
        )

    html_path.write_text(content, encoding="utf-8")


def git_commit_push(msg):
    git = shutil.which("git") or GIT_EXE
    try:
        subprocess.run([git, "add", "index.html"], check=True)
        subprocess.run([git, "commit", "-m", msg], check=True)
        subprocess.run([git, "push"], check=True)
        print("Commit e push OK!")
    except FileNotFoundError:
        print("AVISO: git nao encontrado")
    except subprocess.CalledProcessError as e:
        print(f"ERRO git: {e}")


def main():
    if not JSON_PATH.exists():
        print(f"ERRO: {JSON_PATH} nao encontrado. Rode mesclar_dados.py primeiro.")
        sys.exit(1)

    dados = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    print(f"Carregados: {len(dados)} pesquisadores")

    dados, removidos = limpar_dados(dados)
    if removidos:
        print(f"Duplicatas removidas: {removidos}")

    novo_db = "const DB = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";"
    atualizar_html(HTML_PATH, novo_db)

    total_artigos = sum(len(p.get("artigosCompletos", [])) for p in dados)
    total_orient  = sum(len(p.get("orientacoesconcluidas", [])) for p in dados)
    print(f"index.html atualizado: {total_artigos} artigos, {total_orient} orientacoes")

    git_commit_push(f"Adiciona secoes de producao: {total_artigos} artigos, {total_orient} orientacoes")


if __name__ == "__main__":
    main()
