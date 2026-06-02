#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$HOME/ytmusic-commits"
PYTHON="/usr/bin/python3"
LOG_FILE="${REPO_DIR}/commit_music.log"
META_FILE="${REPO_DIR}/.meta_commit.json"
LOCK_FILE="${REPO_DIR}/.last_run"
ONTEM=$(date -d "yesterday" '+%d/%m/%Y')
HOJE=$(date '+%Y-%m-%d')

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

log "Iniciando — data alvo: $ONTEM"
cd "$REPO_DIR"

# Verifica se já rodou hoje
if [ -f "$LOCK_FILE" ] && [ "$(cat "$LOCK_FILE")" = "$HOJE" ]; then
    log "Já rodou hoje ($HOJE) — abortando para evitar commit duplicado."
    exit 0
fi

# Busca músicas de ontem
if ! "$PYTHON" scripts/fetch_music.py >> "$LOG_FILE" 2>&1; then
    log "ERRO: falha ao buscar músicas."
    exit 1
fi

# Gera estatísticas do mês
"$PYTHON" scripts/stats.py >> "$LOG_FILE" 2>&1 || log "⚠️  Stats falharam, continuando..."

# Verifica se há mudanças
if git diff --quiet -- "HISTÓRICO.md" "STATS.md" 2>/dev/null; then
    log "Sem alterações — nada a commitar."
    # Salva o lock mesmo sem commit para não tentar de novo
    echo "$HOJE" > "$LOCK_FILE"
    exit 0
fi

# Monta mensagem de commit rica
if [ -f "$META_FILE" ]; then
    TOTAL=$("$PYTHON" -c "import json; d=json.load(open('$META_FILE')); print(d['total_scrobbles'])")
    ARTISTA=$("$PYTHON" -c "import json; d=json.load(open('$META_FILE')); print(d['artista_dia'])")
    SCROBBLE_LABEL=$([ "$TOTAL" = "1" ] && echo "scrobble" || echo "scrobbles")
    COMMIT_MSG="🎵 Top 3 de $ONTEM | $TOTAL $SCROBBLE_LABEL | Artista do dia: $ARTISTA"
else
    COMMIT_MSG="🎵 Top 3 músicas de $ONTEM"
fi

git add HISTÓRICO.md STATS.md
git commit --date="yesterday 09:00" -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
log "Commit criado: $COMMIT_MSG"

# Pull + push
if git pull origin main --no-edit >> "$LOG_FILE" 2>&1 && git push origin main >> "$LOG_FILE" 2>&1; then
    log "✅ Push realizado com sucesso!"
    echo "$HOJE" > "$LOCK_FILE"
else
    log "⚠️  Push falhou."
    exit 1
fi
