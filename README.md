# 🎵 YTMusic Commits

Automação que registra as **3 músicas mais ouvidas no dia anterior** via Last.fm e faz um commit no GitHub toda vez que você liga o PC.

---

## 📁 Estrutura

```
ytmusic-commits/
├── HISTÓRICO.md           ← gerado automaticamente a cada boot
├── commit_music.sh        ← script principal (executado pelo systemd)
├── README.md
└── scripts/
    ├── fetch_music.py     ← busca e filtra as músicas via Last.fm
    ├── fetch_music_hoje.py← versão de teste (busca músicas de hoje)
    └── oauth.json         ← credenciais do YouTube Music (não vai ao GitHub)
```

---

## ⚙️ Como funciona

1. Você ouve músicas no YouTube Music (PC ou celular)
2. O **Web Scrobbler** (navegador) e o **Pano Scrobbler** (Android) registram tudo no Last.fm com timestamp exato
3. Quando você liga o PC, o systemd aguarda 30 segundos e roda `commit_music.sh`
4. O script consulta a API do Last.fm filtrando pelo dia anterior
5. As 3 músicas mais ouvidas são salvas no `HISTÓRICO.md`
6. Um commit é feito com a data de ontem e enviado ao GitHub

---

## 📋 Exemplo de HISTÓRICO.md

```markdown
# 🎵 Histórico de Músicas — YouTube Music

## 📅 26/05/2026
🥇 The Emptiness Machine — Linkin Park (3x)
🥈 When They Come for Me — Linkin Park
🥉 Animal I Have Become — Three Days Grace

## 📅 25/05/2026
🥇 Prison Song — System of a Down (3x)
🥈 Black Rover — VK Blanka (3x)
🥉 Hail to the King — Avenged Sevenfold (3x)
```

---

## 🛠️ Dependências

- Python 3
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) — autenticação com YouTube Music
- Conta no [Last.fm](https://www.last.fm) com API key
- [Web Scrobbler](https://addons.mozilla.org/pt-BR/firefox/addon/web-scrobbler/) — scrobble no navegador
- [Pano Scrobbler](https://play.google.com/store/apps/details?id=com.arn.scrobble) — scrobble no Android

---

## 🔍 Ver logs

```bash
tail -f ~/ytmusic-commits/commit_music.log
```

---

## ⚠️ Observações

- O `scripts/oauth.json` contém cookies de autenticação — nunca sobe para o GitHub (está no `.gitignore`)
- Se o Last.fm não tiver scrobbles do dia anterior, nenhum commit é feito
- Para testar sem esperar até amanhã: `python scripts/fetch_music_hoje.py`
