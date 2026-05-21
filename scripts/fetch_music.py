#!/usr/bin/env python3
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

try:
    from ytmusicapi import YTMusic
except ImportError:
    print("Erro: ytmusicapi não instalado.")
    sys.exit(1)

SCRIPT_DIR   = Path(__file__).parent
REPO_DIR     = SCRIPT_DIR.parent
AUTH_FILE    = SCRIPT_DIR / "oauth.json"
HISTORY_FILE = REPO_DIR / "HISTÓRICO.md"
TOP_N        = 3

def carregar_ytmusic():
    if not AUTH_FILE.exists():
        print(f"Erro: {AUTH_FILE} não encontrado.")
        print("Execute primeiro: ytmusicapi browser --file scripts/oauth.json")
        sys.exit(1)
    return YTMusic(str(AUTH_FILE))

def ontem():
    return (datetime.now() - timedelta(days=1)).date()

def buscar_musicas(ytm):
    historico = ytm.get_history()
    musicas = []
    for item in historico:
        titulo = item.get("title", "Desconhecido")
        artista_raw = item.get("artists") or item.get("artist") or []
        if isinstance(artista_raw, list):
            artista = ", ".join(a.get("name", "") for a in artista_raw)
        else:
            artista = str(artista_raw)
        musicas.append({"titulo": titulo, "artista": artista})
    print(f"  → {len(musicas)} entradas encontradas.")
    return musicas

def top_n(musicas, n):
    chaves = [f"{m['titulo']} — {m['artista']}" for m in musicas]
    return Counter(chaves).most_common(n)

def salvar(data_alvo, top):
    medals = ["🥇", "🥈", "🥉"]
    linhas = [f"\n## 📅 {data_alvo.strftime('%d/%m/%Y')}\n"]
    for i, (musica, contagem) in enumerate(top):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        vezes = f"({contagem}x)" if contagem > 1 else ""
        linhas.append(f"{medal} {musica} {vezes}".strip())
    entrada = "\n".join(linhas) + "\n"

    cabecalho = "# 🎵 Histórico de Músicas — YouTube Music\n"
    conteudo = HISTORY_FILE.read_text(encoding="utf-8").replace(cabecalho, "").lstrip("\n") if HISTORY_FILE.exists() else ""
    HISTORY_FILE.write_text(cabecalho + entrada + conteudo, encoding="utf-8")
    print(f"  → {HISTORY_FILE} atualizado.")

def main():
    data_alvo = ontem()
    print(f"Buscando músicas de {data_alvo}...")
    ytm = carregar_ytmusic()
    musicas = buscar_musicas(ytm)
    if not musicas:
        print("Nenhuma música encontrada.")
        sys.exit(0)
    top = top_n(musicas, TOP_N)
    print(f"\nTop {TOP_N} de {data_alvo}:")
    for musica, contagem in top:
        print(f"  • {musica} ({contagem}x)")
    salvar(data_alvo, top)
    print("\nConcluído!")

if __name__ == "__main__":
    main()
