#!/usr/bin/env python3
import sys
import urllib.request
import urllib.parse
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

LASTFM_API_KEY = "3affae9bce83cc5fd8d062d2b61e772d"
LASTFM_USER    = "joojpa"
REPO_DIR       = Path(__file__).parent.parent
HISTORY_FILE   = REPO_DIR / "HISTÓRICO.md"
TOP_N          = 3

def ontem():
    return (datetime.now() - timedelta(days=1)).date()

def timestamp_dia(d):
    inicio = int(datetime(d.year, d.month, d.day, 0, 0, 0).timestamp())
    fim    = int(datetime(d.year, d.month, d.day, 23, 59, 59).timestamp())
    return inicio, fim

def buscar_scrobbles(data=None):
    if data is None:
        data = ontem()
    inicio, fim = timestamp_dia(data)
    musicas = []
    page = 1

    print(f"Buscando scrobbles de {data} no Last.fm...")

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
            data_json = json.loads(r.read())

        tracks = data_json.get("recenttracks", {}).get("track", [])
        if isinstance(tracks, dict):
            tracks = [tracks]
        if not tracks:
            break

        for t in tracks:
            if not isinstance(t, dict):
                continue
            if not isinstance(t.get("date"), dict):
                continue
            titulo  = t.get("name", "Desconhecido")
            artista = t.get("artist", {})
            album   = t.get("album", {})
            artista = artista.get("#text", "Desconhecido") if isinstance(artista, dict) else str(artista)
            album   = album.get("#text", "") if isinstance(album, dict) else ""
            musicas.append({"titulo": titulo, "artista": artista, "album": album})

        attr = data_json.get("recenttracks", {}).get("@attr", {})
        if page >= int(attr.get("totalPages", 1)):
            break
        page += 1

    print(f"  → {len(musicas)} scrobbles encontrados.")
    return musicas

def top_n(musicas, n):
    chaves = [f"{m['titulo']} — {m['artista']}" for m in musicas]
    return Counter(chaves).most_common(n)

def artista_do_dia(musicas):
    artistas = [m["artista"] for m in musicas]
    if not artistas:
        return "—"
    return Counter(artistas).most_common(1)[0][0]

def salvar(data_alvo, top, total_scrobbles, artista_dia):
    medals = ["🥇", "🥈", "🥉"]
    linhas = [f"## 📅 {data_alvo.strftime('%d/%m/%Y')}"]
    for i, (musica, contagem) in enumerate(top):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        vezes = f" ({contagem}x)" if contagem > 1 else ""
        linhas.append(f"{medal} {musica}{vezes}")
    entrada = "\n".join(linhas) + "\n"

    cabecalho = "# 🎵 Histórico de Músicas — YouTube Music\n"
    conteudo = HISTORY_FILE.read_text(encoding="utf-8").replace(cabecalho, "").lstrip("\n") if HISTORY_FILE.exists() else ""
    HISTORY_FILE.write_text(cabecalho + "\n" + entrada + "\n" + conteudo, encoding="utf-8")
    print(f"  → {HISTORY_FILE} atualizado.")

    # Salva metadados para o commit_music.sh usar
    meta = {
        "total_scrobbles": total_scrobbles,
        "artista_dia": artista_dia,
        "top3": [m for m, _ in top],
        "data": data_alvo.strftime('%d/%m/%Y'),
    }
    meta_file = REPO_DIR / ".meta_commit.json"
    meta_file.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

def main():
    data_alvo = ontem()
    musicas   = buscar_scrobbles(data_alvo)

    if not musicas:
        print("Nenhum scrobble encontrado para ontem.")
        sys.exit(0)

    top           = top_n(musicas, TOP_N)
    artista_dia   = artista_do_dia(musicas)
    total         = len(musicas)

    print(f"\nTop {TOP_N} de {data_alvo}:")
    for musica, contagem in top:
        print(f"  • {musica} ({contagem}x)")
    print(f"  🎤 Artista do dia: {artista_dia}")
    print(f"  🎵 Total: {total} scrobbles")

    salvar(data_alvo, top, total, artista_dia)
    print("\nConcluído!")

if __name__ == "__main__":
    main()
