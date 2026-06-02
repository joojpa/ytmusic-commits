# 🎵 YTMusic Commits

Automação que registra as **3 músicas mais ouvidas no dia anterior** via Last.fm e faz um commit no GitHub toda vez que você liga o PC.

---

## 📁 Estrutura

```
ytmusic-commits/
├── HISTÓRICO.md              ← top 3 diário, gerado automaticamente
├── STATS.md                  ← estatísticas mensais, gerado automaticamente
├── commit_music.sh           ← script principal (executado pelo systemd)
├── README.md
└── scripts/
    ├── fetch_music.py        ← busca o top 3 de ontem via Last.fm
    ├── stats.py              ← gera ranking, gráfico ASCII e streak
    └── fetch_music_hoje.py   ← versão de teste (busca músicas de hoje)
```

---

## ⚙️ Como funciona

1. Você ouve músicas no YouTube Music (PC ou celular)
2. O **Web Scrobbler** (navegador) e o **Pano Scrobbler** (Android) registram tudo no Last.fm com timestamp exato
3. Quando você liga o PC, o systemd aguarda 30 segundos e roda `commit_music.sh`
4. O script verifica se já rodou hoje — se sim, aborta para evitar commits duplicados
5. Consulta a API do Last.fm filtrando pelo dia anterior
6. As 3 músicas mais ouvidas são salvas no `HISTÓRICO.md`
7. O `STATS.md` é atualizado com ranking mensal, gráfico ASCII e streak
8. Um commit rico é feito e enviado ao GitHub:
```
🎵 Top 3 de 01/06/2026 | 70 scrobbles | Artista do dia: LVCAS
```

---

## 📋 Exemplo de HISTÓRICO.md

```markdown
# 🎵 Histórico de Músicas — YouTube Music

## 📅 01/06/2026
🥇 bico do corvo — LVCAS (12x)
🥈 Break of Dawn — Michael Jackson (10x)
🥉 mea culpa — LVCAS (6x)

## 📅 28/05/2026
🥇 Meu Jeitinho — LVCAS (11x)
🥈 mea culpa — LVCAS (3x)
🥉 Blind — Korn (2x)
```

---

## 📊 Exemplo de STATS.md

```markdown
# 📊 Estatísticas Musicais

## 🗓️ Junho/2026

- 🎵 Total de scrobbles: 88
- 📅 Dias ativos: 3
- 🔥 Streak atual: 2 dias
- 🏆 Maior streak do mês: 3 dias

## 🎤 Artistas mais ouvidos no mês

🥇 LVCAS — 24 scrobbles
🥈 Michael Jackson — 12 scrobbles
🥉 Metallica — 8 scrobbles

## 📈 Atividade por dia

`01/06` ██████████████████████████████ 70
`02/06` ████████ 18
```

---

## 🛠️ Dependências

- Python 3 (biblioteca padrão, sem instalações extras)
- Conta no [Last.fm](https://www.last.fm) com API key gratuita
- [Web Scrobbler](https://addons.mozilla.org/pt-BR/firefox/addon/web-scrobbler/) — scrobble no navegador (Firefox/Chrome)
- [Pano Scrobbler](https://play.google.com/store/apps/details?id=com.arn.scrobble) — scrobble no Android

---

## 🔍 Ver logs

```bash
tail -f ~/ytmusic-commits/commit_music.log
```

## 🧪 Testar sem esperar até amanhã

```bash
python ~/ytmusic-commits/scripts/fetch_music_hoje.py
```

---

## ⚠️ Observações

- `scripts/oauth.json`, `.last_run` e `.meta_commit.json` estão no `.gitignore` — não sobem ao GitHub
- Se o Last.fm não tiver scrobbles do dia anterior, nenhum commit é feito
- O script roda apenas uma vez por dia — se o PC for ligado várias vezes, só o primeiro boot commita
