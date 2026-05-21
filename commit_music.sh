#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$HOME/ytmusic-commits"
PYTHON="/usr/bin/python3"
LOG_FILE="${REPO_DIR}/commit_music.log"
ONTEM=$(date -d "yesterday" '+%d/%m/%Y')

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Iniciando — data alvo: $ONTEM"
cd "$REPO_DIR"

if ! "$PYTHON" scripts/fetch_music.py >> "$LOG_FILE" 2>&1; then
    log "ERRO: falha ao buscar músicas."
    exit 1
fi

if git diff --quiet -- "HISTÓRICO.md" 2>/dev/null; then
    log "Sem alterações — nada a commitar."
    exit 0
fi

git add HISTÓRICO.md
git commit --date="yesterday 09:00" -m "🎵 Top 3 músicas de $ONTEM"
log "Commit criado."

if git push origin main >> "$LOG_FILE" 2>&1; then
    log "✅ Push realizado com sucesso!"
else
    log "⚠️  Push falhou. Verifique as credenciais do GitHub."
    exit 1
fi
