#!/usr/bin/env python3
import sys
import urllib.request
import urllib.parse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

LASTFM_API_KEY = "3affae9bce83cc5fd8d062d2b61e772d"
LASTFM_USER    = "joojpa"
HISTORY_FILE   = Path(__file__).parent.parent / "HISTÓRICO.md"
TOP_N          = 3

def hoje():
    return datetime.now().date()

def timestamps_hoje():
    d = hoje()
    inicio = int(datetime(d.year, d.month, d.day, 0, 0, 0).timestamp())
    fim    = int(datetime(d.year, d.month, d.day, 23, 59, 59).timestamp())
    return inicio, fim

def buscar_scrobbles():
    inicio, fim = timestamps_hoje()
    musicas = []
    page = 1

    print(f"Buscando scrobbles de HOJE ({hoje()}) no Last.fm...")

    while True:
        params = urllib.parse.urlencode({
            "method": "user.getrecenttracks",
            "user": LASTFM_USER,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "from": inicio,
            "to": fim,
            "limit": 200,
            "page": page,
        })
        url = f"https://ws.audioscrobbler.com/2.0/?{params}"
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read())

        tracks = data.get("recenttracks", {}).get("track", [])
        if isinstance(tracks, dict):
            tracks = [tracks]
        if not tracks:
            break

        for t in tracks:
            if not isinstance(t, dict):
                continue
            date = t.get("date")
            if not isinstance(date, dict):
                continue
            titulo  = t.get("name", "Desconhecido")
            artista = t.get("artist", {})
            if isinstance(artista, dict):
                artista = artista.get("#text", "Desconhecido")
            else:
                artista = str(artista)
            musicas.append(f"{titulo} — {artista}")

        attr = data.get("recenttracks", {}).get("@attr", {})
        total_pages = int(attr.get("totalPages", 1))
        if page >= total_pages:
            break
        page += 1

    print(f"  → {len(musicas)} scrobbles encontrados.")
    return musicas

def top_n(musicas, n):
    return Counter(musicas).most_common(n)

def salvar(data_alvo, top):
    medals = ["🥇", "🥈", "🥉"]
    linhas = [f"\n## 📅 {data_alvo.strftime('%d/%m/%Y')} (TESTE — hoje)\n"]
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
    data_alvo = hoje()
    musicas   = buscar_scrobbles()

    if not musicas:
        print("Nenhum scrobble encontrado para hoje. O Web Scrobbler está ativo?")
        sys.exit(0)

    top = top_n(musicas, TOP_N)
    print(f"\nTop {TOP_N} de hoje:")
    for musica, contagem in top:
        print(f"  • {musica} ({contagem}x)")

    salvar(data_alvo, top)
    print("\nConcluído!")

if __name__ == "__main__":
    main()
