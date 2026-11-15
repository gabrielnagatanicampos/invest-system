#!/usr/bin/env bash
# Backup do Postgres em backups/invest_AAAAMMDD_HHMMSS.sql.gz
# Exemplo de cron (todo dia às 03:00, ajuste o caminho):
#   0 3 * * * /home/ubuntu/invest-system/scripts/backup.sh >> /home/ubuntu/backup.log 2>&1
# Apague backups antigos manualmente de vez em quando.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; . ./.env; set +a
mkdir -p backups
ARQ="backups/invest_$(date +%Y%m%d_%H%M%S).sql.gz"

docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$ARQ"
echo "Backup salvo em $ARQ"
