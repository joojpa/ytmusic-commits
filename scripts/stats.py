#!/usr/bin/env python3
"""
Gera STATS.md com:
- Ranking mensal de artistas
- Gráfico de barras ASCII dos dias mais ativos
- Streak de dias consecutivos ouvindo música
"""
import urllib.request
import urllib.parse
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

LASTFM_API_KEY = "3affae9bce83cc5fd8d062d2b61e772d"
LASTFM_USER    = "joojpa"
REPO_DIR       = Path(__file__).parent.parent
STATS_FILE     = REPO_DIR / "STATS.md"

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def buscar_mes_atual():
    hoje       = datetime.now().date()
    inicio_mes = hoje.replace(day=1)
    inicio     = int(datetime(inicio_mes.year, inicio_mes.month, inicio_mes.day, 0, 0, 0).timestamp())
    fim        = int(datetime(hoje.year, hoje.month, hoje.day, 23, 59, 59).timestamp())

    print(f"Buscando scrobbles de {inicio_mes} até {hoje}...")
    musicas = []
    page = 1

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
            date_field = t.get("date")
            if not isinstance(date_field, dict):
                continue
            artista = t.get("artist", {})
            artista = artista.get("#text", "?") if isinstance(artista, dict) else str(artista)
            uts = int(date_field.get("uts", 0))
            dia = datetime.fromtimestamp(uts).date()
            musicas.append({"artista": artista, "dia": dia})

        attr = data.get("recenttracks", {}).get("@attr", {})
        if page >= int(attr.get("totalPages", 1)):
            break
        page += 1

    print(f"  → {len(musicas)} scrobbles no mês.")
    return musicas

def ranking_artistas(musicas, top_n=10):
    return Counter(m["artista"] for m in musicas).most_common(top_n)

def scrobbles_por_dia(musicas):
    contagem = defaultdict(int)
    for m in musicas:
        contagem[m["dia"]] += 1
    return dict(sorted(contagem.items()))

def grafico_ascii(por_dia, largura=30):
    if not por_dia:
        return "_sem dados_"
    max_val = max(por_dia.values())
    linhas = []
    for dia, qtd in sorted(por_dia.items()):
        barra = int((qtd / max_val) * largura)
        linhas.append(f"`{dia.strftime('%d/%m')}` {'█' * barra} {qtd}")
    return "\n".join(linhas)

def calcular_streak(por_dia):
    if not por_dia:
        return 0, 0
    hoje = datetime.now().date()
    dias_com_musica = set(por_dia.keys())

    streak_atual = 0
    d = hoje - timedelta(days=1)
    while d in dias_com_musica:
        streak_atual += 1
        d -= timedelta(days=1)

    dias_ordenados = sorted(dias_com_musica)
    streak_max = 1
    atual = 1
    for i in range(1, len(dias_ordenados)):
        if (dias_ordenados[i] - dias_ordenados[i-1]).days == 1:
            atual += 1
            streak_max = max(streak_max, atual)
        else:
            atual = 1

    return streak_atual, streak_max

def scrobble_str(n):
    return "1 scrobble" if n == 1 else f"{n} scrobbles"

def gerar_stats():
    musicas  = buscar_mes_atual()
    hoje     = datetime.now()
    mes_nome = f"{MESES[hoje.month]}/{hoje.year}"

    ranking      = ranking_artistas(musicas)
    por_dia      = scrobbles_por_dia(musicas)
    streak_atual, streak_max = calcular_streak(por_dia)
    total_mes    = len(musicas)
    dias_ativos  = len(por_dia)

    linhas = [
        "# 📊 Estatísticas Musicais\n",
        f"> Atualizado em {hoje.strftime('%d/%m/%Y às %H:%M')}\n",
        "---\n",
        f"## 🗓️ {mes_nome}\n",
        f"- 🎵 Total de scrobbles: **{total_mes}**",
        f"- 📅 Dias ativos: **{dias_ativos}**",
        f"- 🔥 Streak atual: **{streak_atual} {'dia' if streak_atual == 1 else 'dias'}**",
        f"- 🏆 Maior streak do mês: **{streak_max} {'dia' if streak_max == 1 else 'dias'}**\n",
        "---\n",
        "## 🎤 Artistas mais ouvidos no mês\n",
    ]

    medals = ["🥇", "🥈", "🥉"]
    for i, (artista, qtd) in enumerate(ranking):
        medal = medals[i] if i < 3 else f"{i+1}."
        linhas.append(f"{medal} **{artista}** — {scrobble_str(qtd)}")

    linhas += [
        "\n---\n",
        "## 📈 Atividade por dia\n",
        "```",
        grafico_ascii(por_dia),
        "```\n",
    ]

    STATS_FILE.write_text("\n".join(linhas), encoding="utf-8")
    print(f"  → {STATS_FILE} atualizado.")

if __name__ == "__main__":
    gerar_stats()
    print("Stats geradas com sucesso!")
